#!/usr/bin/env python3
"""
Consolidated test script for all MCP servers
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import config_manager

async def test_feishu_server():
    """Test Feishu MCP server"""
    print("Testing Feishu MCP Server...")
    try:
        from servers.feishu_server import FeishuMCPServer
        if not config_manager.validate_required_env_vars(["FEISHU_APP_ID", "FEISHU_APP_SECRET"]):
            print("SKIP - Missing Feishu credentials")
            return

        server = FeishuMCPServer()
        tools = server.get_tools()
        print(f"OK - {len(tools)} tools available")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"FAIL - {e}")

async def test_news_server():
    """Test News MCP server"""
    print("Testing News MCP Server...")
    try:
        from servers.news_server import NewsMCPServer
        server = NewsMCPServer()
        tools = server.get_tools()
        print(f"OK - {len(tools)} tools available")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"FAIL - {e}")

async def test_weather_server():
    """Test Weather MCP server"""
    print("Testing Weather MCP Server...")
    try:
        from servers.weather_server import WeatherMCPServer
        server = WeatherMCPServer()
        tools = server.get_tools()
        print(f"OK - {len(tools)} tools available")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"FAIL - {e}")

async def test_jimeng_server():
    """Test Jimeng MCP server"""
    print("Testing Jimeng MCP Server...")
    try:
        from servers.jimeng_mcp_server import JimengMCPServer
        if not config_manager.validate_required_env_vars(["JIMENG_API_KEY"]):
            print("SKIP - Missing Jimeng API key")
            return

        server = JimengMCPServer()
        print("OK - Server initialized")
    except Exception as e:
        print(f"FAIL - {e}")

async def main():
    """Run all tests"""
    print("MCP Servers Test Suite")
    print("=" * 50)

    # Load environment
    config_manager.load_env()

    # Test all servers
    await test_feishu_server()
    print()
    await test_news_server()
    print()
    await test_weather_server()
    print()
    await test_jimeng_server()

    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(main())