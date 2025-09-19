#!/usr/bin/env python3
"""
Jimeng MCP Server
A Model Context Protocol server for Jimeng AI image generation
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JimengAPI:
    """Jimeng AI API client"""

    def __init__(self):
        self.base_url = "https://jimeng.jianying.com"
        self.api_key = os.getenv('JIMENG_API_KEY') or os.getenv('jimeng_key')
        self.session_token = os.getenv('JIMENG_SESSION_TOKEN') or self.api_key

        if not self.session_token:
            raise ValueError("JIMENG_SESSION_TOKEN or JIMENG_API_KEY must be set")

    async def generate_image(self, prompt: str, style: str = "通用", size: str = "1024x1024", model: str = "jimeng-2.1") -> Dict[str, Any]:
        """Generate image using Jimeng API"""
        try:
            async with httpx.AsyncClient() as client:
                # Parse size to width and height
                if 'x' in size:
                    width, height = map(int, size.split('x'))
                else:
                    width = height = 1024

                headers = {
                    "Cookie": f"sessionid={self.session_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }

                data = {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "sample_strength": 0.5
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/generate",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "data": result,
                        "image_url": result.get("url") or result.get("image_url")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API Error: {response.status_code} - {response.text}",
                        "status_code": response.status_code
                    }

        except Exception as e:
            logger.error(f"Jimeng API error: {str(e)}")
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }

    async def get_models(self) -> Dict[str, Any]:
        """Get available models from Jimeng API (mock implementation)"""
        # Since we don't have access to a models endpoint, return mock data
        return {
            "success": True,
            "models": [
                {
                    "id": "jimeng-2.1",
                    "description": "Jimeng AI v2.1 - General purpose image generation model"
                },
                {
                    "id": "jimeng-pro",
                    "description": "Jimeng AI Pro - High quality image generation"
                }
            ]
        }

# Initialize Jimeng API
jimeng_api = JimengAPI()

class JimengMCPServer:
    def __init__(self):
        self.server = Server("jimeng-mcp")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Jimeng tools"""
            return [
                Tool(
                    name="generate_image",
                    description="Generate an image using Jimeng AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The text prompt for image generation"
                            },
                            "style": {
                                "type": "string",
                                "description": "Image style (default: 通用)",
                                "default": "通用",
                                "enum": ["通用", "写实", "动漫", "油画", "水彩", "素描", "国风"]
                            },
                            "size": {
                                "type": "string",
                                "description": "Image size (default: 1024x1024)",
                                "default": "1024x1024",
                                "enum": ["512x512", "768x768", "1024x1024", "1024x1536", "1536x1024"]
                            },
                            "model": {
                                "type": "string",
                                "description": "Model to use for generation (default: jimeng-2.1)",
                                "default": "jimeng-2.1"
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="get_models",
                    description="Get list of available Jimeng AI models",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "generate_image":
                    prompt = arguments.get("prompt")
                    if not prompt:
                        return CallToolResult(
                            content=[TextContent(type="text", text="Error: prompt is required")],
                            isError=True
                        )

                    style = arguments.get("style", "通用")
                    size = arguments.get("size", "1024x1024")
                    model = arguments.get("model", "jimeng-2.1")

                    logger.info(f"Generating image with prompt: {prompt}")
                    result = await jimeng_api.generate_image(prompt, style, size, model)

                    if result["success"]:
                        response_text = f"✅ Image generated successfully!\n\n"
                        response_text += f"📝 Prompt: {prompt}\n"
                        response_text += f"🎨 Style: {style}\n"
                        response_text += f"📐 Size: {size}\n"
                        response_text += f"🤖 Model: {model}\n"

                        if result.get("image_url"):
                            response_text += f"\n🖼️ Image URL: {result['image_url']}\n"

                        response_text += f"\n📊 Full Response:\n```json\n{json.dumps(result['data'], indent=2, ensure_ascii=False)}\n```"

                        return CallToolResult(
                            content=[TextContent(type="text", text=response_text)]
                        )
                    else:
                        error_text = f"❌ Image generation failed!\n\n"
                        error_text += f"📝 Prompt: {prompt}\n"
                        error_text += f"❌ Error: {result['error']}"

                        return CallToolResult(
                            content=[TextContent(type="text", text=error_text)],
                            isError=True
                        )

                elif name == "get_models":
                    logger.info("Getting available models")
                    result = await jimeng_api.get_models()

                    if result["success"]:
                        response_text = "✅ Available Jimeng AI Models:\n\n"
                        for model in result["models"]:
                            response_text += f"🤖 {model.get('id', 'Unknown')}\n"
                            if model.get('description'):
                                response_text += f"   📝 {model['description']}\n"
                            response_text += "\n"

                        return CallToolResult(
                            content=[TextContent(type="text", text=response_text)]
                        )
                    else:
                        error_text = f"❌ Failed to get models: {result['error']}"
                        return CallToolResult(
                            content=[TextContent(type="text", text=error_text)],
                            isError=True
                        )

                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True
                    )

            except Exception as e:
                logger.error(f"Tool call error: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )

# Create server instance
mcp_server = JimengMCPServer()

async def main():
    """Main entry point"""
    # Load environment variables from config/.env
    config_env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
    if os.path.exists(config_env_path):
        from dotenv import load_dotenv
        load_dotenv(config_env_path)
        logger.info(f"Loaded environment from {config_env_path}")

    logger.info("Starting Jimeng MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="jimeng-mcp",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())