#!/usr/bin/env python3
"""
Feishu MCP Server
A Model Context Protocol server for Feishu integration
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
from mcp.server.models import NotificationOptions, ExperimentalCapabilities

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeishuAPI:
    """Feishu API client"""

    def __init__(self):
        self.base_url = "https://open.feishu.cn/open-apis"
        self.app_id = os.getenv('FEISHU_APP_ID')
        self.app_secret = os.getenv('FEISHU_APP_SECRET')
        self.access_token = None
        self.token_expires_at = None

        if not self.app_id or not self.app_secret:
            raise ValueError("FEISHU_APP_ID and FEISHU_APP_SECRET must be set")

    async def get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and self.token_expires_at:
            # Check if token is still valid (with 5 min buffer)
            import time
            if time.time() < self.token_expires_at - 300:
                return self.access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret
                }
            )

            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"Failed to get access token: {result.get('msg')}")

            self.access_token = result["tenant_access_token"]
            self.token_expires_at = result.get("expire", 0) + int(datetime.now().timestamp())

            return self.access_token

    async def send_message(self, receive_id: str, msg_type: str, content: str, receive_id_type: str = "chat_id") -> Dict[str, Any]:
        """Send message to Feishu"""
        token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Prepare content based on message type
        if msg_type == "text":
            message_content = {"text": content}
        elif msg_type == "rich_text":
            message_content = json.loads(content) if isinstance(content, str) else content
        else:
            message_content = {"text": content}  # fallback

        payload = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": json.dumps(message_content)
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/im/v1/messages",
                headers=headers,
                json=payload,
                params={"receive_id_type": receive_id_type}
            )

            return response.json()

    async def create_document(self, title: str, content: str, folder_token: Optional[str] = None) -> Dict[str, Any]:
        """Create a Feishu document"""
        token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "title": title
        }

        if folder_token:
            payload["folder_token"] = folder_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/docx/v1/documents",
                headers=headers,
                json=payload
            )

            result = response.json()
            if result.get("code") != 0:
                return result

            # Add content to document if provided
            document_id = result["data"]["document"]["document_id"]
            if content:
                await self.add_content_to_document(document_id, content)

            return result

    async def add_content_to_document(self, document_id: str, content: str) -> Dict[str, Any]:
        """Add content to an existing document"""
        token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Simple text block
        payload = {
            "requests": [
                {
                    "insert_text": {
                        "location": {
                            "zone_id": "",
                            "index": 0
                        },
                        "elements": [
                            {
                                "text_run": {
                                    "text": content
                                }
                            }
                        ]
                    }
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/docx/v1/documents/{document_id}/blocks",
                headers=headers,
                json=payload
            )

            return response.json()

    async def get_chat_list(self) -> Dict[str, Any]:
        """Get list of chats/groups"""
        token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/im/v1/chats",
                headers=headers
            )

            return response.json()

class FeishuMCPServer:
    """MCP Server for Feishu integration"""

    def __init__(self):
        self.feishu = FeishuAPI()
        self.server = Server("feishu-mcp-server")
        self.setup_tools()

    def setup_tools(self):
        """Setup MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="send_feishu_message",
                    description="Send a message to Feishu chat/group",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "receive_id": {"type": "string", "description": "Chat ID or user ID"},
                            "message": {"type": "string", "description": "Message content"},
                            "message_type": {"type": "string", "enum": ["text", "rich_text"], "default": "text"},
                            "receive_id_type": {"type": "string", "enum": ["chat_id", "user_id", "email"], "default": "chat_id"}
                        },
                        "required": ["receive_id", "message"]
                    }
                ),
                Tool(
                    name="create_feishu_document",
                    description="Create a new Feishu document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Document title"},
                            "content": {"type": "string", "description": "Document content"},
                            "folder_token": {"type": "string", "description": "Optional folder token to place document in"}
                        },
                        "required": ["title"]
                    }
                ),
                Tool(
                    name="get_feishu_chats",
                    description="Get list of available Feishu chats/groups",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="send_news_summary",
                    description="Send formatted news summary to specified group",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "group_id": {"type": "string", "description": "Target group chat ID"},
                            "news_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "summary": {"type": "string"},
                                        "url": {"type": "string"},
                                        "source": {"type": "string"}
                                    }
                                }
                            },
                            "date": {"type": "string", "description": "Date for the news summary"}
                        },
                        "required": ["group_id", "news_items"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            try:
                if name == "send_feishu_message":
                    return await self._send_message(arguments)
                elif name == "create_feishu_document":
                    return await self._create_document(arguments)
                elif name == "get_feishu_chats":
                    return await self._get_chats(arguments)
                elif name == "send_news_summary":
                    return await self._send_news_summary(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

    async def _send_message(self, args: Dict[str, Any]) -> CallToolResult:
        """Send message tool implementation"""
        receive_id = args["receive_id"]
        message = args["message"]
        msg_type = args.get("message_type", "text")
        receive_id_type = args.get("receive_id_type", "chat_id")

        result = await self.feishu.send_message(receive_id, msg_type, message, receive_id_type)

        if result.get("code") == 0:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Message sent successfully. Message ID: {result.get('data', {}).get('message_id')}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to send message: {result.get('msg')}")]
            )

    async def _create_document(self, args: Dict[str, Any]) -> CallToolResult:
        """Create document tool implementation"""
        title = args["title"]
        content = args.get("content", "")
        folder_token = args.get("folder_token")

        result = await self.feishu.create_document(title, content, folder_token)

        if result.get("code") == 0:
            doc_url = result["data"]["document"]["url"]
            return CallToolResult(
                content=[TextContent(type="text", text=f"Document created successfully: {doc_url}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to create document: {result.get('msg')}")]
            )

    async def _get_chats(self, args: Dict[str, Any]) -> CallToolResult:
        """Get chats tool implementation"""
        result = await self.feishu.get_chat_list()

        if result.get("code") == 0:
            chats = result.get("data", {}).get("items", [])
            chat_info = []
            for chat in chats:
                chat_info.append(f"- {chat.get('name', 'Unknown')} (ID: {chat.get('chat_id')})")

            return CallToolResult(
                content=[TextContent(type="text", text=f"Available chats:\n" + "\n".join(chat_info))]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get chats: {result.get('msg')}")]
            )

    async def _send_news_summary(self, args: Dict[str, Any]) -> CallToolResult:
        """Send formatted news summary"""
        group_id = args["group_id"]
        news_items = args["news_items"]
        date = args.get("date", datetime.now().strftime("%Y-%m-%d"))

        # Format news summary
        summary_text = f"📰 AI新闻简报 - {date}\n\n"

        for i, item in enumerate(news_items, 1):
            summary_text += f"{i}. **{item.get('title', 'No title')}**\n"
            summary_text += f"   {item.get('summary', 'No summary')}\n"
            if item.get('source'):
                summary_text += f"   来源: {item['source']}\n"
            if item.get('url'):
                summary_text += f"   链接: {item['url']}\n"
            summary_text += "\n"

        result = await self.feishu.send_message(group_id, "text", summary_text)

        if result.get("code") == 0:
            return CallToolResult(
                content=[TextContent(type="text", text=f"News summary sent successfully")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to send news summary: {result.get('msg')}")]
            )

def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join("config", ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

async def main():
    """Main server entry point"""
    # Load environment variables
    load_env()

    # Initialize server
    server_instance = FeishuMCPServer()

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="feishu-mcp-server",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities=ExperimentalCapabilities()
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())