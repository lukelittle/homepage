#!/bin/bash
set -e

echo "🔨 Building Lambda deployment package..."

# Clean up
rm -rf package
rm -f lambda.zip

# Create package directory
mkdir -p package

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -t package/ --platform manylinux2014_aarch64 --only-binary=:all:

# Copy handler
echo "📄 Copying handler..."
cp handler.py package/

# Create zip
echo "🗜️  Creating deployment package..."
cd package
zip -r ../lambda.zip . -q
cd ..

# Clean up
rm -rf package

echo "✅ Lambda package created: lambda.zip"
echo "   Size: $(du -h lambda.zip | cut -f1)"
