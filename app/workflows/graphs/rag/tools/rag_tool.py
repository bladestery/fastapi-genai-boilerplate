"""Rag tool to match search format form search tool"""
from app import settings

import asyncio
from typing import Any, Sequence

import httpx
import json
import ast
from langchain_core.tools import BaseTool
from loguru import logger
from pydantic import Field

from app import settings
from app.database.session import async_session_factory
from app.services.vectorstores.pgvector.repository import PgVectorRepository
from app.services.vectorstores.pgvector.service import PgVectorService
from google import genai

from ....pipelines import RagService, RagServiceError

def _create_vector_service() -> PgVectorService:
    """Instantiate the PGVector service layer."""

    repository = PgVectorRepository(async_session_factory)
    return PgVectorService(repository)

def _create_genai_service() -> genai.client.AsyncClient:
    """Instantiate the PGVector service layer."""
    client = genai.Client(
        vertexai=True, project=settings.PROJECT_ID, location=settings.REGION
    )
    return client

def _create_rag_service(
    *,
    client: genai.client.AsyncClient,
    vector_service: PgVectorService,
    default_top_k: int,
) -> RagService:
    """Compose the ``RagService`` configured for Google embeddings."""

    return RagService(
        vector_service=vector_service,
        client=client,
        timeout=settings.RAG_EMBEDDING_TIMEOUT,
        default_top_k=default_top_k,
    )

class RagTool(BaseTool):
    """Tool that retrieves similar documents using the internal RAG pipeline."""

    name: str = "rag_tool"
    description: str = (
        "Retrieve documents from the PGVector store using Google GenAI embeddings."
    )
    top_k: int = Field(
        default=settings.RAG_DEFAULT_TOP_K,
        ge=1,
        description="Maximum number of documents returned from the vector store.",
    )

    def __init__(
        self,
        *,
        client: genai.client.AsyncClient | None = None,
        vector_service: PgVectorService | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        if not settings.GOOGLE_GENAI_API_KEY:
            msg = "GOOGLE_GENAI_API_KEY must be configured to use RagTool."
            raise ValueError(msg)

        self._client = client
        self._owns_client = client is None
        self._vector_service = vector_service or _create_vector_service()
        self._genai_service = client or _create_genai_service()
        self._service = _create_rag_service(
            client=self._genai_service,
            vector_service=self._vector_service,
            default_top_k=self.top_k,
        )

    def _run(self, query: str, top_k: int | None = None, **_: Any) -> dict[str, Any]:
        """Synchronous entry point that proxies to the async implementation."""

        return asyncio.run(self._arun(query, top_k=top_k))

    async def _arun(
        self, query: str, top_k: int | None = None, **_: Any
    ) -> dict[str, Any]:
        """Execute the RAG pipeline asynchronously."""

        search_k = top_k or self.top_k

        try:
            results = await self._service.run(query, top_k=search_k)
        except RagServiceError as exc:
            logger.error("RAG tool failed for query '{}': {}", query, exc)
            return {"query": query, "results": [], "error": str(exc), "source" : "rag"}

        # Transform results
        
        formatted_results = []
        for result in results:
            logger.debug(result['payload']['content'])
            temp2 = ast.literal_eval(result['payload']['content'])
            formatted_result = {
                "id" : result['id'],
                "score" : result['score'],
                "book": temp2['book'],
                "page": temp2['page'],
                "content": temp2['contents'],
                "header": temp2['header'],
                "footnote": temp2['footnotes'],
                "source": "Rag",
            }
            formatted_results.append(formatted_result)

        logger.info(
            f"Rag search completed with {len(formatted_results)} results"
        )

        return {"query": query, "results": formatted_results, "top_k": search_k, "source" : "Rag"}

    async def aclose(self) -> None:
        """Close the underlying HTTP client if owned by the tool."""

        if self._owns_client:
            await self._client.aclose()


# Create the Rag search tool instance
RAG_TOOL: BaseTool = RagTool(
    max_results=settings.RAG_MAX_RESULTS
)
