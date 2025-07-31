"""
Guard Brick gRPC 功能測試
"""

import asyncio

import pytest
import pytest_asyncio

from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.core.brick import get_service_info_handler, unary_handler
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
)
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse
from llmbrick.servers.grpc.server import GrpcServer


class _TestGuardBrick(GuardBrick):
    """測試用的 Guard Brick"""

    @unary_handler
    async def unary_handler(self, request: GuardRequest) -> GuardResponse:
        await asyncio.sleep(0.1)
        # 回傳 results 欄位，模擬檢查結果
        from llmbrick.protocols.models.bricks.guard_types import GuardResult

        result = GuardResult(
            is_attack=False, confidence=0.99, detail=f"echo: {request.text}"
        )
        return GuardResponse(
            results=[result], error=ErrorDetail(code=0, message="No error", detail="")
        )

    @get_service_info_handler
    async def get_service_info_handler(self):
        await asyncio.sleep(0.01)
        return ServiceInfoResponse(
            service_name="TestGuardBrick",
            version="9.9.9",
            models=[
                {
                    "model_id": "test",
                    "version": "1.0",
                    "supported_languages": ["zh", "en"],
                    "support_streaming": True,
                    "description": "test",
                }
            ],
            error=ErrorDetail(code=0, message="No error"),
        )


@pytest.mark.asyncio
async def test_async_grpc_server_startup():
    """測試異步 gRPC 伺服器啟動"""
    guard_brick = _TestGuardBrick()
    server = GrpcServer(port=50110)
    server.register_service(guard_brick)
    assert server.server is not None
    assert server.port == 50110


@pytest_asyncio.fixture
async def grpc_server():
    guard_brick = _TestGuardBrick()
    server = GrpcServer(port=50111)
    server.register_service(guard_brick)
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
async def grpc_client(grpc_server):
    client_brick = _TestGuardBrick.toGrpcClient(remote_address="127.0.0.1:50111")
    yield client_brick
    await client_brick._grpc_channel.close()


@pytest.mark.asyncio
async def test_unary(grpc_client):
    request = GuardRequest(text="測試內容", client_id="cid")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert isinstance(response.results, list)
    assert response.results[0].detail.startswith("echo")
    assert response.results[0].confidence > 0.9


@pytest.mark.asyncio
async def test_get_service_info(grpc_client):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestGuardBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)
