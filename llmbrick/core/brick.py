from typing import TypeVar, Generic, Callable, Awaitable, Optional, AsyncIterator, Union
from enum import Enum
import functools
# --- 強型別 decorator，避免字串錯誤 ---
def unary_handler(func):
    return _brick_handler("unary")(func)

def output_streaming_handler(func):
    return _brick_handler("output_streaming")(func)

def input_streaming_handler(func):
    return _brick_handler("input_streaming")(func)

def bidi_streaming_handler(func):
    return _brick_handler("bidi_streaming")(func)

def get_service_info_handler(func):
    return _brick_handler("get_service_info")(func)

# --- Brick Handler Decorator for Class-level Registration ---
def _brick_handler(call_type: str):
    """
    用於標記 class method 為 brick handler，call_type 可為 'unary'、'output_streaming' 等
    """
    def decorator(func):
        setattr(func, "_brick_handler_type", call_type)
        return func
    return decorator
from ..utils.logging import log_function

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")

UnaryHandler = Callable[[InputT], Awaitable[OutputT]]
OutputStreamingHandler = Callable[[InputT], AsyncIterator[OutputT]]
InputStreamingHandler = Callable[[AsyncIterator[InputT]], Awaitable[OutputT]]
BidiStreamingHandler = Callable[[AsyncIterator[InputT]], AsyncIterator[OutputT]]


class GRPCCallType(Enum):
    UNARY = "unary"
    output_streaming = "output_streaming"
    input_streaming = "input_streaming"
    BIDI_STREAMING = "bidi_streaming"

class BaseBrick(Generic[InputT, OutputT]):

    grpc_service_type = "common"  # 預設為 common
    # 可由子類覆寫，若為 None 則不限制
    allowed_handler_types: Optional[set] = None

    def __init__(self, verbose: bool = True):
        self._unary_handler: Optional[UnaryHandler] = None
        self._output_streaming_handler: Optional[OutputStreamingHandler] = None
        self._input_streaming_handler: Optional[InputStreamingHandler] = None
        self._bidi_streaming_handler: Optional[BidiStreamingHandler] = None
        self._get_service_info_handler: Optional[Callable] = None
        self.brick_name: str = self.__class__.__name__
        self._verbose: bool = verbose

        # --- 自動註冊 class-level handler ---
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_brick_handler_type"):
                call_type = getattr(attr, "_brick_handler_type")
                # 檢查是否允許此 handler
                allowed = getattr(self, "allowed_handler_types", None)
                if allowed is not None and call_type not in allowed:
                    raise RuntimeError(
                        f"[{self.brick_name}] 不允許定義 handler: '{call_type}'，"
                        f"只允許: {sorted(allowed)}"
                    )
                if call_type == "unary":
                    self._unary_handler = attr
                elif call_type == "output_streaming":
                    self._output_streaming_handler = attr
                elif call_type == "input_streaming":
                    self._input_streaming_handler = attr
                elif call_type == "bidi_streaming":
                    self._bidi_streaming_handler = attr
                elif call_type == "get_service_info":
                    self._get_service_info_handler = attr

    def get_service_info(self):
        """
        回傳服務資訊，子類可覆寫
        """
        return {
            "service_name": self.brick_name,
            "version": "1.0.0",
            "models": []
        }
    # Decorator for unary
    def unary(self):
        def decorator(func: UnaryHandler) -> UnaryHandler:
            if self._verbose:
                @functools.wraps(func)
                @log_function(service_name=f"{self.brick_name}-Unary")
                async def wrapper(*args, **kwargs):
                    res = await func(*args, **kwargs)
                    return res
            else:
                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    res = await func(*args, **kwargs)
                    return res
            self._unary_handler = wrapper  # type: ignore
            return wrapper  # type: ignore
        return decorator

    # Decorator for server streaming
    def output_streaming(self):
        def decorator(func: OutputStreamingHandler) -> OutputStreamingHandler:
            if self._verbose:
                @functools.wraps(func)
                @log_function(service_name=f"{self.brick_name}-OutputStreaming")
                async def wrapper(*args, **kwargs):
                    async for val in func(*args, **kwargs):
                        yield val
            else:
                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    async for val in func(*args, **kwargs):
                        yield val
            self._output_streaming_handler = wrapper  # type: ignore
            return wrapper  # type: ignore
        return decorator

    # Decorator for client streaming
    def input_streaming(self):
        def decorator(func: InputStreamingHandler) -> InputStreamingHandler:
            if self._verbose:
                @functools.wraps(func)
                @log_function(service_name=f"{self.brick_name}-InputStreaming")
                async def wrapper(*args, **kwargs):
                    res = await func(*args, **kwargs)
                    return res
            else:
                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    res = await func(*args, **kwargs)
                    return res
            self._input_streaming_handler = wrapper  # type: ignore
            return wrapper  # type: ignore
        return decorator

    # Decorator for bidi streaming
    def bidi_streaming(self):
        def decorator(func: BidiStreamingHandler) -> BidiStreamingHandler:
            if self._verbose:
                @functools.wraps(func)
                @log_function(service_name=f"{self.brick_name}-BidiStreaming")
                async def wrapper(*args, **kwargs):
                    async for val in func(*args, **kwargs):
                        yield val
            else:
                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    async for val in func(*args, **kwargs):
                        yield val
            self._bidi_streaming_handler = wrapper  # type: ignore
            return wrapper  # type: ignore
        return decorator

    # Entry: unary call
    async def run_unary(self, input_data: InputT) -> OutputT:
        if not self._unary_handler:
            raise NotImplementedError("Unary handler not registered")
        try:
            return await self._unary_handler(input_data)
        except Exception as e:
            from ..utils.logging import logger
            logger.error(f"[{self.brick_name}] run_unary exception: {e}", exc_info=True)
            raise

    # Entry: get_service_info call
    async def run_get_service_info(self):
        """
        呼叫 get_service_info handler，若無則回傳預設
        """
        if self._get_service_info_handler:
            if callable(self._get_service_info_handler):
                # 支援 async/await
                if hasattr(self._get_service_info_handler, "__code__") and self._get_service_info_handler.__code__.co_flags & 0x80:
                    return await self._get_service_info_handler()
                else:
                    return self._get_service_info_handler()
        # fallback 預設
        return {
            "service_name": self.brick_name,
            "version": "1.0.0",
            "models": []
        }

    # Entry: server streaming call
    async def run_output_streaming(self, input_data: InputT) -> AsyncIterator[OutputT]:
        if not self._output_streaming_handler:
            raise NotImplementedError("Server streaming handler not registered")
        try:
            async for val in self._output_streaming_handler(input_data):
                yield val
        except Exception as e:
            from ..utils.logging import logger
            logger.error(f"[{self.brick_name}] run_output_streaming exception: {e}", exc_info=True)
            raise

    # Entry: client streaming call
    async def run_input_streaming(self, input_stream: AsyncIterator[InputT]) -> OutputT:
        if not self._input_streaming_handler:
            raise NotImplementedError("Client streaming handler not registered")
        try:
            return await self._input_streaming_handler(input_stream)
        except Exception as e:
            from ..utils.logging import logger
            logger.error(f"[{self.brick_name}] run_input_streaming exception: {e}", exc_info=True)
            raise

    # Entry: bidirectional streaming call
    async def run_bidi_streaming(self, input_stream: AsyncIterator[InputT]) -> AsyncIterator[OutputT]:
        if not self._bidi_streaming_handler:
            raise NotImplementedError("Bidi streaming handler not registered")
        try:
            async for val in self._bidi_streaming_handler(input_stream):
                yield val
        except Exception as e:
            from ..utils.logging import logger
            logger.error(f"[{self.brick_name}] run_bidi_streaming exception: {e}", exc_info=True)
            raise
