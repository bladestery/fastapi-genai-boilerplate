"""DuckDuckGo search tool for websearch."""

from typing import Any

from duckduckgo_search import DDGS
from langchain_core.tools import BaseTool
from loguru import logger
from pydantic import Field

from app import settings


class DuckDuckGoSearchTool(BaseTool):
    """DuckDuckGo search tool that mimics Tavily's interface."""

    name: str = "duckduckgo_search"
    description: str = "Search the web using DuckDuckGo"
    max_results: int = Field(default=10, description="Maximum number of search results")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._ddgs = DDGS()  # Initialize lazily

    #@property
    #def ddgs(self) -> DDGS:
    #    """Lazy initialization of DDGS instance."""
    #    if self._ddgs is None:
    #        self._ddgs = DDGS()
    #    return self._ddgs

    def _run(self, query: str) -> dict[str, Any] | None:
        """Execute DuckDuckGo search and return results in Tavily-compatible format."""
        try:
            logger.info(f"Performing DuckDuckGo search for: {query}")

            # Perform the search
            results = list(self.ddgs.text(query, max_results=self.max_results))

            # Transform results to match Tavily format
            formatted_results = []
            for result in results:
                formatted_result = {
                    "title": result.get("header", ""),
                    "link": result.get("link", ""),
                    "content": result.get("body", ""),
                    "source": "DuckDuckGo",
                }
                formatted_results.append(formatted_result)

            logger.info(
                f"DuckDuckGo search completed with {len(formatted_results)} results"
            )

            return {
                "results": formatted_results,
                "query": query,
                "source": "DuckDuckGo",
            }

        except Exception as e:
            logger.error(f"Error in DuckDuckGo search: {e}")
            return {
                "results": [],
                "query": query,
                "error": str(e),
                "source": "DuckDuckGo",
            }

    async def _arun(self, query: str) -> dict[str, Any] | None:
        """Async version of the search."""
        return self._run(query)


# Create the DuckDuckGo search tool instance
DUCKDUCKGO_SEARCH_TOOL: BaseTool = DuckDuckGoSearchTool(
    max_results=settings.DUCKDUCKGO_MAX_RESULTS
)
