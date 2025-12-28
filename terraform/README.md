# Terraform Infrastructure for Homepage

This directory contains Terraform configuration for deploying the Hugo blog to AWS.

## Architecture

```
GitHub Actions → AWS (OIDC) → S3 + CloudFront + ACM Certificate
```

## Resources Created

- **S3 Bucket**: Private bucket for static files
- **CloudFront Distribution**: Global CDN with HTTPS
- **ACM Certificate**: Free SSL certificate (lukelittle.com + www)
- **Origin Access Control (OAC)**: Secure CloudFront → S3 access
- **IAM Role + OIDC Provider**: GitHub Actions authentication
- **IAM Policies**: S3 upload and CloudFront invalidation permissions

## Cost Estimate

For a personal blog with <10,000 visitors/month:
- S3: ~$0.10/month
- CloudFront: $0.00 (free tier)
- ACM Certificate: $0.00 (always free)

**Total: ~$0.25/month or ~$3/year**

## Quick Start

### Initial Setup

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

After applying, get the GitHub Actions role ARN:

```bash
terraform output github_actions_role_arn
terraform output cloudfront_distribution_id
terraform output s3_bucket_name
```

Add these as GitHub secrets (see [GITHUB_ACTIONS_SETUP.md](../GITHUB_ACTIONS_SETUP.md)).

### Daily Use

**You don't need to run Terraform manually!** 

Deployments are automated via GitHub Actions - just push to main:

```bash
git add .
git commit -m "New blog post"
git push origin main
```

GitHub Actions will automatically:
1. Build the Hugo site
2. Upload to S3
3. Invalidate CloudFront cache

## Manual Deployment (Fallback)

If GitHub Actions is down, you can deploy manually:

```bash
cd ..
./scripts/deploy.sh
```

## Configuration

Edit `variables.tf` to customize:

- `domain_name`: Primary domain (default: lukelittle.com)
- `alternative_domain_names`: Additional domains (default: www.lukelittle.com)
- `aws_region`: AWS region (default: us-east-1)
- `cloudfront_price_class`: CDN coverage (default: PriceClass_100)
- `enable_versioning`: S3 versioning (default: true)

## Remote State

State is stored remotely in S3:
- **Bucket**: `168737286209-us-east-1-tf-state`
- **Key**: `homepage/terraform.tfstate`
- **DynamoDB Lock**: `tf-lock`

This allows safe concurrent access and state history.

## Files

```
terraform/
├── backend.tf          # Remote state configuration
├── versions.tf         # Provider configuration & default tags
├── variables.tf        # Input variables
├── main.tf            # S3, CloudFront, ACM resources
├── iam.tf             # GitHub Actions OIDC + IAM role
├── outputs.tf         # Output values for GitHub secrets
└── README.md          # This file
```

## Common Commands

```bash
# View outputs
terraform output

# View specific output
terraform output github_actions_role_arn

# View current state
terraform show

# Update infrastructure
terraform plan
terraform apply

# Destroy (⚠️ dangerous!)
terraform destroy
```

## Security Features

- ✅ S3 bucket is private (not publicly accessible)
- ✅ CloudFront uses Origin Access Control (OAC)
- ✅ HTTPS enforced via ACM certificate
- ✅ GitHub Actions uses OIDC (no access keys!)
- ✅ TLS 1.2+ required
- ✅ All resources tagged with Project="homepage"

## Troubleshooting

### Certificate Issues
- Ensure ACM certificate is validated (check ACM console in us-east-1)
- DNS validation records must be in Route 53

### Deployment Failures
- Check GitHub Actions logs
- Verify GitHub secrets are set correctly
- Ensure CloudFront distribution is deployed (not just in progress)

### State Lock
If Terraform is locked:
```bash
terraform force-unlock <LOCK_ID>
```

## Documentation

- **GitHub Actions Setup**: See [GITHUB_ACTIONS_SETUP.md](../GITHUB_ACTIONS_SETUP.md)
- **Manual Deployment**: Use `./scripts/deploy.sh`
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/
