# ============================================================================
# S3 BUCKETS
# ============================================================================

# Frontend hosting bucket
resource "aws_s3_bucket" "frontend" {
  bucket_prefix = "${var.project_name}-frontend-"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.frontend]
}

# Data bucket for discogs.csv
resource "aws_s3_bucket" "data" {
  bucket_prefix = "${var.project_name}-data-"
}

resource "aws_s3_object" "discogs_csv" {
  bucket = aws_s3_bucket.data.id
  key    = "discogs.csv"
  source = "${path.module}/../../data/discogs.csv"
  etag   = filemd5("${path.module}/../../data/discogs.csv")
}

# ============================================================================
# LAMBDA FUNCTION (FastMCP + Bedrock)
# Just ONE Lambda! FastMCP embedded, no separate action group Lambda needed
# ============================================================================

resource "aws_lambda_function" "chat" {
  filename         = "${path.module}/../../lambda/lambda.zip"
  function_name    = "${var.project_name}-chat"
  role             = aws_iam_role.chat_lambda.arn
  handler          = "handler.lambda_handler"
  source_code_hash = fileexists("${path.module}/../../lambda/lambda.zip") ? filebase64sha256("${path.module}/../../lambda/lambda.zip") : null
  runtime          = var.lambda_runtime
  architecture     = var.lambda_architecture
  timeout          = 60
  memory_size      = 512

  environment {
    variables = {
      PROJECT_TAG      = var.project_name
      DATA_BUCKET      = aws_s3_bucket.data.id
      DATA_KEY         = "discogs.csv"
      BEDROCK_MODEL_ID = var.bedrock_model_id
      FRONTEND_ORIGIN  = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
    }
  }

  tags = {
    Name = "${var.project_name}-chat-lambda"
  }
  
  lifecycle {
    ignore_changes = [source_code_hash]
  }
}

resource "aws_cloudwatch_log_group" "chat_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.chat.function_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-chat-lambda-logs"
  }
}

resource "aws_iam_role" "chat_lambda" {
  name = "${var.project_name}-chat-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-chat-lambda-role"
  }
}

resource "aws_iam_role_policy_attachment" "chat_lambda_basic" {
  role       = aws_iam_role.chat_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "chat_lambda_policy" {
  name = "${var.project_name}-chat-lambda-policy"
  role = aws_iam_role.chat_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.data.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/*"
      }
    ]
  })
}

# ============================================================================
# API GATEWAY HTTP API (No Auth - Public Demo!)
# ============================================================================

resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]  # Public API for demos!
    allow_methods = ["POST", "OPTIONS", "GET"]
    allow_headers = ["content-type"]
    max_age       = 300
  }

  tags = {
    Name = "${var.project_name}-api"
  }
}

resource "aws_apigatewayv2_integration" "chat" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.chat.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "chat" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /chat"
  target    = "integrations/${aws_apigatewayv2_integration.chat.id}"
  # No authorization! Public for demos
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Name = "${var.project_name}-api-stage"
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chat.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
