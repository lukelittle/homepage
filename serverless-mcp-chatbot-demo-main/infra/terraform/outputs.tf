output "frontend_website_url" {
  description = "S3 website URL for the frontend"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "frontend_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "api_chat_url" {
  description = "Full chat endpoint URL"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/chat"
}

output "data_bucket_name" {
  description = "S3 bucket name for data"
  value       = aws_s3_bucket.data.id
}

output "deployment_region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}

output "next_steps" {
  description = "Next steps after terraform apply"
  value       = <<-EOT
    
    ✅ Infrastructure deployed successfully!
    
    Next steps:
    
    1. Build Lambda: cd ../../lambda && ./build.sh
    
    2. Re-apply Terraform: terraform apply
       (to deploy the new Lambda code)
    
    3. Update frontend: Edit ../../frontend/index.html
       Change API_URL to: ${aws_apigatewayv2_api.main.api_endpoint}/chat
    
    4. Upload frontend: 
       aws s3 cp ../../frontend/index.html s3://${aws_s3_bucket.frontend.id}/
    
    5. Visit: http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}
    
    That's it! FastMCP + Bedrock is fully configured. No console steps! 🚀
    
    📚 Read FRAMEWORK_GUIDE.md to learn about FastMCP vs. other approaches
  EOT
}
