# ========================================
# Terraform Backend Configuration
# ========================================
#
# Backend configuration cannot use variables.
# To use remote state, create a backend config file:
#
# Create backend.hcl with:
#   bucket         = "<your-account-id>-us-east-1-tf-state"
#   key            = "homepage/terraform.tfstate"
#   region         = "us-east-1"
#   dynamodb_table = "tf-lock"
#   encrypt        = true
#
# Then run: terraform init -backend-config=backend.hcl
#
# Or use the default local backend by leaving this commented.
# ========================================

# terraform {
#   backend "s3" {
#     bucket         = "<your-account-id>-us-east-1-tf-state"
#     key            = "homepage/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "tf-lock"
#     encrypt        = true
#   }
# }
