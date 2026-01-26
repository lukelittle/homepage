# Lambda Function - FastMCP + Bedrock

This directory contains the Lambda function for the Serverless MCP Chatbot Demo using **FastMCP**.

## 🌐 Architecture: FastMCP + Bedrock

FastMCP provides the **Model Context Protocol** implementation. Bedrock handles the reasoning. Simple and powerful!

```
User Request → Lambda → FastMCP tools → Bedrock → Tool execution → Response
```

## Files

- **handler.py** - Main Lambda with FastMCP server and Bedrock integration
- **requirements.txt** - Minimal dependencies: boto3, fastmcp
- **build.sh** - Build script for deployment package (ARM64)

## Building the Lambda Package

```bash
cd lambda
./build.sh
```

Creates `lambda.zip` with all dependencies (~16MB with FastMCP, very efficient!)

## How It Works

### FastMCP Tool Definition

FastMCP makes tool definitions incredibly simple:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vinyl-collection-server")

@mcp.tool()
def query_vinyl_collection(query_type: str, search_term: str, limit: int = 10) -> str:
    """Query Luke's vinyl collection"""
    # Your business logic here
    return results
```

**That's it!** FastMCP handles the MCP protocol details.

### Bedrock Integration

The handler integrates FastMCP with Bedrock:

```python
# Get tool definitions in Bedrock format
tools = mcp.list_tools_for_llm(llm_format="bedrock")

# Bedrock decides when to use tools
response = bedrock_client.converse(
    modelId="claude-3-5-sonnet",
    messages=messages,
    toolConfig={"tools": tools}
)

# FastMCP executes the tool
if tool_use_requested:
    result = mcp.call_tool(tool_name, tool_input)
```

### Agentic Loop

The handler implements a full agentic loop:

1. **User sends message** → API Gateway → Lambda
2. **Bedrock reasons** → Decides if tool use is needed
3. **Tool execution** → FastMCP executes via `@mcp.tool()` decorator
4. **Result to Bedrock** → Synthesizes final answer
5. **Response to user** → With `tool_used` flag

## Tool: query_vinyl_collection

Demonstrates MCP tool behavior:

- Reads `discogs.csv` from S3
- Filters by query type: artist, label, year, title, or all
- Returns formatted results
- MCP-compliant via FastMCP decorator

**Query types:**
- `artist` - Search by artist name
- `label` - Search by record label
- `year` - Search by release year
- `title` - Search by album title
- `all` - Browse entire collection

## Environment Variables

Set automatically by Terraform:

- `PROJECT_TAG` - Project identifier
- `DATA_BUCKET` - S3 bucket containing discogs.csv
- `DATA_KEY` - S3 object key (default: discogs.csv)
- `BEDROCK_MODEL_ID` - Model to use (default: Claude 3.5 Sonnet v2)
- `FRONTEND_ORIGIN` - CORS origin for API responses

## Testing Locally

Test the Lambda locally:

```python
import handler
import json
import os

# Set required environment variables
os.environ['DATA_BUCKET'] = 'your-bucket'
os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-5-sonnet-20241022-v2:0'

event = {
    'body': json.dumps({'message': 'What Grimes records do I have?'})
}

result = handler.lambda_handler(event, None)
print(json.loads(result['body']))
```

Make sure AWS credentials are configured!

## Adding Your Own Tools

Want to add more tools? FastMCP makes it easy:

```python
@mcp.tool()
def your_new_tool(param: str) -> str:
    """Your tool description for the model"""
    # Your logic here
    return result
```

FastMCP automatically:
- ✅ Generates MCP-compliant tool schema
- ✅ Converts to Bedrock format
- ✅ Handles tool execution
- ✅ Manages errors and responses

## Why FastMCP?

### vs. Manual Bedrock Tool Use
- **Less code** - Decorators vs. manual JSON schemas
- **Standards-based** - True MCP protocol
- **Maintainable** - Tool definitions with business logic

### vs. AgentCore
- **Zero console setup** - Everything in code
- **Version controlled** - All configuration in git
- **Flexible** - Easy to customize and extend

### vs. LangChain
- **Simpler** - No framework overhead
- **Focused** - Just MCP protocol
- **Lightweight** - Smaller Lambda package

## Learn More

- [FRAMEWORK_GUIDE.md](../FRAMEWORK_GUIDE.md) - FastMCP vs. alternatives
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

## CloudWatch Logs

Monitor your Lambda:
```bash
aws logs tail /aws/lambda/serverless-mcp-chatbot-demo-chat --follow
```

Look for these emojis in logs:
- 🚀 Server initialization
- 🎵 Tool called
- 📀 CSV loaded
- ✅ Results found
- 🔧 FastMCP tools available
- 🔄 Bedrock iteration
- ⚡ Stop reason

Happy building with FastMCP! 🎉
