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
# The state for lukelittle.com already lives in S3, so the backend must stay
# enabled; without it, Terraform would think no infrastructure exists.
# ========================================

terraform {
  backend "s3" {}
}
