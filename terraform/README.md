# Terraform AWS Deployment for Hugo Blog

This Terraform configuration deploys your Hugo blog to AWS using S3, CloudFront, and ACM.

## Architecture

```
User → Route 53 (DNS) → CloudFront (CDN + SSL) → S3 Bucket (Static Files)
```

## Infrastructure Components

- **S3 Bucket**: Private bucket storing static website files
- **CloudFront Distribution**: Global CDN with HTTPS
- **ACM Certificate**: Free SSL certificate for your domain
- **Origin Access Control (OAC)**: Secure S3 access from CloudFront

## Cost Estimate

For a personal blog with <10,000 visitors/month:
- S3 Storage: ~$0.10/month
- S3 Requests: ~$0.05/month
- CloudFront: $0.00 (free tier covers most personal blogs)
- ACM Certificate: $0.00 (always free)

**Total: ~$0.25-$0.50/month** or **~$6/year**

## Prerequisites

1. **AWS Account** (ID: 168737286209)
2. **AWS CLI** configured with credentials
3. **Terraform** installed (>= 1.0)
4. **Domain** registered (lukelittle.com)
5. **Route 53** hosted zone (managed separately)

## Quick Start

### Step 1: Initialize Terraform

```bash
cd terraform
terraform init
```

This will:
- Download AWS provider
- Configure remote state backend in S3

### Step 2: Review the Plan

```bash
terraform plan
```

This will show you what infrastructure will be created.

### Step 3: Apply Configuration

```bash
terraform apply
```

Type `yes` to confirm. This creates:
- S3 bucket: `lukelittle.com`
- CloudFront distribution
- ACM certificate (pending validation)

**Note**: This takes ~5-10 minutes as CloudFront distribution is created.

### Step 4: Validate ACM Certificate

After `terraform apply`, you'll see output like:

```
acm_certificate_validation_records = {
  "lukelittle.com" = {
    name  = "_abc123.lukelittle.com"
    type  = "CNAME"
    value = "_def456.acm-validations.aws"
  }
  ...
}
```

**Action Required:**
1. Go to Route 53 → Hosted Zone for `lukelittle.com`
2. Create CNAME records from the output above
3. Wait 5-30 minutes for validation
4. Check ACM console to confirm status is "Issued"

### Step 5: Configure DNS

After certificate is validated, add A records in Route 53:

**Record 1 (apex domain):**
- Name: (blank)
- Type: A
- Alias: Yes
- Alias Target: `<cloudfront_domain>` (from Terraform output)

**Record 2 (www subdomain):**
- Name: www
- Type: A
- Alias: Yes
- Alias Target: `<cloudfront_domain>` (from Terraform output)

### Step 6: Deploy Your Site

```bash
cd ..
./scripts/deploy.sh
```

This will:
1. Build Hugo site (`hugo --minify`)
2. Upload to S3
3. Invalidate CloudFront cache

Your site will be live at `https://lukelittle.com` 🚀

## Daily Workflow

When you write a new blog post:

```bash
# 1. Create your post
hugo new posts/my-new-post/index.md

# 2. Edit and preview locally
hugo server -D

# 3. When ready, deploy
./scripts/deploy.sh
```

That's it! The script handles building, uploading, and cache invalidation.

## Terraform Commands

### View Current State

```bash
terraform show
```

### See Outputs Again

```bash
terraform output
```

### View Specific Output

```bash
terraform output cloudfront_distribution_id
terraform output acm_certificate_validation_records
```

### Update Infrastructure

After modifying `.tf` files:

```bash
terraform plan   # Review changes
terraform apply  # Apply changes
```

### Destroy Everything

⚠️ **Warning**: This deletes all infrastructure!

```bash
terraform destroy
```

## Configuration Variables

Edit these in `variables.tf` if needed:

- `domain_name`: Primary domain (default: lukelittle.com)
- `alternative_domain_names`: Additional domains (default: www.lukelittle.com)
- `aws_region`: AWS region (default: us-east-1)
- `cloudfront_price_class`: CDN coverage (default: PriceClass_100 - cheapest)
- `enable_versioning`: S3 versioning (default: true)

## Remote State Backend

State is stored in:
- **S3 Bucket**: `168737286209-us-east-1-tf-state`
- **Key**: `homepage/terraform.tfstate`
- **DynamoDB Lock Table**: `terraform-state-lock`

This allows:
- Safe state storage
- Prevents concurrent modifications
- State history/rollback via S3 versioning

## Troubleshooting

### Certificate Not Validating

- Check CNAME records in Route 53 are correct
- Wait 30 minutes (validation can be slow)
- Verify in ACM Console (us-east-1 region)

### 403 Forbidden Errors

- Ensure S3 bucket policy is applied
- Check CloudFront distribution status is "Deployed"
- Wait 10-15 minutes after terraform apply

### Site Not Updating

- Make sure you ran `./scripts/deploy.sh`
- CloudFront invalidation takes 5-10 minutes
- Check invalidation status in CloudFront console

### DNS Not Resolving

- Verify A records in Route 53
- DNS propagation can take 24-48 hours
- Test with: `dig lukelittle.com` or `nslookup lukelittle.com`

### Terraform State Locked

If another operation is running or was interrupted:

```bash
# View lock info
terraform force-unlock <LOCK_ID>
```

## Security Features

- ✅ S3 bucket is private (not publicly accessible)
- ✅ CloudFront uses Origin Access Control (OAC)
- ✅ HTTPS enforced (HTTP redirects to HTTPS)
- ✅ TLS 1.2+ required
- ✅ All public access blocked on S3

## Monitoring Costs

```bash
# Check S3 storage
aws s3 ls s3://lukelittle.com --recursive --summarize --human-readable

# View CloudFront metrics
aws cloudfront get-distribution --id <DISTRIBUTION_ID>

# Check billing
# AWS Console → Billing Dashboard → Cost Explorer
```

## Backup & Recovery

- **S3 Versioning**: Enabled by default
- **Terraform State**: Versioned in S3
- **Rollback**: Restore previous version from S3 console

## Next Steps After Deployment

1. Set up AWS Budget alerts ($5/month threshold)
2. Monitor CloudWatch for traffic patterns
3. Consider adding WAF for security (if needed)
4. Optimize images for faster loading
5. Set up CloudWatch alarms for high costs

## Support

- AWS Documentation: https://docs.aws.amazon.com/
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Hugo Documentation: https://gohugo.io/documentation/

## Clean Architecture

```
terraform/
├── backend.tf       # Remote state configuration
├── versions.tf      # Provider versions
├── variables.tf     # Input variables
├── main.tf          # Main resources (S3, CloudFront, ACM)
├── outputs.tf       # Output values
├── .gitignore       # Ignore state files
└── README.md        # This file
```

State is centralized in S3, infrastructure is version-controlled, and deployments are repeatable.
