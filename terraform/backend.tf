terraform {
  backend "s3" {
    bucket         = "168737286209-us-east-1-tf-state"
    key            = "homepage/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-lock"
    encrypt        = true
    profile        = "AdministratorAccess"
  }
}
