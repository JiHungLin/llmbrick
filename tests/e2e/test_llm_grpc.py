"""
LLMBrick gRPC 端到端功能測試

本測試涵蓋 LLMBrick 在 gRPC server/client 模式下的主要功能與錯誤處理。
"""

import asyncio
from typing import Any, AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.core.brick import (
    unary_handler,
    output_streaming_handler,
    get_service_info_handler,
)
from llmbrick.protocols.models.bricks.llm_types import (
    LLMRequest,
    LLMResponse,
)
from llmbrick.protocols.models.bricks.common_types import (
    ServiceInfoResponse,
    ErrorDetail,
    ModelInfo,
)
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.core.error_codes import ErrorCodes

# Server 端專用 LLMBrick，需有 handler
class ServerLLMBrick(LLMBrick):
    def __init__(self, default_prompt: str = "gRPC hi", **kwargs):
        super().__init__(default_prompt=default_prompt, **kwargs)

    @unary_handler
    async def unary(self, request: LLMRequest) -> LLMResponse:
        await asyncio.sleep(0.01)
        return LLMResponse(
            text=f"gRPC Echo: {request.prompt or self.default_prompt}",
            tokens=["echo"],  # tokens 必須為 List[str]
            is_final=True,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

    @output_streaming_handler
    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMResponse]:
        for i in range(2):
            await asyncio.sleep(0.01)
            yield LLMResponse(
                text=f"gRPC Stream {i}: {request.prompt or self.default_prompt}",
                tokens=[str(i)],  # tokens 必須為 List[str]
                is_final=(i == 1),
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
            )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="TestLLMBrick",
            version="2.0.0",
            models=[
                ModelInfo(
                    model_id="llm-grpc",
                    version="2.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=True,
                    description="gRPC test LLM",
                )
            ],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

# Client 端專用 LLMBrick，handler 由 toGrpcClient 註冊
class TestLLMBrick(LLMBrick):
    def __init__(self, default_prompt: str = "gRPC hi", **kwargs):
        super().__init__(default_prompt=default_prompt, **kwargs)

@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
    # server 端需有 handler
    brick = ServerLLMBrick(default_prompt="gRPC default", verbose=False)
    server = GrpcServer(port=50060)
    server.register_service(brick)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)  # 等 server 啟動
    yield
    await server.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

@pytest_asyncio.fixture
async def grpc_client(grpc_server: Any) -> AsyncIterator[LLMBrick]:
    client_brick = TestLLMBrick.toGrpcClient(
        remote_address="127.0.0.1:50060", default_prompt="gRPC default", verbose=False
    )
    yield client_brick

@pytest.mark.asyncio
async def test_grpc_unary(grpc_client: LLMBrick):
    req = LLMRequest(prompt="gRPC test", context=[])
    resp = await grpc_client.run_unary(req)
    assert resp.text == "gRPC Echo: gRPC test"
    assert resp.tokens == ["echo"]
    assert resp.is_final is True
    assert resp.error.code == ErrorCodes.SUCCESS

@pytest.mark.asyncio
async def test_grpc_output_streaming(grpc_client: LLMBrick):
    req = LLMRequest(prompt="gRPC stream", context=[])
    results = []
    async for resp in grpc_client.run_output_streaming(req):
        results.append((resp.text, resp.tokens))
    assert results == [
        ("gRPC Stream 0: gRPC stream", ["0"]),
        ("gRPC Stream 1: gRPC stream", ["1"]),
    ]

@pytest.mark.asyncio
async def test_grpc_get_service_info(grpc_client: LLMBrick):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestLLMBrick"
    assert info.version == "2.0.0"
    assert info.models[0].model_id == "llm-grpc"

@pytest.mark.asyncio
async def test_grpc_error_response(grpc_server):
    class ErrorLLMBrick(LLMBrick):
        @unary_handler
        async def error_unary(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text="",
                tokens=[],  # tokens 必須為 List[str]
                is_final=True,
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message="gRPC error"),
            )
    # 啟動一個臨時 server
    server = GrpcServer(port=50061)
    brick = ErrorLLMBrick(default_prompt="err", verbose=False)
    server.register_service(brick)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.3)
    client = ErrorLLMBrick.toGrpcClient("127.0.0.1:50061", default_prompt="err", verbose=False)
    req = LLMRequest(prompt="err", context=[])
    resp = await client.run_unary(req)
    assert resp.error.code == ErrorCodes.INTERNAL_ERROR
    assert "gRPC error" in resp.error.message
    await server.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass
