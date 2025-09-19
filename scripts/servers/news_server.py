#!/usr/bin/env python3
"""
Refactored News MCP Server
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List

import httpx
from mcp.types import CallToolResult, TextContent, Tool

from core.base_server import BaseMCPServer

class NewsAPI:
    """News API client"""

    def __init__(self, newsapi_key: str = None):
        self.newsapi_key = newsapi_key
        self.base_url = "https://newsapi.org/v2"

    async def fetch_ai_news(self, limit: int = 10, language: str = "zh") -> List[Dict[str, Any]]:
        """Fetch AI-related news"""
        if not self.newsapi_key:
            return await self._fetch_rss_news(limit)

        keywords = "AI OR 人工智能 OR GPT OR Claude"

        async with httpx.AsyncClient() as client:
            params = {
                "q": keywords,
                "language": language,
                "sortBy": "publishedAt",
                "pageSize": limit,
                "apiKey": self.newsapi_key
            }

            try:
                response = await client.get(f"{self.base_url}/everything", params=params)
                data = response.json()

                if data.get("status") == "ok":
                    return [
                        {
                            "title": article["title"],
                            "description": article["description"] or "",
                            "url": article["url"],
                            "source": article["source"]["name"],
                            "published_at": article["publishedAt"]
                        }
                        for article in data.get("articles", [])
                    ]
                else:
                    return await self._fetch_rss_news(limit)
            except Exception:
                return await self._fetch_rss_news(limit)

    async def _fetch_rss_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fallback: Fetch news from RSS feeds"""
        # Simplified RSS sources
        rss_sources = [
            {"name": "AI新闻", "rss": "https://feeds.feedburner.com/oreilly/radar"},
            {"name": "科技资讯", "rss": "https://feeds.feedburner.com/venturebeat/SZYF"}
        ]

        articles = []
        async with httpx.AsyncClient() as client:
            for source in rss_sources[:2]:
                try:
                    response = await client.get(source["rss"], timeout=10)
                    root = ET.fromstring(response.text)

                    for item in root.findall(".//item")[:limit//2]:
                        title = item.find("title")
                        description = item.find("description")
                        link = item.find("link")

                        if title is not None and link is not None:
                            articles.append({
                                "title": title.text or "",
                                "description": description.text[:200] + "..." if description is not None else "",
                                "url": link.text or "",
                                "source": source["name"],
                                "published_at": ""
                            })
                except Exception:
                    continue

        return articles[:limit]

class NewsMCPServer(BaseMCPServer):
    """Refactored News MCP Server"""

    def __init__(self):
        super().__init__("news-mcp-server")

        # Initialize News API
        from utils.config import config_manager
        newsapi_key = config_manager.get_env_var("NEWSAPI_KEY")
        self.news_api = NewsAPI(newsapi_key)

    def get_tools(self) -> List[Tool]:
        """Return list of news tools"""
        return [
            Tool(
                name="fetch_ai_news",
                description="Fetch latest AI news from various sources",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "number", "description": "Number of articles", "default": 10},
                        "language": {"type": "string", "description": "Language preference", "default": "zh"}
                    },
                    "required": []
                }
            ),
            Tool(
                name="summarize_articles",
                description="Summarize news articles",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "articles": {
                            "type": "array",
                            "description": "Articles to summarize",
                            "items": {"type": "object"}
                        },
                        "max_length": {"type": "number", "description": "Max summary length", "default": 200}
                    },
                    "required": ["articles"]
                }
            )
        ]

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls"""
        if name == "fetch_ai_news":
            return await self._fetch_ai_news(arguments)
        elif name == "summarize_articles":
            return await self._summarize_articles(arguments)
        else:
            return self.create_error_result(f"Unknown tool: {name}")

    async def _fetch_ai_news(self, args: Dict[str, Any]) -> CallToolResult:
        """Fetch AI news implementation"""
        try:
            limit = args.get("limit", 10)
            language = args.get("language", "zh")

            articles = await self.news_api.fetch_ai_news(limit, language)

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(articles, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            return self.create_error_result(str(e))

    async def _summarize_articles(self, args: Dict[str, Any]) -> CallToolResult:
        """Summarize articles implementation"""
        try:
            articles = args["articles"]
            max_length = args.get("max_length", 200)

            summarized = []
            for article in articles:
                description = article.get("description", "")
                sentences = description.split("。")
                summary = sentences[0][:max_length] + "..." if len(sentences[0]) > max_length else sentences[0]

                summarized.append({
                    **article,
                    "summary": summary if summary else article.get("title", "")[:max_length]
                })

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(summarized, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            return self.create_error_result(str(e))

async def main():
    """Main server entry point"""
    server = NewsMCPServer()
    await server.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())