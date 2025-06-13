"""Route for chat streaming"""

from fastapi import Depends, Query, Request
from fastapi.routing import APIRouter
from fastapi_utils.cbv import cbv

from app.core import limiter
from app.core.responses import AppStreamingResponse

from .models import ChatRequest
from .service import ChatService

router = APIRouter()


def common_dependency():
    """Common dependency."""
    return {"msg": "This is a dependency"}


@cbv(router)
class ChatRoute:
    """Chat-related routes."""

    def __init__(self, common_dep=Depends(common_dependency)):
        self.common_dep = common_dep
        self.service = ChatService()

    @router.get("/chat", response_class=AppStreamingResponse)
    @limiter.limit("5/minute")
    async def chat(
        self,
        request: Request,
        sleep: float = Query(
            1, description="Sleep duration (in seconds) between streamed tokens."
        ),
        number: int = Query(10, description="Total number of tokens to stream."),
    ):
        """Stream chat tokens based on query parameters."""
        chat_request = ChatRequest(sleep=sleep, number=number)
        data = await self.service.chat_service(request_params=chat_request)

        return AppStreamingResponse(data_stream=data)
