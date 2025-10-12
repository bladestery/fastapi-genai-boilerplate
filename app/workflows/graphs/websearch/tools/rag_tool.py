"""Rag tool to match search format form saerch tool"""

from typing import Any

from langchain_core.tools import BaseTool
from loguru import logger
from pydantic import Field

from app import settings

class RagTool(BaseTool):
    """Rag tool that mimics Tavily's interface."""

    name: str = "rag_search"
    description: str = "Search vectordb"
    max_results: int = Field(default=10, description="Maximum number of search results")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._rag = rag_service()

    def _run(self, query: str) -> dict[str, Any] | None:
        """Execute Rag search and return results."""
        try:
            logger.info(f"Performing Rag search for: {query}")

            # Perform the search
            results = list(self.rag.text(query, max_results=self.max_results))

            # Transform results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "book": result.get("book", "") ,
                    "page": result.get("page", "") ,
                    "content": result.get("content", "") ,
                    "header": result.get("header", "") ,
                    "footnote": result.get("footnote", "") ,
                    "source": "Rag",
                }
                formatted_results.append(formatted_result)

            logger.info(
                f"Rag search completed with {len(formatted_results)} results"
            )

            return {
                "results": formatted_results,
                "query": query,
                "source": "Rag",
            }

        except Exception as e:
            logger.error(f"Error in Rag search: {e}")
            return {
                "results": [],
                "query": query,
                "error": str(e),
                "source": "Rag",
            }

    async def _arun(self, query: str) -> dict[str, Any] | None:
        """Async version of the search."""
        return self._run(query)


# Create the DuckDuckGo search tool instance
RAG_TOOL: BaseTool = RagTool(
    max_results=settings.RAG_MAX_RESULTS
)
