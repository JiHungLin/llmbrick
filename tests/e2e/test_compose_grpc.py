"""
Compose Brick gRPC 功能測試
"""
import asyncio
from typing import AsyncIterator
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
import pytest_asyncio

class _TestComposeBrick(ComposeBrick):
    """測試用的 Compose Brick"""

    @unary_handler
    async def unary_handler(self, request: ComposeRequest) -> ComposeResponse:
        await asyncio.sleep(0.1)
        return ComposeResponse(
            data={"echo": request.data, "processed": True}
        )

    @output_streaming_handler
    async def output_streaming_handler(self, request: ComposeRequest) -> AsyncIterator[ComposeResponse]:
        count = request.data.get("count", 3) if request.data else 3
        for i in range(int(count)):
            await asyncio.sleep(0.05)
            yield ComposeResponse(
                data={"index": i, "message": f"Stream {i}"}
            )

    @get_service_info_handler
    async def get_service_info_handler(self):
        await asyncio.sleep(0.01)
        return type("ServiceInfo", (), {
            "service_name": "TestComposeBrick",
            "version": "9.9.9",
            "models": [{
                "model_id": "test",
                "version": "1.0",
                "supported_languages": ["zh", "en"],
                "support_streaming": True,
                "description": "test"
            }]
        })()

@pytest.mark.asyncio
async def test_async_grpc_server_startup():
    """測試異步 gRPC 伺服器啟動"""
    llm_brick = _TestComposeBrick()
    server = GrpcServer(port=50100)
    server.register_service(llm_brick)
    assert server.server is not None
    assert server.port == 50100

@pytest_asyncio.fixture
async def grpc_server():
    compose_brick = _TestComposeBrick()
    server = GrpcServer(port=50101)
    server.register_service(compose_brick)
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
    client_brick = _TestComposeBrick.toGrpcClient(remote_address="127.0.0.1:50101")
    yield client_brick
    await client_brick._grpc_channel.close()

@pytest.mark.asyncio
async def test_unary(grpc_client):
    request = ComposeRequest(data={"test": "data"})
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.data["processed"] is True

@pytest.mark.asyncio
async def test_output_streaming(grpc_client):
    stream_req = ComposeRequest(data={"count": 2})
    results = []
    async for resp in grpc_client.run_output_streaming(stream_req):
        results.append(resp.data["index"])
    assert results == [0, 1]

@pytest.mark.asyncio
async def test_get_service_info(grpc_client):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestComposeBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)