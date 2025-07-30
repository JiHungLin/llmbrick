"""
Rectify Brick gRPC 功能測試
"""
import asyncio
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse
import pytest_asyncio

class _TestRectifyBrick(RectifyBrick):
    """測試用的 Rectify Brick"""

    @unary_handler
    async def unary_handler(self, request: RectifyRequest) -> RectifyResponse:
        await asyncio.sleep(0.1)
        # 回傳 corrected_text 欄位，模擬修正
        return RectifyResponse(
            corrected_text=f"rectified: {request.text}"
        )

    @get_service_info_handler
    async def get_service_info_handler(self):
        await asyncio.sleep(0.01)
        return type("ServiceInfo", (), {
            "service_name": "TestRectifyBrick",
            "version": "9.9.9",
            "models": [{
                "model_id": "test",
                "version": "1.0",
                "supported_languages": ["zh", "en"],
                "support_streaming": False,
                "description": "test"
            }]
        })()

@pytest.mark.asyncio
async def test_async_grpc_server_startup():
    """測試異步 gRPC 伺服器啟動"""
    rectify_brick = _TestRectifyBrick()
    server = GrpcServer(port=50130)
    server.register_service(rectify_brick)
    assert server.server is not None
    assert server.port == 50130

@pytest_asyncio.fixture
async def grpc_server():
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
async def grpc_client(grpc_server):
    client_brick = _TestRectifyBrick.toGrpcClient(remote_address="127.0.0.1:50131")
    yield client_brick
    await client_brick._grpc_channel.close()

@pytest.mark.asyncio
async def test_unary(grpc_client):
    request = RectifyRequest(text="原始句子", client_id="cid")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.corrected_text.startswith("rectified:")

@pytest.mark.asyncio
async def test_get_service_info(grpc_client):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestRectifyBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)