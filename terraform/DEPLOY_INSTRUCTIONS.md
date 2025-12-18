# Two-Stage Terraform Deployment

Due to ACM certificate validation requirements, we need to deploy in two stages.

## Stage 1: Create ACM Certificate

```bash
cd terraform

# Deploy only the ACM certificate
terraform apply -target=aws_acm_certificate.website
```

This will create the ACM certificate and show you the DNS validation records.

### View the validation records:

```bash
terraform output acm_certificate_validation_records
```

You'll see output like:
```
{
  "lukelittle.com" = {
    name  = "_abc123.lukelittle.com"
    type  = "CNAME"
    value = "_def456.acm-validations.aws."
  }
  "www.lukelittle.com" = {
    name  = "_xyz789.www.lukelittle.com"
    type  = "CNAME"
    value = "_uvw012.acm-validations.aws."
  }
}
```

### Add these CNAME records to Route 53:

1. Go to Route 53 console
2. Open your hosted zone for `lukelittle.com`
3. Create CNAME records with the exact values shown above
4. Wait 5-30 minutes for validation

### Check validation status:

```bash
# Via AWS Console
# Go to ACM → Certificates (us-east-1 region)
# Wait until status shows "Issued"

# Or via CLI
aws acm describe-certificate \
  --certificate-arn $(terraform output -raw acm_certificate_arn) \
  --region us-east-1 \
  --query 'Certificate.Status' \
  --output text
```

Wait until it returns `ISSUED`.

## Stage 2: Deploy Everything Else

Once the certificate shows "Issued":

```bash
# Deploy all remaining resources
terraform apply
```

This will create:
- S3 bucket
- CloudFront distribution (using the now-validated certificate)
- Bucket policies
- Origin Access Control

After this completes:

1. View the CloudFront domain:
   ```bash
   terraform output cloudfront_distribution_domain
   ```

2. Add A records in Route 53 pointing to that CloudFront domain

3. Deploy your site:
   ```bash
   cd ..
   ./scripts/deploy.sh
   ```

Done! Your site will be live at https://lukelittle.com 🚀
