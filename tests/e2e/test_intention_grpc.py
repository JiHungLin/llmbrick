"""
Intention Brick gRPC 功能測試
"""
import asyncio
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest, IntentionResponse
import pytest_asyncio

class _TestIntentionBrick(IntentionBrick):
    """測試用的 Intention Brick"""

    @unary_handler
    async def unary_handler(self, request: IntentionRequest) -> IntentionResponse:
        await asyncio.sleep(0.1)
        return IntentionResponse(
            data={"echo": request.data, "checked": True}
        )

    @get_service_info_handler
    async def get_service_info_handler(self):
        await asyncio.sleep(0.01)
        return type("ServiceInfo", (), {
            "service_name": "TestIntentionBrick",
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
    intention_brick = _TestIntentionBrick()
    server = GrpcServer(port=50120)
    server.register_service(intention_brick)
    assert server.server is not None
    assert server.port == 50120

@pytest_asyncio.fixture
async def grpc_server():
    intention_brick = _TestIntentionBrick()
    server = GrpcServer(port=50121)
    server.register_service(intention_brick)
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
    client_brick = _TestIntentionBrick.toGrpcClient(remote_address="127.0.0.1:50121")
    yield client_brick
    await client_brick._grpc_channel.close()

@pytest.mark.asyncio
async def test_unary(grpc_client):
    request = IntentionRequest(data={"test": "data"})
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.data["checked"] is True

@pytest.mark.asyncio
async def test_get_service_info(grpc_client):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestIntentionBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)