# ========================================
# S3 Bucket for Static Website Hosting
# ========================================

locals {
  account_id  = "168737286209"
  bucket_name = "${local.account_id}-${var.aws_region}-homepage"
}

resource "aws_s3_bucket" "website" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_versioning" "website" {
  bucket = aws_s3_bucket.website.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ========================================
# CloudFront Origin Access Control (OAC)
# ========================================

resource "aws_cloudfront_origin_access_control" "website" {
  name                              = "${var.domain_name}-oac"
  description                       = "OAC for ${var.domain_name}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# ========================================
# CloudFront Function for URL Rewriting
# ========================================

resource "aws_cloudfront_function" "url_rewrite" {
  name    = "append-index-html"
  runtime = "cloudfront-js-1.0"
  comment = "Append index.html to directory requests and redirect www to apex"
  publish = true
  code    = <<-EOT
function handler(event) {
    var request = event.request;
    var host = request.headers.host.value;
    
    // Redirect www to apex domain
    if (host === 'www.lukelittle.com') {
        return {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: {
                'location': { value: 'https://lukelittle.com' + request.uri }
            }
        };
    }
    
    var uri = request.uri;
    
    // Check if the URI is missing a file name (ends with /)
    if (uri.endsWith('/')) {
        request.uri += 'index.html';
    }
    // Check if the URI is missing a file extension
    else if (!uri.includes('.')) {
        request.uri += '/index.html';
    }
    
    return request;
}
EOT
}

# ========================================
# ACM Certificate (us-east-1 for CloudFront)
# ========================================

resource "aws_acm_certificate" "website" {
  provider          = aws.us_east_1
  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = var.alternative_domain_names

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = var.domain_name
  }
}

# ========================================
# CloudFront Distribution
# ========================================

resource "aws_cloudfront_distribution" "website" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront distribution for ${var.domain_name}"
  default_root_object = "index.html"
  price_class         = var.cloudfront_price_class
  aliases             = concat([var.domain_name], var.alternative_domain_names)

  origin {
    domain_name              = aws_s3_bucket.website.bucket_regional_domain_name
    origin_id                = "S3-${var.domain_name}"
    origin_access_control_id = aws_cloudfront_origin_access_control.website.id
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${var.domain_name}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600   # 1 hour
    max_ttl                = 86400  # 24 hours
    compress               = true

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.url_rewrite.arn
    }
  }

  # Custom error response for SPA-style routing
  custom_error_response {
    error_code         = 404
    response_code      = 404
    response_page_path = "/404.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.website.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  tags = {
    Name = var.domain_name
  }
}

# ========================================
# S3 Bucket Policy for CloudFront OAC
# ========================================

data "aws_iam_policy_document" "website_bucket_policy" {
  statement {
    sid    = "AllowCloudFrontServicePrincipal"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.website.arn}/*"
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.website.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "website" {
  bucket = aws_s3_bucket.website.id
  policy = data.aws_iam_policy_document.website_bucket_policy.json
}
