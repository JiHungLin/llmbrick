from typing import TypeVar, Generic, Callable, Awaitable, Optional, AsyncIterator, Union
from enum import Enum
import functools
from ..utils.logging import log_function

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

class BaseBrick(Generic[InputT, OutputT]):
    def __init__(self, verbose: bool = True):
        self._unary_handler: Optional[Callable[[InputT], Awaitable[OutputT]]] = None
        self._server_streaming_handler: Optional[Callable[[InputT], AsyncIterator[OutputT]]] = None
        self._client_streaming_handler: Optional[Callable[[AsyncIterator[InputT]], Awaitable[OutputT]]] = None
        self._bidi_streaming_handler: Optional[Callable[[AsyncIterator[InputT]], AsyncIterator[OutputT]]] = None
        self.brick_name: str = self.__class__.__name__
        self._verbose: bool = verbose

    # Decorator for unary
    def unary(self):
        def decorator(func):
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
            self._unary_handler = wrapper
            return wrapper
        return decorator

    # Decorator for server streaming
    def server_streaming(self):
        def decorator(func):
            if self._verbose:
                @functools.wraps(func)
                @log_function(service_name=f"{self.brick_name}-ServerStreaming")
                async def wrapper(*args, **kwargs):
                    async for val in func(*args, **kwargs):
                        yield val
            else:
                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    async for val in func(*args, **kwargs):
                        yield val
            self._server_streaming_handler = wrapper
            return wrapper
        return decorator

    # Decorator for client streaming
    def client_streaming(self):
        def decorator(func):
            if self._verbose:
                @functools.wraps(func)
                @log_function(service_name=f"{self.brick_name}-ClientStreaming")
                async def wrapper(*args, **kwargs):
                    res = await func(*args, **kwargs)
                    return res
            else:
                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    res = await func(*args, **kwargs)
                    return res
            self._client_streaming_handler = wrapper
            return wrapper
        return decorator

    # Decorator for bidi streaming
    def bidi_streaming(self):
        def decorator(func):
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
