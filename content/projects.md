---
title: "Projects"
description: "Things I've built, with write-ups and code."
ShowPostNavLinks: false
ShowReadingTime: false
---

Most of what I build starts as a demo for a talk, a class, or a question I couldn't stop thinking about. Everything here has a write-up, and most of it has code you can deploy yourself.

## Regulated markets on AWS

**Pre-trade risk controls (SEC Rule 15c3-5)**\
Streaming market access controls with Kafka and Spark, inspired by the Knight Capital incident.\
[Write-up]({{< relref "/posts/2026/02/sec-15c3-5-market-access-controls" >}}) · [Code](https://github.com/lukelittle/sec-15c3-5-market-access-controls-example)

More in the [Regulated Markets on AWS](/series/regulated-markets-on-aws/) series.

## AI and agents

**Vinyl collection chatbot with FastMCP**\
A serverless MCP server that lets an AI agent query a record collection.\
[Write-up]({{< relref "/posts/2026/01/mcp-fastmcp-universal-translator-ai-agents" >}}) · [Code](https://github.com/lukelittle/rawsug-fastmcp-demo)

**GitHub PR reviewer with Bedrock Agents**\
An agent that reviews pull requests using Bedrock Agents and action groups.\
[Write-up]({{< relref "/posts/2026/02/github-bedrock-pr-reviewer" >}})

**AWS cost optimization agent**\
A Bedrock agent that reads Cost Explorer data and recommends ways to cut your bill.\
[Write-up]({{< relref "/posts/2026/02/aws-bedrock-cost-optimization-agent" >}})

**Company knowledge bot**\
Slack plus Bedrock Knowledge Bases for instant answers from your internal docs.\
[Write-up]({{< relref "/posts/2026/02/slack-bedrock-knowledge-base-company-docs" >}})

**Serverless URL shortener, built with Kiro**\
Roughly 15 hours of Terraform done in 3 with an agentic coding tool.\
[Write-up]({{< relref "/posts/2026/01/building-serverless-url-shortener-ai-assisted-kiro" >}}) · [Code](https://github.com/lukelittle/url-shortener)

## Teaching

**Cracking the Cloud survey app**\
A small serverless Pokémon survey app I use to show students what the cloud can do.\
[Write-up]({{< relref "/posts/2025/12/pokemon-surveys-and-cloud-infrastructure" >}}) · [Code](https://github.com/lukelittle/cracking-the-cloud)

**Adding Cognito authentication to the survey app**\
The follow-up: securing the same app with Amazon Cognito.\
[Write-up]({{< relref "/posts/2026/01/adding-cognito-to-our-survey-app" >}}) · [Code](https://github.com/lukelittle/adding-cognito-to-our-survey-app)

**Student branding starter**\
A template for students to launch a personal site and online presence.\
[Write-up]({{< relref "/posts/2026/02/building-your-personal-brand-student-guide" >}}) · [Code](https://github.com/lukelittle/student-branding-starter)

## This site

**lukelittle.com**\
Hugo on S3 and CloudFront, deployed by GitHub Actions with Terraform, for about $3 a year.\
[Write-up]({{< relref "/posts/2025/12/hugo-blog-aws-side-quest" >}}) · [Code](https://github.com/lukelittle/homepage)\
