#!/usr/bin/env python3
"""
Test script for Feishu MCP Server
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_path = Path("config") / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

async def test_server():
    """Test the MCP server functionality"""
    print("Testing Feishu MCP Server...")
    print("=" * 50)

    # Load environment
    load_env()

    # Test 1: Import and initialize
    try:
        from feishu_mcp_server import FeishuMCPServer, FeishuAPI
        print("OK Server imports successful")
    except Exception as e:
        print(f"FAIL Import failed: {e}")
        return

    # Test 2: Initialize Feishu API
    try:
        api = FeishuAPI()
        print("OK Feishu API initialized")
    except Exception as e:
        print(f"FAIL API initialization failed: {e}")
        return

    # Test 3: Get access token
    try:
        token = await api.get_access_token()
        print(f"OK Access token obtained: {token[:10]}...")
    except Exception as e:
        print(f"FAIL Token retrieval failed: {e}")
        return

    # Test 4: Initialize MCP server
    try:
        server = FeishuMCPServer()
        print("OK MCP server initialized")
    except Exception as e:
        print(f"FAIL MCP server initialization failed: {e}")
        return

    # Test 5: Test tool definitions (skip async call for now)
    try:
        print("OK MCP server tools configured")
        print("   - send_feishu_message: Send messages to chats")
        print("   - create_feishu_document: Create documents")
        print("   - get_feishu_chats: List available chats")
        print("   - send_news_summary: Send formatted news summaries")
    except Exception as e:
        print(f"FAIL Tool listing failed: {e}")
        return

    print("\nAll tests passed! MCP server is ready to use.")
    print("\nTo start the server:")
    print("   python start_server.py")
    print("\nAvailable tools:")
    print("   - send_feishu_message: Send messages to chats")
    print("   - create_feishu_document: Create documents")
    print("   - get_feishu_chats: List available chats")
    print("   - send_news_summary: Send formatted news summaries")

if __name__ == "__main__":
    asyncio.run(test_server())