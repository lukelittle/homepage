# GitHub Actions Deployment Setup

This guide explains how to set up automated deployments to AWS using GitHub Actions with OIDC authentication.

## Architecture Overview

- **Hugo** builds the static site
- **GitHub Actions** automates the deployment
- **AWS OIDC** provides temporary credentials (no long-lived access keys!)
- **S3** hosts the static files
- **CloudFront** serves content via CDN

## One-Time Setup

### Step 1: Deploy Terraform Infrastructure

First, create the AWS resources including the OIDC provider and IAM role:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Important:** Save the outputs! You'll need them for GitHub secrets.

### Step 2: Get Required Values from Terraform

After `terraform apply` completes, get these values:

```bash
# Get the GitHub Actions role ARN
terraform output github_actions_role_arn

# Get the CloudFront distribution ID
terraform output cloudfront_distribution_id

# Get the S3 bucket name
terraform output s3_bucket_name
```

### Step 3: Add GitHub Secrets

Go to your GitHub repository:
1. Navigate to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `AWS_ROLE_ARN` | `arn:aws:iam::168737286209:role/github-actions-homepage-deploy` | From `terraform output github_actions_role_arn` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `E1234567890ABC` | From `terraform output cloudfront_distribution_id` |
| `S3_BUCKET_NAME` | `168737286209-us-east-1-homepage` | From `terraform output s3_bucket_name` |

### Step 4: Test the Deployment

You can trigger a deployment in two ways:

#### Option A: Push to main branch
```bash
git add .
git commit -m "Setup GitHub Actions deployment"
git push origin main
```

#### Option B: Manual trigger
1. Go to **Actions** tab in GitHub
2. Select **Deploy to AWS** workflow
3. Click **Run workflow**
4. Select **main** branch
5. Click **Run workflow**

### Step 5: Monitor the Deployment

1. Go to the **Actions** tab in your GitHub repository
2. Click on the latest workflow run
3. Watch the deployment progress in real-time
4. Check for any errors in the logs

## How It Works

### OIDC Authentication Flow

1. GitHub Actions requests a temporary token from GitHub's OIDC provider
2. GitHub Actions assumes the AWS IAM role using the token
3. AWS validates the token and grants temporary credentials (valid for ~1 hour)
4. Deployment runs with the temporary credentials
5. Credentials automatically expire after the workflow completes

### No Secrets Stored!

The only "secret" stored in GitHub (`AWS_ROLE_ARN`) is just an identifier - it's not a credential and can't be used to access AWS directly. An attacker would need:
- The role ARN (public-ish, not sensitive)
- A valid OIDC token from GitHub (only issued during workflow runs)
- From the correct repository (restricte in IAM trust policy)

This is why OIDC is more secure than access keys!

## Deployment Process

When code is pushed to `main`, the workflow:

1. ✅ Checks out code (including Hugo theme submodules)
2. ✅ Installs Hugo (extended version)
3. ✅ Builds the site with `hugo --minify`
4. ✅ Configures AWS credentials via OIDC
5. ✅ Syncs files to S3 with appropriate cache headers
6. ✅ Invalidates CloudFront cache for immediate updates

## Cache Strategy

- **Static assets** (CSS, JS, images): 1 hour cache (`max-age=3600`)
- **HTML/XML files**: 5 minutes cache (`max-age=300`) for faster content updates
- **CloudFront invalidation**: Clears CDN cache globally (~5-10 minutes)

## Troubleshooting

### Workflow fails with "AccessDenied"
- Verify the `AWS_ROLE_ARN` secret is correct
- Check that Terraform was successfully applied
- Ensure the IAM role trust policy includes your repository

### Workflow fails with "Error assuming role"
- Verify the OIDC provider was created in AWS
- Check that the role ARN matches exactly
- Ensure `id-token: write` permission is set in workflow

### CloudFront still shows old content
- Cache invalidation takes 5-10 minutes to propagate
- Check the invalidation status in AWS CloudFront console
- Hard refresh your browser (Cmd+Shift+R or Ctrl+Shift+R)

### How to check IAM resources
```bash
# List OIDC providers
aws iam list-open-id-connect-providers

# Check role
aws iam get-role --role-name github-actions-homepage-deploy

# List attached policies
aws iam list-attached-role-policies --role-name github-actions-homepage-deploy
```

## Manual Deployment (Alternative)

If you prefer to deploy manually, the old script still works:

```bash
./scripts/deploy.sh
```

This is useful for:
- Testing deployments locally
- Emergency deployments when GitHub Actions is down
- Debugging deployment issues

## Security Notes

✅ **Secure:**
- No long-lived credentials
- Temporary tokens (auto-expire)
- Restricted to specific repository
- Can restrict to specific branches
- Audit trail in GitHub Actions logs

❌ **Not Secure (Old Way):**
- IAM user access keys in GitHub secrets
- Keys never expire
- If leaked, permanent access until rotated
- No audit trail of who/what used them

## Reusing for Other Projects

To use this setup for another project:

1. Copy `terraform/iam.tf` to the new project's Terraform directory
2. Update resource names to include the project name (not "homepage")
3. Update the repository name in the trust policy condition
4. Update the GitHub Actions workflow file
5. Apply Terraform and add secrets to the new repository

**Important:** Each project should have its own IAM role and policies to maintain proper isolation!

## Resources

- [AWS OIDC Blog Post](https://aws.amazon.com/blogs/security/use-iam-roles-to-connect-github-actions-to-actions-in-aws/)
- [GitHub OIDC Docs](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)

## Questions?

If you encounter issues:
1. Check the GitHub Actions logs for detailed error messages
2. Verify all secrets are set correctly in GitHub
3. Ensure Terraform was successfully applied
4. Check AWS IAM console for role/policy configuration
