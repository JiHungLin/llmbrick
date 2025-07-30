"""
Retrieval Brick gRPC 功能測試
"""
import asyncio
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse
import pytest_asyncio

class _TestRetrievalBrick(RetrievalBrick):
    """測試用的 Retrieval Brick"""

    @unary_handler
    async def unary_handler(self, request: RetrievalRequest) -> RetrievalResponse:
        await asyncio.sleep(0.1)
        return RetrievalResponse(
            data={"echo": request.data, "retrieved": True}
        )

    @get_service_info_handler
    async def get_service_info_handler(self):
        await asyncio.sleep(0.01)
        return type("ServiceInfo", (), {
            "service_name": "TestRetrievalBrick",
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
    retrieval_brick = _TestRetrievalBrick()
    server = GrpcServer(port=50140)
    server.register_service(retrieval_brick)
    assert server.server is not None
    assert server.port == 50140

@pytest_asyncio.fixture
async def grpc_server():
    retrieval_brick = _TestRetrievalBrick()
    server = GrpcServer(port=50141)
    server.register_service(retrieval_brick)
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
    client_brick = _TestRetrievalBrick.toGrpcClient(remote_address="127.0.0.1:50141")
    yield client_brick
    await client_brick._grpc_channel.close()

@pytest.mark.asyncio
async def test_unary(grpc_client):
    request = RetrievalRequest(data={"test": "data"})
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.data["retrieved"] is True

@pytest.mark.asyncio
async def test_get_service_info(grpc_client):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestRetrievalBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)