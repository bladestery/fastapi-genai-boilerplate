"""DuckDuckGo search tool for websearch via LangChain Community Tools."""

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import BaseTool

DUCKDUCKGO_SEARCH_TOOL: BaseTool = DuckDuckGoSearchResults(
    num_results=10, handle_tool_error=True, output_format="list"
)
