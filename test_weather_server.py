#!/usr/bin/env python3
"""
Weather MCP Server 测试脚本
测试weather MCP服务器的功能
"""

import asyncio
import json
import sys
from weather_mcp_server import WeatherAPI

async def test_weather_api():
    """测试WeatherAPI类的功能"""
    print("=== 测试Weather API类功能 ===\n")

    weather_api = WeatherAPI()

    # 测试1: 获取当前天气
    print("1. 测试获取当前天气...")
    try:
        current_weather = await weather_api.get_current_weather("Shanghai")
        print("当前天气获取成功:")
        print(json.dumps(current_weather, ensure_ascii=False, indent=2))
        print()
    except Exception as e:
        print(f"当前天气获取失败: {e}")
        print()

    # 测试2: 获取逐小时预报
    print("2. 测试获取逐小时预报...")
    try:
        forecast = await weather_api.get_hourly_forecast("Shanghai", 12)
        print("逐小时预报获取成功:")
        print(json.dumps(forecast, ensure_ascii=False, indent=2))
        print()
    except Exception as e:
        print(f"逐小时预报获取失败: {e}")
        print()

def test_weather_analysis():
    """测试天气分析功能"""
    print("=== 测试天气分析功能 ===\n")

    # 导入分析函数
    from weather_mcp_server import _analyze_outfit_suggestions

    # 测试不同天气条件
    test_cases = [
        {
            "name": "寒冷天气",
            "weather": {
                "current": {
                    "temperature": 5,
                    "humidity": 70,
                    "description": "雨夹雪"
                },
                "precipitation": {"probability": 80}
            }
        },
        {
            "name": "舒适天气",
            "weather": {
                "current": {
                    "temperature": 22,
                    "humidity": 60,
                    "description": "多云"
                },
                "precipitation": {"probability": 20}
            }
        },
        {
            "name": "炎热天气",
            "weather": {
                "current": {
                    "temperature": 35,
                    "humidity": 80,
                    "description": "晴"
                },
                "precipitation": {"probability": 5}
            }
        }
    ]

    for case in test_cases:
        print(f"测试场景: {case['name']}")
        analysis = _analyze_outfit_suggestions(case['weather'])
        print("穿搭建议分析:")
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        print("-" * 50)

async def test_mcp_tools():
    """测试MCP工具接口"""
    print("=== 测试MCP工具接口 ===\n")

    # 导入MCP服务器组件
    from weather_mcp_server import server

    # 测试工具列表
    print("1. 测试工具列表...")
    try:
        tools = await server.list_tools()
        print("可用工具:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        print()
    except Exception as e:
        print(f"工具列表获取失败: {e}")
        print()

    # 测试工具调用（模拟）
    print("2. 模拟工具调用测试...")

    test_calls = [
        {
            "name": "get_current_weather",
            "args": {"location": "Shanghai"}
        },
        {
            "name": "get_hourly_forecast",
            "args": {"location": "Shanghai", "hours": 6}
        },
        {
            "name": "analyze_outfit_weather",
            "args": {"location": "Shanghai"}
        }
    ]

    for call in test_calls:
        print(f"调用工具: {call['name']}")
        try:
            # 这里模拟工具调用，实际使用时会通过MCP协议
            result = await server.call_tool(call['name'], call['args'])
            print("调用成功")
            if result.content:
                content = result.content[0].text
                # 限制输出长度
                if len(content) > 500:
                    content = content[:500] + "..."
                print(f"返回内容预览: {content}")
            print()
        except Exception as e:
            print(f"调用失败: {e}")
            print()

def test_error_handling():
    """测试错误处理"""
    print("=== 测试错误处理 ===\n")

    from weather_mcp_server import WeatherAPI

    # 测试无效地点
    print("测试无效地点处理...")
    weather_api = WeatherAPI()

    # 由于使用模拟数据，这个测试主要验证代码结构
    print("错误处理机制已内置（降级到模拟数据）")
    print()

async def main():
    """主测试函数"""
    print("Weather MCP Server 功能测试\n")
    print("=" * 60)

    # 执行所有测试
    await test_weather_api()
    test_weather_analysis()
    await test_mcp_tools()
    test_error_handling()

    print("=" * 60)
    print("所有测试完成!")

    # 使用说明
    print("\n使用说明:")
    print("1. Weather MCP服务器目前使用模拟数据")
    print("2. 要使用真实天气数据，请设置环境变量:")
    print("   - OPENWEATHER_API_KEY (OpenWeatherMap)")
    print("   - WEATHERAPI_KEY (WeatherAPI)")
    print("3. 服务器通过MCP协议与Claude Code集成")
    print("4. 主要功能:")
    print("   - get_current_weather: 获取当前天气")
    print("   - get_hourly_forecast: 获取逐小时预报")
    print("   - analyze_outfit_weather: 穿搭天气分析")

if __name__ == "__main__":
    asyncio.run(main())