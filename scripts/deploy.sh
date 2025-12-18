#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
BUCKET_NAME="168737286209-us-east-1-homepage"
DISTRIBUTION_ID=""  # Will be fetched from Terraform output

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Hugo Blog Deployment Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Check if Hugo is installed
if ! command -v hugo &> /dev/null; then
    echo -e "${RED}Error: Hugo is not installed${NC}"
    echo "Install Hugo: brew install hugo"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install AWS CLI: brew install awscli"
    exit 1
fi

# Get CloudFront distribution ID from Terraform output
echo -e "${GREEN}➜${NC} Fetching CloudFront distribution ID..."
cd "$PROJECT_ROOT/terraform"
DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id 2>/dev/null || echo "")

if [ -z "$DISTRIBUTION_ID" ]; then
    echo -e "${RED}Error: Could not get CloudFront distribution ID from Terraform${NC}"
    echo "Make sure you have run 'terraform apply' first"
    exit 1
fi

echo -e "${GREEN}✓${NC} CloudFront Distribution: $DISTRIBUTION_ID"
echo ""

# Build Hugo site
echo -e "${GREEN}➜${NC} Building Hugo site..."
cd "$PROJECT_ROOT"
hugo --minify

if [ ! -d "public" ]; then
    echo -e "${RED}Error: Hugo build failed - public/ directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Hugo build complete"
echo ""

# Sync to S3
echo -e "${GREEN}➜${NC} Uploading to S3 bucket: s3://$BUCKET_NAME/"
aws s3 sync public/ s3://$BUCKET_NAME/ \
    --delete \
    --cache-control "public, max-age=3600" \
    --exclude "*.html" \
    --exclude "*.xml"

# Upload HTML files with shorter cache (for content updates)
aws s3 sync public/ s3://$BUCKET_NAME/ \
    --exclude "*" \
    --include "*.html" \
    --include "*.xml" \
    --cache-control "public, max-age=300" \
    --content-type "text/html; charset=utf-8"

echo -e "${GREEN}✓${NC} Upload complete"
echo ""

# Invalidate CloudFront cache
echo -e "${GREEN}➜${NC} Invalidating CloudFront cache..."
INVALIDATION_OUTPUT=$(aws cloudfront create-invalidation \
    --distribution-id "$DISTRIBUTION_ID" \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

echo -e "${GREEN}✓${NC} Invalidation created: $INVALIDATION_OUTPUT"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete! 🚀${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your site is now live at:"
echo -e "${YELLOW}https://lukelittle.com${NC}"
echo ""
echo "Note: CloudFront invalidation may take 5-10 minutes to propagate globally"
