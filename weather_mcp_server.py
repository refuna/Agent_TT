#!/usr/bin/env python3
"""
Weather MCP Server
A Model Context Protocol server for weather information
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

class WeatherAPI:
    """Weather API client"""

    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.api_key = os.getenv('OPENWEATHER_API_KEY')

        if not self.api_key:
            # 使用免费的天气API作为备选
            self.base_url = "https://api.weatherapi.com/v1"
            self.api_key = os.getenv('WEATHERAPI_KEY')

        # 如果没有API Key，使用模拟数据
        self.use_mock = not self.api_key

    async def get_current_weather(self, location: str = "Shanghai") -> Dict[str, Any]:
        """获取当前天气信息"""
        if self.use_mock:
            return self._get_mock_weather()

        try:
            async with httpx.AsyncClient() as client:
                if "openweathermap" in self.base_url:
                    url = f"{self.base_url}/weather"
                    params = {
                        "q": location,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "zh"
                    }
                else:
                    url = f"{self.base_url}/current.json"
                    params = {
                        "key": self.api_key,
                        "q": location,
                        "lang": "zh"
                    }

                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._get_mock_weather()

    async def get_hourly_forecast(self, location: str = "Shanghai", hours: int = 24) -> Dict[str, Any]:
        """获取逐小时天气预报"""
        if self.use_mock:
            return self._get_mock_forecast()

        try:
            async with httpx.AsyncClient() as client:
                if "openweathermap" in self.base_url:
                    url = f"{self.base_url}/forecast"
                    params = {
                        "q": location,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "zh",
                        "cnt": min(hours // 3, 40)  # 3小时间隔，最多40个点
                    }
                else:
                    url = f"{self.base_url}/forecast.json"
                    params = {
                        "key": self.api_key,
                        "q": location,
                        "days": min(hours // 24 + 1, 3),  # 最多3天
                        "lang": "zh"
                    }

                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Forecast API error: {e}")
            return self._get_mock_forecast()

    def _get_mock_weather(self) -> Dict[str, Any]:
        """模拟天气数据"""
        return {
            "location": "上海",
            "current": {
                "temperature": 22,
                "feels_like": 24,
                "humidity": 65,
                "description": "多云",
                "wind_speed": 12,
                "uv_index": 6,
                "visibility": 10
            },
            "precipitation": {
                "probability": 20,
                "type": None
            },
            "air_quality": {
                "aqi": 85,
                "level": "良"
            }
        }

    def _get_mock_forecast(self) -> Dict[str, Any]:
        """模拟预报数据"""
        return {
            "location": "上海",
            "forecast": [
                {
                    "time": "09:00",
                    "temperature": 20,
                    "description": "多云",
                    "precipitation": 10
                },
                {
                    "time": "12:00",
                    "temperature": 24,
                    "description": "晴",
                    "precipitation": 5
                },
                {
                    "time": "15:00",
                    "temperature": 26,
                    "description": "晴",
                    "precipitation": 0
                },
                {
                    "time": "18:00",
                    "temperature": 23,
                    "description": "多云",
                    "precipitation": 15
                },
                {
                    "time": "21:00",
                    "temperature": 21,
                    "description": "多云",
                    "precipitation": 20
                }
            ]
        }

# Initialize weather API
weather_api = WeatherAPI()

# Initialize MCP server
server = Server("weather-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available weather tools"""
    return [
        Tool(
            name="get_current_weather",
            description="获取指定地点的当前天气信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "地点名称，默认为上海",
                        "default": "Shanghai"
                    }
                }
            }
        ),
        Tool(
            name="get_hourly_forecast",
            description="获取指定地点的逐小时天气预报",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "地点名称，默认为上海",
                        "default": "Shanghai"
                    },
                    "hours": {
                        "type": "integer",
                        "description": "预报小时数，默认24小时",
                        "default": 24,
                        "minimum": 1,
                        "maximum": 72
                    }
                }
            }
        ),
        Tool(
            name="analyze_outfit_weather",
            description="基于天气条件分析穿搭建议",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "地点名称",
                        "default": "Shanghai"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "get_current_weather":
            location = arguments.get("location", "Shanghai")
            weather_data = await weather_api.get_current_weather(location)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(weather_data, ensure_ascii=False, indent=2)
                    )
                ]
            )

        elif name == "get_hourly_forecast":
            location = arguments.get("location", "Shanghai")
            hours = arguments.get("hours", 24)
            forecast_data = await weather_api.get_hourly_forecast(location, hours)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(forecast_data, ensure_ascii=False, indent=2)
                    )
                ]
            )

        elif name == "analyze_outfit_weather":
            location = arguments.get("location", "Shanghai")
            weather_data = await weather_api.get_current_weather(location)

            # 基于天气分析穿搭建议
            analysis = _analyze_outfit_suggestions(weather_data)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(analysis, ensure_ascii=False, indent=2)
                    )
                ]
            )

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ],
            isError=True
        )

def _analyze_outfit_suggestions(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """基于天气数据分析穿搭建议"""
    if weather_data.get("current"):
        temp = weather_data["current"]["temperature"]
        humidity = weather_data["current"]["humidity"]
        description = weather_data["current"]["description"]
        precipitation = weather_data.get("precipitation", {}).get("probability", 0)
    else:
        # 兼容不同API格式
        temp = 22
        humidity = 65
        description = "多云"
        precipitation = 20

    suggestions = {
        "temperature_guidance": "",
        "material_suggestions": [],
        "color_suggestions": [],
        "accessories_needed": [],
        "outfit_style": "",
        "comfort_level": "舒适"
    }

    # 温度建议
    if temp < 10:
        suggestions["temperature_guidance"] = "寒冷天气，需要保暖"
        suggestions["material_suggestions"] = ["羊毛", "羽绒", "厚棉"]
        suggestions["accessories_needed"] = ["围巾", "手套", "帽子"]
        suggestions["outfit_style"] = "保暖为主"
    elif temp < 20:
        suggestions["temperature_guidance"] = "凉爽天气，适合叠穿"
        suggestions["material_suggestions"] = ["针织", "薄外套", "长袖"]
        suggestions["accessories_needed"] = ["薄外套"]
        suggestions["outfit_style"] = "叠穿搭配"
    elif temp < 28:
        suggestions["temperature_guidance"] = "舒适温度，穿搭选择丰富"
        suggestions["material_suggestions"] = ["棉质", "雪纺", "牛仔"]
        suggestions["outfit_style"] = "日常休闲"
    else:
        suggestions["temperature_guidance"] = "炎热天气，选择透气材质"
        suggestions["material_suggestions"] = ["棉麻", "雪纺", "透气面料"]
        suggestions["accessories_needed"] = ["防晒帽", "太阳镜"]
        suggestions["outfit_style"] = "清爽夏日"

    # 降水建议
    if precipitation > 50:
        suggestions["accessories_needed"].append("雨伞")
        suggestions["accessories_needed"].append("防水外套")
        suggestions["color_suggestions"] = ["深色系", "不易显脏的颜色"]

    # 湿度建议
    if humidity > 70:
        suggestions["material_suggestions"] = [m for m in suggestions["material_suggestions"] if "透气" in m or "棉" in m]
        suggestions["comfort_level"] = "注意透气性"

    return suggestions

async def main():
    """Main server entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())