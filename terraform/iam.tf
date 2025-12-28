# ========================================
# GitHub OIDC Provider for GitHub Actions
# ========================================

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
  ]

  tags = {
    Name    = "github-actions-oidc"
    Project = "homepage"
  }
}

# ========================================
# IAM Role for GitHub Actions
# ========================================

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    actions = ["sts:AssumeRoleWithWebIdentity"]

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:lukelittle/homepage:*"]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "github-actions-homepage-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json

  tags = {
    Name = "github-actions-homepage-deploy"
  }
}

# ========================================
# IAM Policy for S3 Deployment
# ========================================

data "aws_iam_policy_document" "github_actions_s3" {
  statement {
    sid    = "S3BucketAccess"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.website.arn,
    ]
  }

  statement {
    sid    = "S3ObjectAccess"
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
      "s3:PutObjectAcl",
    ]

    resources = [
      "${aws_s3_bucket.website.arn}/*",
    ]
  }
}

resource "aws_iam_policy" "github_actions_s3" {
  name        = "github-actions-homepage-s3-access"
  description = "Allows GitHub Actions to deploy to S3 bucket"
  policy      = data.aws_iam_policy_document.github_actions_s3.json
}

resource "aws_iam_role_policy_attachment" "github_actions_s3" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions_s3.arn
}

# ========================================
# IAM Policy for CloudFront Invalidation
# ========================================

data "aws_iam_policy_document" "github_actions_cloudfront" {
  statement {
    sid    = "CloudFrontInvalidation"
    effect = "Allow"

    actions = [
      "cloudfront:CreateInvalidation",
      "cloudfront:GetInvalidation",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "github_actions_cloudfront" {
  name        = "github-actions-homepage-cloudfront-access"
  description = "Allows GitHub Actions to invalidate CloudFront cache"
  policy      = data.aws_iam_policy_document.github_actions_cloudfront.json
}

resource "aws_iam_role_policy_attachment" "github_actions_cloudfront" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions_cloudfront.arn
}
