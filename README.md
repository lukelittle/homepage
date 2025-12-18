# Luke Little's Personal Blog

Personal blog built with Hugo and deployed to AWS.

**Live Site:** https://lukelittle.com

## Tech Stack

- **Static Site Generator:** [Hugo](https://gohugo.io)
- **Theme:** [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- **Hosting:** AWS S3 + CloudFront
- **Infrastructure:** Terraform
- **Cost:** ~$0.50/month

## Quick Start

### Local Development

```bash
# Install Hugo (macOS)
brew install hugo

# Clone repo
git clone https://github.com/lukelittle/homepage.git
cd homepage

# Start local server
hugo server -D

# Visit http://localhost:1313
```

### Create New Post

```bash
hugo new posts/my-new-post/index.md
```

Edit the file in `content/posts/my-new-post/index.md`, then preview with `hugo server -D`.

### Deploy to Production

```bash
./scripts/deploy.sh
```

This builds the site, uploads to S3, and invalidates the CloudFront cache.

## Project Structure

```
.
├── content/          # Blog posts and pages
├── static/           # Static assets (images, etc.)
├── themes/           # Hugo theme (PaperMod)
├── terraform/        # AWS infrastructure (S3, CloudFront, ACM)
├── scripts/          # Deployment automation
├── public/           # Built site (generated, not committed)
├── config.yaml       # Hugo configuration
└── DEPLOYMENT.md     # Full deployment guide
```

## Infrastructure

The blog is hosted on AWS using:

- **S3 Bucket:** Stores static files
- **CloudFront:** Global CDN with HTTPS
- **ACM:** Free SSL certificate
- **Route 53:** DNS (managed separately)

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for complete deployment instructions.

## Terraform

Infrastructure is managed with Terraform. See [`terraform/README.md`](terraform/README.md) for details.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## License

Content: © Luke Little  
Code: MIT License
