#!/usr/bin/env python3
"""
Refactored Feishu MCP Server
"""

import json
from typing import Dict, Any, List
from datetime import datetime

import httpx
from mcp.types import CallToolResult, TextContent, Tool

from core.base_server import BaseMCPServer

class FeishuAPI:
    """Feishu API client"""

    def __init__(self, app_id: str, app_secret: str):
        self.base_url = "https://open.feishu.cn/open-apis"
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = None

    async def get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and self.token_expires_at:
            import time
            if time.time() < self.token_expires_at - 300:
                return self.access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/v3/tenant_access_token/internal",
                json={"app_id": self.app_id, "app_secret": self.app_secret}
            )

            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"Failed to get access token: {result.get('msg')}")

            self.access_token = result["tenant_access_token"]
            self.token_expires_at = result.get("expire", 0) + int(datetime.now().timestamp())

            return self.access_token

    async def send_message(self, receive_id: str, content: str, msg_type: str = "text") -> Dict[str, Any]:
        """Send message to Feishu"""
        token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        message_content = {"text": content} if msg_type == "text" else json.loads(content)

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
                params={"receive_id_type": "chat_id"}
            )

            return response.json()

class FeishuMCPServer(BaseMCPServer):
    """Refactored Feishu MCP Server"""

    def __init__(self):
        super().__init__("feishu-mcp-server")

        # Validate required environment variables
        if not self.validate_required_env_vars(["FEISHU_APP_ID", "FEISHU_APP_SECRET"]):
            raise ValueError("Missing required Feishu credentials")

        # Initialize Feishu API
        from utils.config import config_manager
        app_id = config_manager.get_env_var("FEISHU_APP_ID")
        app_secret = config_manager.get_env_var("FEISHU_APP_SECRET")
        self.feishu = FeishuAPI(app_id, app_secret)

    def get_tools(self) -> List[Tool]:
        """Return list of Feishu tools"""
        return [
            Tool(
                name="send_feishu_message",
                description="Send a message to Feishu chat/group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "receive_id": {"type": "string", "description": "Chat ID"},
                        "message": {"type": "string", "description": "Message content"},
                        "message_type": {"type": "string", "enum": ["text", "rich_text"], "default": "text"}
                    },
                    "required": ["receive_id", "message"]
                }
            ),
            Tool(
                name="send_news_summary",
                description="Send formatted news summary to group",
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

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls"""
        if name == "send_feishu_message":
            return await self._send_message(arguments)
        elif name == "send_news_summary":
            return await self._send_news_summary(arguments)
        else:
            return self.create_error_result(f"Unknown tool: {name}")

    async def _send_message(self, args: Dict[str, Any]) -> CallToolResult:
        """Send message implementation"""
        try:
            receive_id = args["receive_id"]
            message = args["message"]
            msg_type = args.get("message_type", "text")

            result = await self.feishu.send_message(receive_id, message, msg_type)

            if result.get("code") == 0:
                return self.create_success_result(
                    f"Message sent successfully. Message ID: {result.get('data', {}).get('message_id')}"
                )
            else:
                return self.create_error_result(f"Failed to send message: {result.get('msg')}")

        except Exception as e:
            return self.create_error_result(str(e))

    async def _send_news_summary(self, args: Dict[str, Any]) -> CallToolResult:
        """Send formatted news summary"""
        try:
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

            result = await self.feishu.send_message(group_id, summary_text)

            if result.get("code") == 0:
                return self.create_success_result("News summary sent successfully")
            else:
                return self.create_error_result(f"Failed to send news summary: {result.get('msg')}")

        except Exception as e:
            return self.create_error_result(str(e))

async def main():
    """Main server entry point"""
    server = FeishuMCPServer()
    await server.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())