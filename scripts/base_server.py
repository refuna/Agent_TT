#!/usr/bin/env python3
"""
Base MCP Server class with common functionality
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

from utils.config import config_manager
from utils.logging_setup import setup_logging

class BaseMCPServer(ABC):
    """Base class for MCP servers with common functionality"""

    def __init__(self, server_name: str, version: str = "1.0.0"):
        self.server_name = server_name
        self.version = version
        self.server = Server(server_name)
        self.logger = setup_logging(server_name=server_name)

        # Load configuration
        config_manager.load_env()

        # Setup handlers
        self.setup_handlers()

    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """Return list of tools provided by this server"""
        pass

    @abstractmethod
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls"""
        pass

    def setup_handlers(self):
        """Setup MCP server handlers"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return self.get_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            try:
                return await self.handle_tool_call(name, arguments)
            except Exception as e:
                self.logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )

    def validate_required_env_vars(self, required_vars: List[str]) -> bool:
        """Validate required environment variables"""
        return config_manager.validate_required_env_vars(required_vars)

    async def run(self):
        """Run the MCP server"""
        self.logger.info(f"Starting {self.server_name} v{self.version}")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.server_name,
                    server_version=self.version,
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )

    def create_success_result(self, message: str) -> CallToolResult:
        """Create a successful tool result"""
        return CallToolResult(
            content=[TextContent(type="text", text=message)]
        )

    def create_error_result(self, error_message: str) -> CallToolResult:
        """Create an error tool result"""
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {error_message}")],
            isError=True
        )