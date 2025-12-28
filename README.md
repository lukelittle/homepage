# Luke Little's Blog

My personal blog hosted at [lukelittle.com](https://lukelittle.com)

Hugo + AWS + GitHub Actions = ~$3/year hosting

## Daily Use

### Writing a new post

```bash
hugo new posts/my-post-title/index.md
hugo server -D  # preview at localhost:1313
```

Edit in `content/posts/`, then push to deploy:

```bash
git add .
git commit -m "New post: whatever"
git push
```

GitHub Actions handles the rest (build → upload to S3 → invalidate CloudFront).

### Running locally

```bash
hugo server -D
```

Visit http://localhost:1313

## Tech Stack

- **Hugo** - Static site generator (crazy fast)
- **PaperMod** - Clean, minimal theme
- **AWS S3 + CloudFront** - Hosting + CDN
- **Terraform** - Infrastructure as code
- **GitHub Actions** - Automated deployments with OIDC

## Infrastructure

Everything's in AWS:
- S3 bucket stores the files
- CloudFront serves them globally with HTTPS
- ACM provides the SSL cert (free)
- Route 53 handles DNS

Deployed via Terraform. See [`terraform/README.md`](terraform/README.md) if you need to modify infrastructure.

Automated deployment via GitHub Actions. See [`GITHUB_ACTIONS_SETUP.md`](GITHUB_ACTIONS_SETUP.md) for setup details.

## Project Structure

```
.
├── content/              # Blog posts and pages
├── static/               # Images, CSS, etc.
├── themes/PaperMod/      # Theme (git submodule)
├── terraform/            # AWS infrastructure
├── .github/workflows/    # Deployment automation
└── config.yaml           # Hugo config
```

## Emergency Manual Deploy

If GitHub Actions is down:

```bash
./scripts/deploy.sh
```

## Cost

About $0.25/month. Mostly S3 storage.

## For Visitors

Feel free to browse the code to see how it's built. This is how I run a simple blog on AWS for pennies. The Terraform configs and GitHub Actions setup might be useful if you're building something similar.