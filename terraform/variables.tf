variable "aws_region" {
  description = "AWS region for resources (S3 bucket)"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Primary domain name for the website"
  type        = string
  default     = "lukelittle.com"
}

variable "alternative_domain_names" {
  description = "Alternative domain names (e.g., www subdomain)"
  type        = list(string)
  default     = ["www.lukelittle.com"]
}

variable "cloudfront_price_class" {
  description = "CloudFront price class (PriceClass_All, PriceClass_200, PriceClass_100)"
  type        = string
  default     = "PriceClass_100" # US, Canada, Europe - cheapest option
}

variable "enable_versioning" {
  description = "Enable versioning on S3 bucket"
  type        = bool
  default     = true
}
