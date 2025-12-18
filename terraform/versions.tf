terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "AdministratorAccess-168737286209"

  default_tags {
    tags = {
      Project     = "homepage"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

# ACM certificates for CloudFront must be in us-east-1
provider "aws" {
  alias   = "us_east_1"
  region  = "us-east-1"
  profile = "AdministratorAccess-168737286209"

  default_tags {
    tags = {
      Project     = "homepage"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}
