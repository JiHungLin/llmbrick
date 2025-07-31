"""
Rectify Brick gRPC 功能測試
"""

import asyncio
from typing import AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.core.brick import get_service_info_handler, unary_handler
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo
)
from llmbrick.protocols.models.bricks.rectify_types import (
    RectifyRequest,
    RectifyResponse,
)
from llmbrick.servers.grpc.server import GrpcServer


class _TestRectifyBrick(RectifyBrick):
    """測試用的 Rectify Brick"""

    @unary_handler
    async def unary_handler(self, request: RectifyRequest) -> RectifyResponse:
        await asyncio.sleep(0.1)
        # 回傳 corrected_text 欄位，模擬修正
        return RectifyResponse(
            corrected_text=f"rectified: {request.text}",
            error=ErrorDetail(code=0, message="No error", detail=""),
        )

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        return ServiceInfoResponse(
            service_name="TestRectifyBrick",
            version="9.9.9",
            models=[
                ModelInfo(
                    model_id="test",
                    version="1.0",
                    supported_languages=["zh", "en"],
                    support_streaming=True,
                    description="test",
                )
            ],
            error=ErrorDetail(code=0, message="No error"),
        )


@pytest.mark.asyncio
async def test_async_grpc_server_startup() -> None:
    """測試異步 gRPC 伺服器啟動"""
    rectify_brick = _TestRectifyBrick()
    server = GrpcServer(port=50130)
    server.register_service(rectify_brick)
    assert server.server is not None
    assert server.port == 50130


@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
    rectify_brick = _TestRectifyBrick()
    server = GrpcServer(port=50131)
    server.register_service(rectify_brick)
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
async def grpc_client(grpc_server: AsyncIterator[None]) -> AsyncIterator[_TestRectifyBrick]:
    client_brick = _TestRectifyBrick.toGrpcClient(remote_address="127.0.0.1:50131")
    yield client_brick
    await client_brick._grpc_channel.close()


@pytest.mark.asyncio
async def test_unary(grpc_client: _TestRectifyBrick) -> None:
    request = RectifyRequest(text="原始句子", client_id="cid")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.corrected_text.startswith("rectified:")


@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestRectifyBrick) -> None:
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestRectifyBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)
