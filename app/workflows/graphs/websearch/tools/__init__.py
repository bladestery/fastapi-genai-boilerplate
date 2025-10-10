"""Initialize and expose available tools for the agent."""

from langchain_core.tools import BaseTool

from app import settings

from .duckduckgo_search_tool import DUCKDUCKGO_SEARCH_TOOL

# Import both search tools
from .tavily_search_tool import TAVILY_SEARCH_TOOL

# Select search tool based on configuration
if settings.SEARCH_PROVIDER.lower() == "duckduckgo":
    SEARCH_TOOL: BaseTool = DUCKDUCKGO_SEARCH_TOOL
else:
    SEARCH_TOOL: BaseTool = TAVILY_SEARCH_TOOL

TOOLS: list[BaseTool] = [SEARCH_TOOL]

__all__ = ["TOOLS", "SEARCH_TOOL", "TAVILY_SEARCH_TOOL", "DUCKDUCKGO_SEARCH_TOOL"]
