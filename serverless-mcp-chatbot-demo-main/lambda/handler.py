"""
Serverless MCP Chatbot Demo - FastMCP + Bedrock Implementation
TRUE Model Context Protocol with FastMCP! No console setup, just code.

This is SIMPLE - FastMCP provides MCP protocol, Bedrock does reasoning.
Everything in code, fully automated with Terraform!
"""

import os
import json
import logging
import csv
from io import StringIO
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
PROJECT_TAG = os.environ.get('PROJECT_TAG', 'serverless-mcp-chatbot-demo')
DATA_BUCKET = os.environ.get('DATA_BUCKET')
DATA_KEY = os.environ.get('DATA_KEY', 'discogs.csv')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN', '*')

# AWS clients
s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime')

# Create FastMCP server - TRUE MCP Protocol! 🎉
mcp = FastMCP("vinyl-collection-server")

logger.info(f"🚀 FastMCP Server initialized | Model: {BEDROCK_MODEL_ID}")

# ============================================================================
# MCP TOOL DEFINITION - Use the @mcp.tool() decorator!
# This is what FastMCP is all about - clean, simple tool definitions
# ============================================================================

@mcp.tool()
def query_vinyl_collection(query_type: str, search_term: str, limit: int = 10) -> str:
    """
    Query Luke's vinyl record collection from his Discogs export.
    
    Use this tool when users ask about specific records, artists, labels, years,
    or want to browse the collection. Do NOT use for general music trivia.
    
    Args:
        query_type: Type of query - one of: artist, label, year, title, all
        search_term: The term to search for (artist name, label, year, or title)
        limit: Maximum number of results to return (default 10, max 50)
        
    Returns:
        Formatted list of matching vinyl records from the collection
    """
    try:
        logger.info(f"🎵 MCP Tool Called: query_vinyl_collection | type={query_type}, term={search_term}")
        
        # Download CSV from S3
        response = s3_client.get_object(Bucket=DATA_BUCKET, Key=DATA_KEY)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(StringIO(csv_content))
        records = list(csv_reader)
        
        logger.info(f"📀 Loaded {len(records)} records from CSV")
        
        # Filter records based on query type
        matches = []
        search_lower = search_term.lower()
        
        if query_type == "all":
            matches = records
        elif query_type == "artist":
            matches = [r for r in records if search_lower in r.get('Artist', '').lower()]
        elif query_type == "label":
            matches = [r for r in records if search_lower in r.get('Label', '').lower()]
        elif query_type == "year":
            matches = [r for r in records if search_term in r.get('Released', '')]
        elif query_type == "title":
            matches = [r for r in records if search_lower in r.get('Title', '').lower()]
        
        # Limit results
        matches = matches[:min(limit, 50)]
        
        logger.info(f"✅ Found {len(matches)} matching records")
        
        # Format results
        if not matches:
            return f"No records found matching {query_type}='{search_term}'"
        
        result_lines = [f"Found {len(matches)} record(s):\n"]
        for i, record in enumerate(matches, 1):
            artist = record.get('Artist', 'Unknown')
            title = record.get('Title', 'Unknown')
            label = record.get('Label', '')
            year = record.get('Released', '')
            format_type = record.get('Format', '')
            condition = record.get('Collection Media Condition', '')
            
            result_lines.append(
                f"{i}. {artist} - {title} "
                f"({year}) [{label}] "
                f"Format: {format_type}"
            )
            if condition:
                result_lines[-1] += f" | Condition: {condition}"
        
        return "\n".join(result_lines)
        
    except ClientError as e:
        logger.error(f"S3 error: {e}")
        return f"Error accessing vinyl collection: {str(e)}"
    except Exception as e:
        logger.error(f"Error querying vinyl collection: {e}", exc_info=True)
        return f"Error querying collection: {str(e)}"


# ============================================================================
# BEDROCK + FASTMCP INTEGRATION
# FastMCP generates tool definitions, Bedrock does the reasoning
# ============================================================================

def invoke_bedrock_with_mcp_tools(user_message: str) -> tuple[str, bool]:
    """
    Invoke Bedrock with FastMCP tool definitions.
    
    This is the magic! FastMCP provides MCP-compliant tool definitions,
    Bedrock decides when to use them. Best of both worlds!
    
    Flow:
    1. Get tool definitions from FastMCP server
    2. Send to Bedrock with user message
    3. Bedrock decides whether to call tools
    4. If tool use: FastMCP executes, return result to Bedrock
    5. Bedrock synthesizes final answer
    
    Args:
        user_message: User's message
        
    Returns:
        tuple: (reply_text, tool_used_flag)
    """
    try:
        # Get MCP tool definitions - FastMCP converts to Bedrock format!
        tools = mcp.list_tools_for_llm(llm_format="bedrock")
        
        logger.info(f"🔧 FastMCP Tools available: {[t['toolSpec']['name'] for t in tools]}")
        
        # Build conversation
        messages = [{
            "role": "user",
            "content": [{"text": user_message}]
        }]
        
        system_prompt = [{
            "text": """You are a helpful assistant that can query Luke's vinyl record collection.

When users ask about specific records in the collection, use the query_vinyl_collection tool.
Keep responses concise and demo-friendly (2-3 sentences typically).

For general music questions not about the specific collection, answer from your knowledge without using tools.

Be enthusiastic about music! 🎵"""
        }]
        
        tool_used = False
        max_iterations = 5
        
        # Agentic loop with tool use
        for iteration in range(max_iterations):
            logger.info(f"🔄 Bedrock iteration {iteration + 1}")
            
            # Call Bedrock Converse API with MCP tools
            response = bedrock_client.converse(
                modelId=BEDROCK_MODEL_ID,
                messages=messages,
                system=system_prompt,
                toolConfig={"tools": tools},
                inferenceConfig={
                    "maxTokens": 2000,
                    "temperature": 0.7
                }
            )
            
            stop_reason = response['stopReason']
            logger.info(f"⚡ Bedrock stop reason: {stop_reason}")
            
            # Get assistant's response
            assistant_message = response['output']['message']
            messages.append(assistant_message)
            
            # Check if tool use was requested
            if stop_reason == 'tool_use':
                tool_used = True
                logger.info("🔧 Tool use requested by Bedrock!")
                
                # Process tool requests using FastMCP
                tool_results = []
                for content_block in assistant_message['content']:
                    if 'toolUse' in content_block:
                        tool_use_block = content_block['toolUse']
                        tool_name = tool_use_block['name']
                        tool_input = tool_use_block['input']
                        tool_use_id = tool_use_block['toolUseId']
                        
                        logger.info(f"🛠️  Calling MCP tool: {tool_name} | Input: {tool_input}")
                        
                        # Execute tool via FastMCP
                        result = mcp.call_tool(tool_name, tool_input)
                        
                        logger.info(f"📊 Tool result: {result[:200]}...")
                        
                        tool_results.append({
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [{"text": str(result)}]
                            }
                        })
                
                # Send tool results back to Bedrock
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Continue loop to get final answer
                continue
                
            else:
                # End of turn - extract final response
                final_response = ""
                for content_block in assistant_message['content']:
                    if 'text' in content_block:
                        final_response += content_block['text']
                
                logger.info(f"✅ Final response: {final_response[:200]}...")
                return final_response, tool_used
        
        return "Maximum iterations reached. Please rephrase your question.", tool_used
        
    except ClientError as e:
        logger.error(f"Bedrock error: {e}", exc_info=True)
        return f"Sorry, I encountered an error: {str(e)}", False
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return f"Sorry, something went wrong: {str(e)}", False


# ============================================================================
# LAMBDA HANDLER
# ============================================================================

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for chat endpoint.
    
    Simple! Just parse request, call Bedrock with FastMCP tools, return response.
    No console setup, no manual configuration - everything in code! 🎉
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    logger.info(f"📨 Request received | FastMCP + Bedrock")
    
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        user_message = body.get('message', '').strip()
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': FRONTEND_ORIGIN
                },
                'body': json.dumps({
                    'error': 'Message is required'
                })
            }
        
        logger.info(f"💬 Processing: {user_message}")
        
        # Invoke Bedrock with FastMCP tools
        reply, tool_used = invoke_bedrock_with_mcp_tools(user_message)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': FRONTEND_ORIGIN
            },
            'body': json.dumps({
                'reply': reply,
                'tool_used': tool_used,
                'mode': 'fastmcp'
            })
        }
    
    except Exception as e:
        logger.error(f"❌ Handler error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': FRONTEND_ORIGIN
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
