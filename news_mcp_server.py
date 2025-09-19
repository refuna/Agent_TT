#!/usr/bin/env python3
"""
News MCP Server
A Model Context Protocol server for news aggregation and processing
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

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

class NewsAPI:
    """News API client for fetching news"""

    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.base_url = "https://newsapi.org/v2"

        if not self.newsapi_key:
            logger.warning("NEWSAPI_KEY not found, some features may not work")

    async def fetch_ai_news(self, limit: int = 10, language: str = "zh") -> List[Dict[str, Any]]:
        """Fetch AI-related news from NewsAPI"""
        if not self.newsapi_key:
            return await self._fetch_rss_news(limit)

        keywords = "AI OR 人工智能 OR GPT OR Claude OR 大语言模型"

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
                            "published_at": article["publishedAt"],
                            "image_url": article.get("urlToImage")
                        }
                        for article in data.get("articles", [])
                    ]
                else:
                    logger.error(f"NewsAPI error: {data.get('message')}")
                    return await self._fetch_rss_news(limit)
            except Exception as e:
                logger.error(f"Error fetching news: {e}")
                return await self._fetch_rss_news(limit)

    async def _fetch_rss_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fallback: Fetch news from RSS feeds"""
        news_sources = self._load_news_sources()
        articles = []

        async with httpx.AsyncClient() as client:
            for source in news_sources.get("ai_news_sources", {}).get("domestic", [])[:3]:
                if "rss" not in source:
                    continue

                try:
                    response = await client.get(source["rss"], timeout=10)
                    root = ET.fromstring(response.text)

                    for item in root.findall(".//item")[:limit//3]:
                        title = item.find("title")
                        description = item.find("description")
                        link = item.find("link")
                        pub_date = item.find("pubDate")

                        if title is not None and link is not None:
                            articles.append({
                                "title": title.text or "",
                                "description": description.text[:200] + "..." if description is not None and description.text else "",
                                "url": link.text or "",
                                "source": source["name"],
                                "published_at": pub_date.text if pub_date is not None else "",
                                "image_url": None
                            })
                except Exception as e:
                    logger.error(f"Error fetching RSS from {source['name']}: {e}")
                    continue

        return articles[:limit]

    def _load_news_sources(self) -> Dict[str, Any]:
        """Load news sources from configuration"""
        try:
            with open("resources/news_sources.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading news sources: {e}")
            return {"ai_news_sources": {"domestic": [], "international": []}}

    async def summarize_news(self, articles: List[Dict[str, Any]], max_length: int = 200) -> List[Dict[str, Any]]:
        """Summarize news articles (simple version)"""
        summarized = []

        for article in articles:
            # Simple summarization - take first sentence of description
            description = article.get("description", "")
            sentences = description.split("。")
            summary = sentences[0][:max_length] + "..." if len(sentences[0]) > max_length else sentences[0]

            summarized.append({
                **article,
                "summary": summary if summary else article.get("title", "")[:max_length]
            })

        return summarized

class NewsMCPServer:
    """MCP Server for news aggregation"""

    def __init__(self):
        self.news_api = NewsAPI()
        self.server = Server("news-mcp-server")
        self.setup_tools()

    def setup_tools(self):
        """Setup MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="fetch_ai_news",
                    description="Fetch latest AI news from various sources",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "number", "description": "Number of articles to fetch", "default": 10},
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
                                "description": "Array of news articles to summarize",
                                "items": {"type": "object"}
                            },
                            "max_length": {"type": "number", "description": "Maximum summary length", "default": 200}
                        },
                        "required": ["articles"]
                    }
                ),
                Tool(
                    name="filter_news_by_keywords",
                    description="Filter news articles by keywords",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "articles": {
                                "type": "array",
                                "description": "Array of news articles to filter",
                                "items": {"type": "object"}
                            },
                            "keywords": {
                                "type": "array",
                                "description": "Keywords to filter by",
                                "items": {"type": "string"}
                            },
                            "exclude_keywords": {
                                "type": "array",
                                "description": "Keywords to exclude",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["articles", "keywords"]
                    }
                ),
                Tool(
                    name="get_news_sources",
                    description="Get configured news sources",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            try:
                if name == "fetch_ai_news":
                    return await self._fetch_ai_news(arguments)
                elif name == "summarize_articles":
                    return await self._summarize_articles(arguments)
                elif name == "filter_news_by_keywords":
                    return await self._filter_news(arguments)
                elif name == "get_news_sources":
                    return await self._get_news_sources(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

    async def _fetch_ai_news(self, args: Dict[str, Any]) -> CallToolResult:
        """Fetch AI news implementation"""
        limit = args.get("limit", 10)
        language = args.get("language", "zh")

        articles = await self.news_api.fetch_ai_news(limit, language)

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(articles, ensure_ascii=False, indent=2))]
        )

    async def _summarize_articles(self, args: Dict[str, Any]) -> CallToolResult:
        """Summarize articles implementation"""
        articles = args["articles"]
        max_length = args.get("max_length", 200)

        summarized = await self.news_api.summarize_news(articles, max_length)

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(summarized, ensure_ascii=False, indent=2))]
        )

    async def _filter_news(self, args: Dict[str, Any]) -> CallToolResult:
        """Filter news implementation"""
        articles = args["articles"]
        keywords = [k.lower() for k in args["keywords"]]
        exclude_keywords = [k.lower() for k in args.get("exclude_keywords", [])]

        filtered = []
        for article in articles:
            title_desc = (article.get("title", "") + " " + article.get("description", "")).lower()

            # Check if any keyword is present
            has_keyword = any(keyword in title_desc for keyword in keywords)

            # Check if any exclude keyword is present
            has_exclude = any(keyword in title_desc for keyword in exclude_keywords)

            if has_keyword and not has_exclude:
                filtered.append(article)

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(filtered, ensure_ascii=False, indent=2))]
        )

    async def _get_news_sources(self, args: Dict[str, Any]) -> CallToolResult:
        """Get news sources implementation"""
        sources = self.news_api._load_news_sources()

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(sources, ensure_ascii=False, indent=2))]
        )

def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join("config", ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

async def main():
    """Main server entry point"""
    # Load environment variables
    load_env()

    # Initialize server
    server_instance = NewsMCPServer()

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="news-mcp-server",
                server_version="1.0.0"
            )
        )

if __name__ == "__main__":
    asyncio.run(main())