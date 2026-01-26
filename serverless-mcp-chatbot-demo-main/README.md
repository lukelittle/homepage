# 🎵 Serverless MCP Chatbot Demo

A dead-simple serverless chatbot using **FastMCP** + **AWS Bedrock**. No auth, no console setup, just code. Perfect for demos!

Ask about Luke's vinyl collection and watch the bot intelligently decide when to query the data. **True agentic AI** in action! 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)

---

## 🎯 Why This Demo?

Perfect for **AWS User Groups** and **University presentations** because it's:

✅ **Simple** - Deploy in 2 minutes with `./deploy.sh`  
✅ **No Console Setup** - Everything in code, no clicking around AWS Console  
✅ **Agentic AI** - Watch the bot decide when to use tools  
✅ **True MCP** - Implements Model Context Protocol standard  
✅ **Cheap** - ~$15/month, mostly Bedrock costs  
✅ **Educational** - Clean code, heavily commented  

### What is "Agentic"?

Traditional bots always do the same thing. **Agentic AI decides**:
- Ask "What Grimes records do I have?" → ✅ Uses tool, queries CSV
- Ask "What is vinyl?" → ❌ No tool, answers from knowledge

The bot **chooses** based on the question. That's agentic behavior!

---

## 🏗️ Architecture (Super Simple)

```
Browser          API Gateway         Lambda               Bedrock
(S3 HTML)    →   (Public)       →   (FastMCP)       →    (Claude)
                                         ↓
                                     S3 CSV Data
```

**That's it!** No auth, no databases, just:
1. S3 hosts the website
2. API Gateway routes requests  
3. Lambda runs FastMCP + Bedrock
4. CSV file has the data

### Why FastMCP?

**FastMCP** = Model Context Protocol implementation for Python

```python
# Define tools with a decorator - SO SIMPLE!
@mcp.tool()
def query_vinyl_collection(query_type: str, search_term: str) -> str:
    """Query the vinyl collection"""
    return results
```

**That's it!** FastMCP handles:
- ✅ Tool schema generation
- ✅ MCP protocol compliance  
- ✅ Bedrock format conversion
- ✅ Tool execution

**vs. Manual**: Write JSON schemas, handle tool routing, parse responses  
**vs. AgentCore**: No console setup, everything in code  
**vs. LangChain**: Lighter, focused on MCP standard

Read [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) for detailed comparison!

---

## 🚀 Quick Start (Seriously, It's Easy)

### Prerequisites

- AWS Account with CLI configured (`aws configure`)
- Terraform installed
- Python 3.12+
- Bedrock access (enable Claude in your region)

### Deploy Everything

```bash
./deploy.sh
```

**That's it!** The script:
1. Builds Lambda package  
2. Deploys infrastructure
3. Configures frontend
4. Uploads to S3
5. Shows you the URL

Visit the URL and start chatting! 🎉

### Manual Steps (If You Want Control)

```bash
# 1. Build Lambda
cd lambda && ./build.sh && cd ..

# 2. Deploy infrastructure
cd infra/terraform
terraform init
terraform apply

# 3. Get API URL
terraform output api_chat_url

# 4. Update frontend/index.html with API URL

# 5. Upload frontend
BUCKET=$(terraform output -raw frontend_bucket_name)
aws s3 cp ../../frontend/index.html s3://$BUCKET/

# 6. Get website URL
terraform output frontend_website_url
```

---

## 📁 Project Structure

```
serverless-mcp-chatbot-demo/
├── lambda/
│   ├── handler.py           # FastMCP + Bedrock integration
│   ├── requirements.txt     # Just boto3 + fastmcp!
│   └── build.sh             # Build deployment package
├── infra/terraform/
│   ├── main.tf              # ALL infrastructure (simple!)
│   ├── variables.tf         # Configuration
│   └── outputs.tf           # URLs and next steps
├── frontend/
│   └── index.html           # Single-file web app
├── data/
│   └── discogs.csv          # Vinyl collection data
├── FRAMEWORK_GUIDE.md       # FastMCP vs alternatives
├── DEPLOYMENT_CHECKLIST.md  # Step-by-step guide
└── README.md                # You are here!
```

**No auth code, no complex state management, no microservices - just working AI!**

---

## 💬 How To Use

### Example Prompts

| Prompt | What Happens | Tool Used? |
|--------|-------------|------------|
| "What Grimes albums do I own?" | Queries CSV, returns results | ✅ Yes |
| "Show me vinyl from 4AD label" | Filters by label | ✅ Yes |
| "What records did I add in 2024?" | Filters by year | ✅ Yes |
| "Do I have any Kraftwerk?" | Searches artist | ✅ Yes |
| "What is vinyl?" | Answers from knowledge | ❌ No |
| "How does MCP work?" | Explains concept | ❌ No |

Watch for the **🔧 FastMCP Tool Used** badge when tools are invoked!

### 30-Second Demo Script

> "This chatbot demonstrates agentic AI using FastMCP and AWS Bedrock. When I ask about my vinyl collection" [type "What Grimes records do I have?"] "the AI decides to query the data - see the green badge? But if I ask" [type "What is vinyl?"] "it just answers from knowledge. The AI chooses when to use tools. All serverless, costs $15/month, true MCP protocol, and everything's in code - no console setup needed!"

---

## 🔧 How It Works (Under the Hood)

### 1. FastMCP Tool Definition

```python
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("vinyl-collection-server")

# Define tool with decorator
@mcp.tool()
def query_vinyl_collection(query_type: str, search_term: str, limit: int = 10) -> str:
    """
    Query Luke's vinyl record collection.
    
    Args:
        query_type: One of: artist, label, year, title, all
        search_term: What to search for
        limit: Max results (default 10)
    """
    # Download CSV from S3
    response = s3_client.get_object(Bucket=DATA_BUCKET, Key='discogs.csv')
    records = parse_csv(response['Body'])
    
    # Filter records
    matches = filter_records(records, query_type, search_term)
    
    # Return formatted results
    return format_results(matches[:limit])
```

### 2. Bedrock Integration

```python
# Get FastMCP tools in Bedrock format
tools = mcp.list_tools_for_llm(llm_format="bedrock")

# Bedrock decides when to use tools
response = bedrock_client.converse(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    messages=messages,
    toolConfig={"tools": tools}
)

# If tool use requested, FastMCP executes it
if response['stopReason'] == 'tool_use':
    result = mcp.call_tool(tool_name, tool_input)
```

### 3. Agentic Loop

1. User sends message
2. Lambda invokes Bedrock with FastMCP tools
3. Bedrock reasons about whether to use tools
4. If yes: FastMCP executes tool, sends result back to Bedrock
5. Bedrock synthesizes final answer
6. Response returned to user

---

## 💰 Cost Breakdown

Monthly costs (1000 queries):

| Service | Cost | Notes |
|---------|------|-------|
| **Bedrock** | ~$15.00 | Main cost (Claude 3.5 Sonnet) |
| **Lambda** | $0.17 | 1000 invocations, ARM64 |
| **S3** | $0.02 | Storage + requests |
| **API Gateway** | $0.01 | HTTP API (cheap!) |
| **Total** | **~$15.20** | 🎉 |

**Most cost is Bedrock!** Infrastructure is basically free.

### Save Money Tips
- Use ARM64 Lambda (already configured)
- Keep conversations short (fewer tokens)
- Use smaller Bedrock models for dev
- Leverage AWS Free Tier

---

## 🎨 Customization Ideas

### Use Your Own Data

Replace `data/discogs.csv`:

```csv
title,artist,year,genre
"Your","Data","2024","Cool"
```

Update tool logic in `lambda/handler.py` and you're done!

**Ideas**: 
- Book collection
- Recipe database  
- Movie watchlist
- Pokemon cards
- Plant care guide
- Anything CSV!

### Add More Tools

```python
@mcp.tool()
def get_collection_stats() -> str:
    """Get statistics about the collection"""
    # Count records, get averages, etc.
    return stats

@mcp.tool()
def recommend_similar(artist: str) -> str:
    """Recommend similar artists"""
    # Your logic here
    return recommendations
```

FastMCP automatically makes them available to Bedrock!

### Use DynamoDB Instead

For larger datasets:
1. Add DynamoDB table in Terraform
2. Update tool to query DynamoDB
3. Add IAM permissions

### Make It Multi-User

Add authentication (we removed it for simplicity):
1. Add Cognito resources back to Terraform
2. Add JWT authorizer to API Gateway  
3. Add auth UI to frontend

See git history for the old auth implementation!

---

## 🐛 Troubleshooting

### "YOUR_API_URL_HERE" Error

**Fix**: Update `CONFIG.API_URL` in `frontend/index.html` with actual API Gateway URL from `terraform output api_chat_url`

### Tool Never Triggers

**Fix**: Be more specific: "What **records** do I have by Grimes?" vs "Tell me about Grimes"

### Bedrock Access Denied

**Fix**: 
1. Go to AWS Bedrock console
2. Enable model access
3. Choose Claude 3.5 Sonnet
4. Wait for approval (usually instant)

### Lambda Timeout

**Fix**: Increase timeout in `infra/terraform/main.tf`:
```hcl
timeout = 120  # Increase from 60
```

### CORS Errors

**Fix**: Use `http://` not `https://` for S3 website URLs (they don't support HTTPS by default)

### Build Fails

**Fix**: 
```bash
cd lambda
rm -rf package lambda.zip
./build.sh
```

---

## 📚 Learn More

### Documentation
- [Lambda README](lambda/README.md) - Deep dive on FastMCP implementation
- [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) - FastMCP vs LangChain vs AgentCore
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Step-by-step deployment

### External Resources
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://spec.modelcontextprotocol.io/)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

## 🎓 Educational Use

This project is **designed for teaching**:

✅ **AWS User Groups** - Show serverless + AI patterns  
✅ **University Classes** - Cloud computing coursework  
✅ **Bootcamps** - Hands-on AI + AWS project  
✅ **Portfolio** - Demonstrate full-stack skills  

**You can:**
- Present at meetups (please do!)
- Use in classroom settings
- Modify for your own demos  
- Put on your resume

**Just please:**
- Don't use it to scrape data
- Don't run up massive Bedrock bills (monitor costs!)
- Give credit if you fork it

---

## 🤝 Contributing

Ideas for improvements:
- [ ] Streaming responses
- [ ] Conversation history
- [ ] More example tools
- [ ] Cost optimization tips
- [ ] Multi-language support
- [ ] Docker local dev setup

PRs welcome! Keep it simple though - that's the whole point! 😄

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

**TL;DR**: Use it however you want! Build cool stuff! 🚀

---

## 🙋 Questions?

- **Found a bug?** Open an issue
- **Using this for a talk?** Tag me - I'd love to see it!
- **Want to collaborate?** Reach out!

Made with ❤️ for the AWS + AI community

**Now go deploy it and show people agentic AI!** 🎉
