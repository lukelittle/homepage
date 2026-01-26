#!/bin/bash
set -e

echo "🚀 Serverless MCP Chatbot Demo - FastMCP Deployment"
echo "===================================================="
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install it first."
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install it first."
    exit 1
fi

echo "✓ Prerequisites OK"
echo ""

# Step 1: Build Lambda
echo "📦 Step 1: Building Lambda package with FastMCP..."
cd lambda
./build.sh
cd ..
echo "✓ Lambda package built"
echo ""

# Step 2: Terraform Apply
echo "🏗️  Step 2: Deploying infrastructure with Terraform..."
cd infra/terraform
terraform init
terraform apply

# Get outputs
API_URL=$(terraform output -raw api_chat_url)
BUCKET_NAME=$(terraform output -raw frontend_bucket_name)
WEBSITE_URL=$(terraform output -raw frontend_website_url)

cd ../..

echo "✓ Infrastructure deployed"
echo ""

# Step 3: Update Frontend
echo "🌐 Step 3: Updating frontend configuration..."

# Update API URL in frontend
sed "s|API_URL: 'YOUR_API_URL_HERE/chat'|API_URL: '$API_URL'|g" frontend/index.html > frontend/index.html.tmp
mv frontend/index.html.tmp frontend/index.html

echo "✓ Frontend configuration updated"
echo ""

# Step 4: Upload Frontend
echo "📤 Step 4: Uploading frontend to S3..."
aws s3 cp frontend/index.html s3://$BUCKET_NAME/

echo "✓ Frontend uploaded"
echo ""

# Done!
echo "===================================================="
echo "✅ Deployment Complete!"
echo "===================================================="
echo ""
echo "🌐 Website URL: $WEBSITE_URL"
echo ""
echo "🎉 FastMCP + Bedrock ready to use!"
echo "   No console setup needed - everything deployed via code!"
echo ""
echo "🎵 Try these prompts:"
echo "   - What Grimes albums do I own?"
echo "   - Show me vinyl from 4AD label"
echo "   - What records did I add in 2024?"
echo ""
echo "📚 Read FRAMEWORK_GUIDE.md to learn about FastMCP!"
echo ""
echo "Happy demoing! 🚀"
