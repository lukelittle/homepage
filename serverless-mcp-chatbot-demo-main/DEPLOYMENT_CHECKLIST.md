# 🚀 FastMCP Deployment Checklist

Use this checklist for smooth FastMCP + Bedrock deployment.

## ✅ Pre-Deployment

- [ ] AWS CLI configured with valid credentials (`aws sts get-caller-identity`)
- [ ] Terraform installed (`terraform --version`)
- [ ] Python 3.12+ installed (`python3 --version`)
- [ ] Bedrock model access enabled in AWS Console (Claude 3.5 Sonnet in your region)

## 🔧 File Verification

All these files should exist:

- [ ] `data/discogs.csv` - Your vinyl collection data
- [ ] `lambda/handler.py` - FastMCP + Bedrock Lambda function
- [ ] `lambda/requirements.txt` - Python dependencies (boto3, fastmcp)
- [ ] `lambda/build.sh` - Build script (executable)
- [ ] `infra/terraform/versions.tf` - Terraform config
- [ ] `infra/terraform/variables.tf` - Variables
- [ ] `infra/terraform/main.tf` - Main infrastructure
- [ ] `infra/terraform/outputs.tf` - Output values
- [ ] `frontend/index.html` - Web UI (no auth!)
- [ ] `deploy.sh` - Automated deployment script (executable)

## 🚀 Deployment Options

### Option 1: Automated (Recommended)

```bash
./deploy.sh
```

This handles everything: builds Lambda, deploys infrastructure, updates frontend, uploads to S3!

### Option 2: Manual Steps

1. **Build Lambda:**
   ```bash
   cd lambda && ./build.sh && cd ..
   ```

2. **Deploy Infrastructure:**
   ```bash
   cd infra/terraform
   terraform init
   terraform apply
   ```

3. **Get API URL:**
   ```bash
   terraform output api_chat_url
   ```

4. **Update Frontend:**
   Edit `frontend/index.html` and replace:
   - `YOUR_API_URL_HERE/chat` → Your actual API Gateway URL

5. **Upload Frontend:**
   ```bash
   BUCKET=$(terraform output -raw frontend_bucket_name)
   aws s3 cp ../../frontend/index.html s3://$BUCKET/
   ```

## ✅ Post-Deployment Verification

- [ ] Visit the website URL from Terraform output
- [ ] See welcome message (no signup needed!)
- [ ] Send test message: "What Grimes albums do I own?"
- [ ] Verify "🔧 FastMCP Tool Used" badge appears
- [ ] Check general knowledge: "What is vinyl?" (should NOT use tool)
- [ ] Review CloudWatch logs: `/aws/lambda/serverless-mcp-chatbot-demo-chat`

## 🧹 Cleanup

When you're done with the demo:

```bash
cd infra/terraform
terraform destroy
```

This will delete all AWS resources and stop billing.

## 📊 Cost Monitoring

Monitor your costs in AWS Console:
- **Bedrock** - Main cost (~$15/month for 1000 queries)
- **Lambda** - Minimal (~$0.17/month)
- **S3 + API Gateway** - < $0.05/month combined

**Total: ~$15/month** for active use

Set up a billing alarm in AWS Console!

## ⚠️ Common Issues & Quick Fixes

| Issue | Solution |
|-------|----------|
| Terraform fails on lambda.zip | Run `cd lambda && ./build.sh` first |
| Bedrock access denied | Enable Claude in Bedrock console for your region |
| "YOUR_API_URL_HERE" error | Update frontend/index.html with actual API URL |
| Tool not triggering | Ask specific questions: "What **records** do I have by Grimes?" |
| CORS errors | Ensure using `http://` not `https://` for S3 website URL |
| FastMCP import error | Rebuild Lambda: `cd lambda && ./build.sh` |

## 🎯 Demo Success Criteria

Your demo is ready when:
- ✅ Website loads without errors
- ✅ No authentication needed (public demo)
- ✅ Chat responds to messages
- ✅ Tool badge appears for collection queries
- ✅ Tool badge does NOT appear for general questions
- ✅ Responses are relevant and accurate

## 📚 Next Steps

- Read [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) to understand why FastMCP
- Check CloudWatch logs for debugging
- Try adding your own tools with `@mcp.tool()` decorator
- Customize for your own data/demos

Happy demoing with FastMCP! 🎵🚀
