#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone starter for Jimeng MCP Server
"""

import os
import sys
import asyncio
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
config_env_path = current_dir / 'config' / '.env'
if config_env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(config_env_path)
    print(f"✅ Loaded environment from {config_env_path}")

# Import and run the server
from jimeng_mcp_server import main

if __name__ == "__main__":
    print("🚀 Starting Jimeng MCP Server...")
    asyncio.run(main())