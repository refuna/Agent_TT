#!/usr/bin/env python3
"""
Feishu MCP Server Startup Script
"""

import os
import sys
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
        print("✅ Environment variables loaded")
        return True
    else:
        print("❌ .env file not found")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import mcp
        import httpx
        print("✅ Dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def start_server():
    """Start the MCP server"""
    print("🚀 Starting Feishu MCP Server...")

    # Load environment
    if not load_env():
        return False

    # Check dependencies
    if not check_dependencies():
        print("Run: pip install mcp httpx")
        return False

    # Validate credentials
    if not os.getenv('FEISHU_APP_ID') or not os.getenv('FEISHU_APP_SECRET'):
        print("❌ Missing FEISHU_APP_ID or FEISHU_APP_SECRET in .env file")
        return False

    print(f"📱 App ID: {os.getenv('FEISHU_APP_ID')}")
    print("🔑 App Secret: [HIDDEN]")
    print("\n🎯 Server is ready to accept MCP connections")
    print("💡 Use this server in Claude Desktop or other MCP clients")
    print("\n" + "="*50)

    # Start the server
    try:
        from feishu_mcp_server import main
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

    return True

if __name__ == "__main__":
    success = start_server()
    sys.exit(0 if success else 1)