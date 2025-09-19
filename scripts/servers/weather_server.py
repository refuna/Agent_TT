#!/usr/bin/env python3
"""
Refactored Weather MCP Server
"""

import json
from typing import Dict, Any, List

import httpx
from mcp.types import CallToolResult, TextContent, Tool

from core.base_server import BaseMCPServer

class WeatherAPI:
    """Weather API client"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5" if api_key else None

    async def get_current_weather(self, location: str = "Shanghai") -> Dict[str, Any]:
        """Get current weather information"""
        if not self.api_key:
            return self._get_mock_weather()

        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "lang": "zh"
                }

                response = await client.get(f"{self.base_url}/weather", params=params)
                response.raise_for_status()
                return response.json()

        except Exception:
            return self._get_mock_weather()

    def _get_mock_weather(self) -> Dict[str, Any]:
        """Mock weather data"""
        return {
            "location": "上海",
            "current": {
                "temperature": 22,
                "feels_like": 24,
                "humidity": 65,
                "description": "多云",
                "wind_speed": 12
            }
        }

class WeatherMCPServer(BaseMCPServer):
    """Refactored Weather MCP Server"""

    def __init__(self):
        super().__init__("weather-mcp-server")

        # Initialize Weather API
        from utils.config import config_manager
        api_key = config_manager.get_env_var("OPENWEATHER_API_KEY")
        self.weather_api = WeatherAPI(api_key)

    def get_tools(self) -> List[Tool]:
        """Return list of weather tools"""
        return [
            Tool(
                name="get_current_weather",
                description="Get current weather information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location name",
                            "default": "Shanghai"
                        }
                    }
                }
            )
        ]

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls"""
        if name == "get_current_weather":
            return await self._get_current_weather(arguments)
        else:
            return self.create_error_result(f"Unknown tool: {name}")

    async def _get_current_weather(self, args: Dict[str, Any]) -> CallToolResult:
        """Get current weather implementation"""
        try:
            location = args.get("location", "Shanghai")
            weather_data = await self.weather_api.get_current_weather(location)

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(weather_data, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            return self.create_error_result(str(e))

async def main():
    """Main server entry point"""
    server = WeatherMCPServer()
    await server.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())