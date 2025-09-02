import json
import os
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Optional

from fastapi.responses import HTMLResponse

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError

from llmbrick.core.exceptions import LLMBrickException, ValidationException
from llmbrick.protocols.models.http.conversation import (
    ConversationSSERequest,
    ConversationSSEResponse,
    ConversationResponseProgressEnum
)
from llmbrick.servers.sse.config import SSEServerConfig
from llmbrick.utils.logging import logger


class SSEServer:
    def __init__(
        self,
        handler: Optional[
            Callable[[ConversationSSERequest], AsyncGenerator[ConversationSSEResponse, None]]
        ] = None,
        config: Optional[SSEServerConfig] = None,
        # 保持向後相容性的參數
        chat_completions_path: Optional[str] = None,
        prefix: Optional[str] = None,
        # 自定義驗證器
        custom_validator: Optional[Any] = None,
        # 新增：是否啟用測試用網頁
        enable_test_page: bool = False,
    ):
        """
        SSEServer

        :param handler: 主 SSE handler
        :param config: SSEServerConfig 配置
        :param chat_completions_path: 舊版 API 路徑參數
        :param prefix: 路徑前綴
        :param custom_validator: 自定義驗證器
        :param enable_test_page: 是否啟用測試用網頁 (預設 False，僅開發/測試用)
        """
        # 初始化配置
        if config is None:
            config = SSEServerConfig()
        
        # 向後相容性：如果提供了舊參數，則覆蓋配置
        if chat_completions_path is not None:
            config.chat_completions_path = chat_completions_path
        if prefix is not None:
            config.prefix = prefix
            
        self.config = config
        self.custom_validator = custom_validator
        self._enable_test_page = enable_test_page  # Store the test page setting
        
        # Initialize FastAPI app with basic configuration
        self.app = FastAPI(
            title="LLMBrick SSE Server",
            description="Server-Sent Events API for LLM conversations",
            debug=self.config.debug_mode
        )

        # Register test page if enabled (only once at initialization)
        if self._enable_test_page:
            templates_dir = Path(__file__).parent / 'templates'
            template_path = templates_dir / 'test_page.html'
            
            if not template_path.exists():
                logger.warning(f"Test page template not found at {template_path}")
            else:
                @self.app.get("/", response_class=HTMLResponse)
                async def test_page():
                    full_path = self.config.prefix + self.config.chat_completions_path
                    # Read the template and inject the API endpoint
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = f.read()
                    
                    # Calculate the actual API endpoint URL
                    html = template.replace('{api_endpoint}', full_path)

                    # Add warning if handler is not set
                    has_handler = hasattr(self, '_handler') and self._handler is not None
                    status_script = f"""
                    <script>
                        window.hasHandler = {str(has_handler).lower()};
                        if (!window.hasHandler) {{
                            const warning = document.createElement('div');
                            warning.className = 'warning';
                            warning.innerHTML = '⚠️ Warning: No handler is configured. Requests will fail until a handler is set.';
                            document.body.insertBefore(warning, document.body.firstChild);
                        }}
                    </script>
                    """
                    # Insert the status script before </body>
                    html = html.replace('</body>', f'{status_script}</body>')
                    
                    return HTMLResponse(content=html)

        # 註冊 LLMBrickException handler
        @self.app.exception_handler(LLMBrickException)
        async def llmbrick_exception_handler(
            _: Any, exc: LLMBrickException
        ) -> JSONResponse:
            logger.error(f"LLMBrickException: {exc}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "LLMBrick Exception",
                    "error_code": exc.code.value,
                    "error_name": exc.code.name,
                    "message": exc.message,
                    "details": exc.detail,
                }
            )

        # 註冊 ValidationException handler
        @self.app.exception_handler(ValidationException)
        async def validation_exception_handler(
            _: Any, exc: ValidationException
        ) -> JSONResponse:
            logger.error(f"ValidationException: {exc}")
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Validation Exception",
                    "error_code": exc.code.value,
                    "error_name": exc.code.name,
                    "message": exc.message,
                    "details": exc.detail,
                }
            )

        # 處理 prefix 格式，確保開頭有 /，結尾無 /
        if self.config.prefix and not self.config.prefix.startswith("/"):
            self.config.prefix = "/" + self.config.prefix
        if self.config.prefix.endswith("/") and self.config.prefix != "/":
            self.config.prefix = self.config.prefix[:-1]
        
        # 處理 path 格式，確保開頭有 /
        if not self.config.chat_completions_path.startswith("/"):
            self.config.chat_completions_path = "/" + self.config.chat_completions_path

        # Register initial routes (including test page)
        self.setup_routes()

        # Set handler if provided (will reset routes)
        if handler is not None:
            self.set_handler(handler)

    @property
    def fastapi_app(self) -> FastAPI:
        return self.app

    def set_handler(
        self, func: Callable[[ConversationSSERequest], AsyncGenerator[ConversationSSEResponse, None]]
    ) -> None:
        """
        直接設定主 handler，handler 必須為 async generator，yield event dict
        """
        self._handler = func
        self.setup_routes()

    def handler(
        self, func: Callable[[ConversationSSERequest], AsyncGenerator[ConversationSSEResponse, None]]
    ) -> Callable[[ConversationSSERequest], AsyncGenerator[ConversationSSEResponse, None]]:
        """
        Decorator 註冊主 handler，handler 必須為 async generator，yield event dict
        用法：
            @server.handler
            async def my_handler(...): ...
        """
        self.set_handler(func)
        self.setup_routes()
        return func

    def _validate_event(self, event: Any) -> tuple[bool, str]:
        """強化型態與內容驗證，回傳(是否有效, 錯誤訊息)"""
        if not isinstance(event, ConversationSSEResponse):
            return False, f"Event must be ConversationSSEResponse, got {type(event)}"
        # 必要欄位檢查
        if not getattr(event, "id", None):
            return False, "Event.id is required"
        if not getattr(event, "type", None):
            return False, "Event.type is required"
        if not getattr(event, "progress", None):
            return False, "Event.progress is required"
        if not isinstance(event.progress, ConversationResponseProgressEnum):
            try:
                event.progress = ConversationResponseProgressEnum(event.progress)
            except Exception:
                return False, f"Invalid progress value: {event.progress}"
        return True, ""

    def setup_routes(self) -> None:
        """設定 API 路由"""
        full_path = self.config.prefix + self.config.chat_completions_path

        # Register SSE endpoint
        @self.app.post(
            full_path,
            response_description="SSE response stream",
            response_model=ConversationSSEResponse,
            response_model_by_alias=True,
        )
        async def chat_completions(request: Request, body: ConversationSSERequest) -> StreamingResponse:
            # 檢查 Accept header 是否包含 text/event-stream
            accept_header = request.headers.get("accept", "")
            if "text/event-stream" not in accept_header:
                raise HTTPException(
                    status_code=406,
                    detail={
                        "error": "Accept header must include 'text/event-stream' for SSE"
                    },
                )

            if not hasattr(self, "_handler") or self._handler is None:
                raise HTTPException(
                    status_code=404, detail={"error": "Handler not set"}
                )
            
            from llmbrick.servers.sse.validators import ConversationSSERequestValidator
            from llmbrick.core.exceptions import ValidationException
            
            # 請求日誌
            if self.config.enable_request_logging:
                logger.info(f"SSE request received: model={body.model}, session_id={body.session_id}")
            
            async def event_stream() -> AsyncGenerator[str, None]:
                try:
                    # 業務邏輯驗證
                    try:
                        if self.custom_validator:
                            # 使用自定義驗證器
                            self.custom_validator.validate(
                                body,
                                allowed_models=self.config.allowed_models,
                                max_message_length=self.config.max_message_length,
                                max_messages_count=self.config.max_messages_count
                            )
                        else:
                            # 使用預設驗證器
                            ConversationSSERequestValidator.validate(
                                body,
                                allowed_models=self.config.allowed_models,
                                max_message_length=self.config.max_message_length,
                                max_messages_count=self.config.max_messages_count
                            )
                    except ValidationException as ve:
                        error_details = str(ve) if self.config.enable_validation_details else "Business validation failed"
                        yield f"event: error\ndata: {json.dumps({'error': 'Business validation failed', 'details': error_details})}\n\n"
                        return
                    
                    async for event in self._handler(body):
                        valid, err_msg = self._validate_event(event)
                        if not valid:
                            error_details = err_msg if self.config.debug_mode else "Server returned invalid event"
                            yield f"event: error\ndata: {json.dumps({'error': 'Server returned invalid event', 'details': error_details})}\n\n"
                            break
                        yield f"event: message\ndata: {event.model_dump_json()}\n\n"
                except Exception as e:
                    error_details = str(e) if self.config.debug_mode else "Handler exception occurred"
                    if self.config.debug_mode:
                        logger.exception("Handler exception in SSE stream")
                    yield f"event: error\ndata: {json.dumps({'error': 'Handler exception', 'details': error_details})}\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")

    def run(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        啟動 FastAPI SSE 服務
        """
        # 使用配置中的值，如果沒有提供參數的話
        actual_host = host or self.config.host
        actual_port = port or self.config.port
        
        full_path = self.config.prefix + self.config.chat_completions_path
        logger.info(
            f"SSE Server starting at: http://{actual_host}:{actual_port}{full_path}"
        )
        logger.info(f"Debug mode: {self.config.debug_mode}")
        logger.info(f"Allowed models: {self.config.allowed_models}")
        
        # Log test page URL if enabled
        if hasattr(self, '_enable_test_page') and self._enable_test_page:
            logger.info(f"Test page available at: http://{actual_host}:{actual_port}/")
        
        uvicorn.run(
            self.app,
            host=actual_host,
            port=actual_port,
            log_level="debug" if self.config.debug_mode else "info"
        )
