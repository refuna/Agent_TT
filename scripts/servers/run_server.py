#!/usr/bin/env python3
"""
Simplified server launcher
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run_server.py <server_name>")
        print("Available servers: feishu, news, weather, jimeng")
        sys.exit(1)

    server_name = sys.argv[1].lower()

    try:
        if server_name == "feishu":
            from servers.feishu_server import main as server_main
        elif server_name == "news":
            from servers.news_server import main as server_main
        elif server_name == "weather":
            from servers.weather_server import main as server_main
        elif server_name == "jimeng":
            from servers.jimeng_mcp_server import main as server_main
        else:
            print(f"Unknown server: {server_name}")
            sys.exit(1)

        print(f"Starting {server_name} MCP server...")
        asyncio.run(server_main())

    except KeyboardInterrupt:
        print(f"\n{server_name} server stopped by user")
    except Exception as e:
        print(f"Error starting {server_name} server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()