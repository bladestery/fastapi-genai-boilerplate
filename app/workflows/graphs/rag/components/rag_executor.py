"""Rag search component that retrieves search results for enhanced or rephrased questions."""

from typing import Any

from loguru import logger

from ..states import AgentState
from ..tools import RAG_TOOL


class RagExecutor:
    """Agent component responsible for executing rag based on refined or enhanced questions."""

    def search(self, state: AgentState) -> dict[str, list[dict[str, Any]]]:
        """
        Executes rag search queries using available questions in the state.
        """
        questions = (
            state["refined_questions"]
            if state["refined_questions"]
            else [state["refined_question"]]
        )
        results = []

        for query in questions:
            logger.info(f"Performing rag search for: {query}")
            result = RAG_TOOL.invoke({"query": query})

            for item in result.get("results"):
                if item.get("content"):
                    results.append(item)

        logger.info(f"Rag completed with {len(results)} result sets.")

        return {"search_results": results}
