"""Rag tool to match search format form search tool"""
from app import settings

import asyncio
from typing import Any, Sequence

import ast
from langchain_core.tools import BaseTool
from loguru import logger
from pydantic import Field
import threading
import time
from concurrent.futures import TimeoutError as FuturesTimeoutError

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

        self._owns_client = client is None
        self._genai_service = client or _create_genai_service()
        self._client = self._genai_service
        self._vector_service = vector_service or _create_vector_service()
        self._service = _create_rag_service(
            client=self._genai_service,
            vector_service=self._vector_service,
            default_top_k=self.top_k,
        )
        self._loop: asyncio.AbstractEventLoop | None = None
        self._loop_thread: threading.Thread | None = None
        self._loop_lock = threading.Lock()

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        """Create (and if necessary start) a dedicated event loop for sync calls."""

        with self._loop_lock:
            if self._loop and self._loop.is_running():
                return self._loop

            loop = asyncio.new_event_loop()

            def _run_loop() -> None:
                asyncio.set_event_loop(loop)
                loop.run_forever()

            thread = threading.Thread(target=_run_loop, daemon=True)
            thread.start()

            self._loop = loop
            self._loop_thread = thread

            # Wait until the loop is running before returning.
            while not loop.is_running():
                time.sleep(0.001)

            return loop


    def _run(self, query: str, top_k: int | None = None, **_: Any) -> dict[str, Any]:
        """Synchronous entry point that proxies to the async implementation."""

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = self._ensure_loop()
            future = asyncio.run_coroutine_threadsafe(
                self._arun(query, top_k=top_k), loop
            )
            try:
                return future.result(timeout=settings.RAG_EMBEDDING_TIMEOUT)
            except FuturesTimeoutError as exc:  # pragma: no cover - defensive
                future.cancel()
                msg = "RAG tool execution timed out."
                logger.exception(msg)
                raise RuntimeError(msg) from exc
        else:  # pragma: no cover - defensive
            msg = (
                "RagTool._run cannot be invoked from within a running event loop. "
                "Use the asynchronous interface (ainvoke) instead."
            )
            raise RuntimeError(msg)

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

        if self._owns_client and hasattr(self._client, "aclose"):
            await self._client.aclose()

        loop = self._loop
        thread = self._loop_thread
        if loop and loop.is_running():
            loop.call_soon_threadsafe(loop.stop)
            if thread:
                await asyncio.to_thread(thread.join)
            loop.close()
            self._loop = None
            self._loop_thread = None

            
# Create the Rag search tool instance
RAG_TOOL: BaseTool = RagTool(
    max_results=settings.RAG_MAX_RESULTS
)
