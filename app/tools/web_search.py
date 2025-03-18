"""
Web Search Tool using Google Custom Search API.
"""

import os
from typing import Dict, Any, Optional

from googleapiclient.discovery import build
from langchain_core.tools import tool


class WebSearchTool:
    """Tool for performing web searches using Google Custom Search API."""

    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None, max_results: int = 5):
        """Initialize the web search tool."""

        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.search_engine_id = search_engine_id or os.environ.get(
            "SEARCH_ENGINE_ID"
        )
        self.max_results = max_results

        if not self.api_key:
            raise ValueError("Google API Key is required")
        if not self.search_engine_id:
            raise ValueError("Search engine ID is required")

        # Initialize the Custom Search API service
        self.service = build("customsearch", "v1", developerKey=self.api_key)

    def search(self, query: str) -> Dict[str, Any]:
        """Perform web search."""
        try:
            res = (
                self.service.cse()
                .list(q=query, cx=self.search_engine_id, num=self.max_results)
                .execute()
            )
            results = []

            if "items" not in res:
              return {
                "query": query,
                "results": results,
                "total_results": 0,
            }

            for item in res["items"]:
                results.append(
                    {
                        "title": item["title"],
                        "link": item["link"],
                        "snippet": item["snippet"],
                    }
                )

            return {
                "query": query,
                "results": results,
                "total_results": len(results),
            }
        except Exception as e:
            return {"error": f"Error during web search: {e}"}


@tool
def web_search(query: str) -> Dict[str, Any]:
    """
    Performs web search and returns current information from the internet.

    Use for finding recent information, news, facts, or data that might not be in training data.
    """
    try:
        search_tool = WebSearchTool()
        results = search_tool.search(query)

        if "error" in results:
            return {"status": "error", "message": results["error"], "results": []}

        formatted_results = []
        for result in results["results"]:
            formatted_results.append(
                {
                    "title": result.get("title", "No title"),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "No snippet available"),
                }
            )

        return {
            "status": "success",
            "query": query,
            "count": len(formatted_results),
            "results": formatted_results,
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "results": []}

