"""
RectifyBrick gRPC 功能測試
"""

import asyncio
from typing import Any, AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ModelInfo, ServiceInfoResponse
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.core.error_codes import ErrorCodes

class _TestRectifyBrick(RectifyBrick):
    """測試用的 Rectify Brick"""

    @unary_handler
    async def rectify_handler(self, request: RectifyRequest) -> RectifyResponse:
        await asyncio.sleep(0.05)
        if not request.text:
            return RectifyResponse(
                corrected_text="",
                error=ErrorDetail(code=400, message="Text is empty")
            )
        return RectifyResponse(
            corrected_text=request.text[::-1],  # 反轉字串作為校正
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
        )

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        error = ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
        return ServiceInfoResponse(
            service_name="TestRectifyBrick",
            version="9.9.9",
            models=[
                ModelInfo(
                    model_id="rectify-test",
                    version="1.0",
                    supported_languages=["zh", "en"],
                    support_streaming=False,
                    description="test",
                )
            ],
            error=error,
        )

@pytest.mark.asyncio
async def test_async_grpc_server_startup() -> None:
    """測試異步 gRPC 伺服器啟動"""
    print("測試異步 gRPC 伺服器啟動...")

    llm_brick = _TestRectifyBrick()
    server = GrpcServer(port=50057)
    server.register_service(llm_brick)

    assert len(server._pending_bricks) > 0
    assert server.port == 50057

    print("✓ 伺服器建立成功")

@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
    rectify_brick = _TestRectifyBrick(verbose=False)
    server = GrpcServer(port=50058)
    server.register_service(rectify_brick)
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
async def grpc_client(grpc_server: Any) -> AsyncIterator[_TestRectifyBrick]:
    client_brick = _TestRectifyBrick.toGrpcClient(
        remote_address="127.0.0.1:50058", verbose=False
    )
    yield client_brick

@pytest.mark.asyncio
async def test_unary(grpc_client: _TestRectifyBrick) -> None:
    request = RectifyRequest(text="abcDEF", client_id="cli", session_id="s1", request_id="r1", source_language="en")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.corrected_text == "FEDcba"
    assert response.error.code == ErrorCodes.SUCCESS

@pytest.mark.asyncio
async def test_unary_empty_text(grpc_client: _TestRectifyBrick) -> None:
    request = RectifyRequest(text="", client_id="cli", session_id="s1", request_id="r1", source_language="en")
    response = await grpc_client.run_unary(request)
    assert response.error.code == ErrorCodes.BAD_REQUEST
    assert response.corrected_text == ""

@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestRectifyBrick) -> None:
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestRectifyBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)
    assert info.models[0].model_id == "rectify-test"
