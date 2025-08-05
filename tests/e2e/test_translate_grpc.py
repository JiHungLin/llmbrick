"""
TranslateBrick gRPC 端到端功能測試

本測試驗證 TranslateBrick 在 gRPC server/client 模式下的正確性與一致性。
"""

import asyncio
from typing import Any, AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.core.brick import (
    unary_handler,
    output_streaming_handler,
    get_service_info_handler,
)
from llmbrick.protocols.models.bricks.translate_types import (
    TranslateRequest,
    TranslateResponse,
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ModelInfo,
    ServiceInfoResponse,
)
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.core.error_codes import ErrorCodes

class _TestTranslateBrick(TranslateBrick):
    """測試用的 TranslateBrick"""

    @unary_handler
    async def unary_handler(self, request: TranslateRequest) -> TranslateResponse:
        await asyncio.sleep(0.05)
        return TranslateResponse(
            text=f"{request.text} ({request.target_language})",
            tokens=list(request.text),
            language_code=request.target_language,
            is_final=True,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="No error"),
        )

    @output_streaming_handler
    async def output_streaming_handler(
        self, request: TranslateRequest
    ) -> AsyncIterator[TranslateResponse]:
        for i, word in enumerate(request.text.split()):
            await asyncio.sleep(0.02)
            yield TranslateResponse(
                text=f"{word} (t{i})",
                tokens=[word],
                language_code=request.target_language,
                is_final=(i == len(request.text.split()) - 1),
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="No error"),
            )

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        return ServiceInfoResponse(
            service_name="TestTranslateBrick",
            version="9.9.9",
            models=[
                ModelInfo(
                    model_id="test-translator",
                    version="1.0",
                    supported_languages=["zh", "en"],
                    support_streaming=True,
                    description="test",
                )
            ],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="No error"),
        )

@pytest.mark.asyncio
async def test_async_grpc_server_startup():
    """測試異步 gRPC 伺服器啟動"""
    brick = _TestTranslateBrick()
    server = GrpcServer(port=50066)
    server.register_service(brick)
    assert len(server._pending_bricks) > 0
    assert server.port == 50066

@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
    brick = _TestTranslateBrick(verbose=False)
    server = GrpcServer(port=50068)
    server.register_service(brick)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    yield
    await server.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

@pytest_asyncio.fixture
async def grpc_client(grpc_server: Any) -> AsyncIterator[_TestTranslateBrick]:
    client_brick = _TestTranslateBrick.toGrpcClient(
        remote_address="127.0.0.1:50068", verbose=False
    )
    yield client_brick

@pytest.mark.asyncio
async def test_unary(grpc_client: _TestTranslateBrick):
    request = TranslateRequest(
        text="Hello world",
        model_id="test-translator",
        target_language="zh",
        client_id="test",
        session_id="s1",
        request_id="r1",
        source_language="en",
    )
    response = await grpc_client.run_unary(request)
    assert response.text.endswith("(zh)")
    assert response.language_code == "zh"
    assert response.is_final
    assert response.error.code == ErrorCodes.SUCCESS

@pytest.mark.asyncio
async def test_output_streaming(grpc_client: _TestTranslateBrick):
    request = TranslateRequest(
        text="Hello world",
        model_id="test-translator",
        target_language="en",
        client_id="test",
        session_id="s1",
        request_id="r2",
        source_language="zh",
    )
    results = []
    async for resp in grpc_client.run_output_streaming(request):
        results.append(resp.text)
    assert results == ["Hello (t0)", "world (t1)"]

@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestTranslateBrick):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestTranslateBrick"
    assert info.models[0].model_id == "test-translator"

@pytest.mark.asyncio
async def test_not_implemented_handlers(grpc_client: _TestTranslateBrick):
    request = TranslateRequest(
        text="test",
        model_id="test-translator",
        target_language="en",
        client_id="test",
        session_id="s1",
        request_id="r3",
        source_language="zh",
    )
    # input_streaming
    with pytest.raises(NotImplementedError):
        await grpc_client.run_input_streaming(iter([request]))
    # bidi_streaming
    with pytest.raises(NotImplementedError):
        async for _ in grpc_client.run_bidi_streaming(iter([request])):
            pass

@pytest.mark.asyncio
async def test_error_handling(grpc_server):
    class ErrorBrick(TranslateBrick):
        @unary_handler
        async def error_handler(self, request: TranslateRequest) -> TranslateResponse:
            return TranslateResponse(
                text="",
                tokens=[],
                language_code="",
                is_final=True,
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message="Simulated error", detail="Test error"),
            )
    # 啟動一個新的 server
    server = GrpcServer(port=50069)
    server.register_service(ErrorBrick(verbose=False))
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    client_brick = ErrorBrick.toGrpcClient("127.0.0.1:50069", verbose=False)
    request = TranslateRequest(
        text="fail",
        model_id="test-translator",
        target_language="en",
        client_id="test",
        session_id="s1",
        request_id="r4",
        source_language="zh",
    )
    response = await client_brick.run_unary(request)
    assert response.error.code == ErrorCodes.INTERNAL_ERROR
    assert "Simulated error" in response.error.message
    await server.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass
