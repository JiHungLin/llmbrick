import json
from typing import Any, AsyncGenerator, Callable, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError

from llmbrick.core.exceptions import LLMBrickException
from llmbrick.protocols.models.http.conversation import (
    ConversationSSERequest,
    ConversationSSEResponse,
)
from llmbrick.utils.logging import logger


class SSEServer:
    def __init__(
        self,
        handler: Optional[Callable[[Dict[str, Any]], AsyncGenerator[Dict[str, Any], None]]] = None,
        chat_completions_path: str = "/chat/completions",
        prefix: str = "",
    ):
        self.app = FastAPI()

        # 註冊 LLMBrickException handler
        @self.app.exception_handler(LLMBrickException)
        async def llmbrick_exception_handler(_: Any, exc: LLMBrickException) -> JSONResponse:
            logger.error(f"LLMBrickException: {exc}")
            raise HTTPException(status_code=400, detail=exc.to_dict())

        # 處理 prefix 格式，確保開頭有 /，結尾無 /
        if prefix and not prefix.startswith("/"):
            prefix = "/" + prefix
        if prefix.endswith("/") and prefix != "/":
            prefix = prefix[:-1]
        self.prefix = prefix
        # 處理 path 格式，確保開頭有 /
        if not chat_completions_path.startswith("/"):
            chat_completions_path = "/" + chat_completions_path
        self.chat_completions_path = chat_completions_path
        if handler is not None:
            self.set_handler(handler)

    @property
    def fastapi_app(self) -> FastAPI:
        return self.app

    def set_handler(
        self, func: Callable[[Dict[str, Any]], AsyncGenerator[Dict[str, Any], None]]
    ) -> None:
        """
        直接設定主 handler，handler 必須為 async generator，yield event dict
        """
        self._handler = func
        self.setup_routes()

    def handler(
        self, func: Callable[[Dict[str, Any]], AsyncGenerator[Dict[str, Any], None]]
    ) -> Callable[[Dict[str, Any]], AsyncGenerator[Dict[str, Any], None]]:
        """
        Decorator 註冊主 handler，handler 必須為 async generator，yield event dict
        用法：
            @server.handler
            async def my_handler(...): ...
        """
        self.set_handler(func)
        self.setup_routes()
        return func

    def _validate_event(self, event: Dict[str, Any]) -> bool:
        # 使用 pydantic v2 model_validate 進行型別驗證
        from pydantic import ValidationError

        try:
            ConversationSSEResponse.model_validate(event)
            return True
        except ValidationError:
            return False

    def setup_routes(self) -> None:
        full_path = self.prefix + self.chat_completions_path

        @self.app.post(
            full_path,
            response_description="SSE response stream",
            response_model=ConversationSSEResponse,
            response_model_by_alias=True,
        )
        async def chat_completions(request: Request) -> StreamingResponse:
            # 檢查 Accept header 是否包含 text/event-stream
            accept_header = request.headers.get("accept", "")
            if "text/event-stream" not in accept_header:
                raise HTTPException(
                    status_code=406,
                    detail={
                        "error": "Accept header must include 'text/event-stream' for SSE"
                    },
                )
            try:
                # 先檢查 body 是否為空
                raw_body = await request.body()
                if not raw_body or raw_body.strip() == b"" or raw_body.strip() == b"{}":
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Empty request body",
                            "details": "Request body is empty. Please provide a valid JSON object.",
                        },
                    )
                body_json = await request.json()
            except ValidationError as ve:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "Invalid request",
                        "details": ve.errors(),
                        "input": body_json,
                        "message": "Request body does not conform to ConversationSSERequest schema. See 'details' for field errors.",
                    },
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Malformed request",
                        "details": str(e),
                    },
                )
            if not hasattr(self, "_handler") or self._handler is None:
                raise HTTPException(
                    status_code=404, detail={"error": "Handler not set"}
                )

            async def event_stream() -> AsyncGenerator[str, None]:
                try:
                    async for event in self._handler(body_json):
                        if not self._validate_event(event):
                            yield f"event: error\ndata: {json.dumps({'error': 'Invalid event format'})}\n\n"
                            break
                        yield f"event: message\ndata: {json.dumps(event)}\n\n"
                except Exception as e:
                    yield f"event: error\ndata: {json.dumps({'error': 'Handler exception', 'details': str(e)})}\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        啟動 FastAPI SSE 服務
        """
        full_path = self.prefix + self.chat_completions_path
        logger.info(
            f"SSE Server endpoint: http://{host}:{port}{full_path} (Press CTRL+C to quit)"
        )
        uvicorn.run(self.app, host=host, port=port)
