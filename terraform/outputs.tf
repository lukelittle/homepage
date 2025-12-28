# ========================================
# Outputs
# ========================================

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.website.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.website.arn
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.website.id
}

output "cloudfront_distribution_domain" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.website.domain_name
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.website.arn
}

output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = aws_acm_certificate.website.arn
}

output "acm_certificate_validation_records" {
  description = "DNS validation records for ACM certificate - ADD THESE TO ROUTE 53"
  value = {
    for dvo in aws_acm_certificate.website.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      value  = dvo.resource_record_value
    }
  }
}

output "github_actions_role_arn" {
  description = "ARN of the IAM role for GitHub Actions - ADD THIS TO GITHUB SECRETS"
  value       = aws_iam_role.github_actions.arn
}

output "route53_dns_instructions" {
  description = "Instructions for Route 53 DNS setup"
  value = <<-EOT
    
    ====================================
    NEXT STEPS: Route 53 Configuration
    ====================================
    
    1. ADD ACM CERTIFICATE VALIDATION RECORDS:
       Go to Route 53 → Hosted Zone for lukelittle.com
       Create CNAME records from 'acm_certificate_validation_records' output above
       
    2. WAIT FOR CERTIFICATE VALIDATION:
       Check ACM console until status shows "Issued" (usually 5-30 minutes)
       
    3. ADD A RECORDS FOR YOUR DOMAIN:
       Create two A records in Route 53:
       
       Record 1:
         Name: (blank for apex domain)
         Type: A
         Alias: Yes
         Alias Target: ${aws_cloudfront_distribution.website.domain_name}
         
       Record 2:
         Name: www
         Type: A
         Alias: Yes
         Alias Target: ${aws_cloudfront_distribution.website.domain_name}
    
    4. DEPLOY YOUR SITE:
       Run: ./scripts/deploy.sh
       
    CloudFront Distribution Domain: ${aws_cloudfront_distribution.website.domain_name}
    CloudFront Distribution ID: ${aws_cloudfront_distribution.website.id}
    S3 Bucket: ${aws_s3_bucket.website.id}
    
  EOT
}
