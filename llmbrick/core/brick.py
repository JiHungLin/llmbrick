from typing import TypeVar, Generic, Callable, Awaitable, Optional, AsyncIterator, Union
from enum import Enum
import functools

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")

UnaryHandler = Callable[[InputT], Awaitable[OutputT]]
ServerStreamingHandler = Callable[[InputT], AsyncIterator[OutputT]]
ClientStreamingHandler = Callable[[AsyncIterator[InputT]], Awaitable[OutputT]]
BidiStreamingHandler = Callable[[AsyncIterator[InputT]], AsyncIterator[OutputT]]


class GRPCCallType(Enum):
    UNARY = "unary"
    SERVER_STREAMING = "server_streaming"
    CLIENT_STREAMING = "client_streaming"
    BIDI_STREAMING = "bidi_streaming"

# 裝飾器範例，可擴充用於前後攔截、驗證、異常捕捉等
def process_decorator(func: Callable[..., Awaitable[OutputT]]) -> Callable[..., Awaitable[OutputT]]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> OutputT:
        print(f"[Decorator] Before {func.__name__}")
        result = await func(*args, **kwargs)
        print(f"[Decorator] After {func.__name__}")
        return result
    return wrapper
class BaseBrick(Generic[InputT, OutputT]):
    def __init__(self):
        self._unary_handler: Optional[Callable[[InputT], Awaitable[OutputT]]] = None
        self._server_streaming_handler: Optional[Callable[[InputT], AsyncIterator[OutputT]]] = None
        self._client_streaming_handler: Optional[Callable[[AsyncIterator[InputT]], Awaitable[OutputT]]] = None
        self._bidi_streaming_handler: Optional[Callable[[AsyncIterator[InputT]], AsyncIterator[OutputT]]] = None

    # Decorator for unary
    def unary(self):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                print("[Unary] Before process")
                res = await func(*args, **kwargs)
                print("[Unary] After process")
                return res
            self._unary_handler = wrapper
            return wrapper
        return decorator

    # Decorator for server streaming
    def server_streaming(self):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                print("[ServerStreaming] Before process")
                async for val in func(*args, **kwargs):
                    yield val
                print("[ServerStreaming] After process")
            self._server_streaming_handler = wrapper
            return wrapper
        return decorator

    # Decorator for client streaming
    def client_streaming(self):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                print("[ClientStreaming] Before process")
                res = await func(*args, **kwargs)
                print("[ClientStreaming] After process")
                return res
            self._client_streaming_handler = wrapper
            return wrapper
        return decorator

    # Decorator for bidi streaming
    def bidi_streaming(self):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                print("[BidiStreaming] Before process")
                async for val in func(*args, **kwargs):
                    yield val
                print("[BidiStreaming] After process")
            self._bidi_streaming_handler = wrapper
            return wrapper
        return decorator

    # Entry: unary call
    async def run_unary(self, input_data: InputT) -> OutputT:
        if not self._unary_handler:
            raise NotImplementedError("Unary handler not registered")
        return await self._unary_handler(input_data)

    # Entry: server streaming call
    async def run_server_streaming(self, input_data: InputT) -> AsyncIterator[OutputT]:
        if not self._server_streaming_handler:
            raise NotImplementedError("Server streaming handler not registered")
        async for val in self._server_streaming_handler(input_data):
            yield val

    # Entry: client streaming call
    async def run_client_streaming(self, input_stream: AsyncIterator[InputT]) -> OutputT:
        if not self._client_streaming_handler:
            raise NotImplementedError("Client streaming handler not registered")
        return await self._client_streaming_handler(input_stream)

    # Entry: bidirectional streaming call
    async def run_bidi_streaming(self, input_stream: AsyncIterator[InputT]) -> AsyncIterator[OutputT]:
        if not self._bidi_streaming_handler:
            raise NotImplementedError("Bidi streaming handler not registered")
        async for val in self._bidi_streaming_handler(input_stream):
            yield val