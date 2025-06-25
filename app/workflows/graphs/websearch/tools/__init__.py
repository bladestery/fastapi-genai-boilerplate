"""Initialize and expose available tools for the agent."""

from langchain_core.tools import BaseTool

from .duckduckgo_search_tool import DUCKDUCKGO_SEARCH_TOOL

TOOLS: list[BaseTool] = [DUCKDUCKGO_SEARCH_TOOL]

__all__ = ["TOOLS", "DUCKDUCKGO_SEARCH_TOOL"]
