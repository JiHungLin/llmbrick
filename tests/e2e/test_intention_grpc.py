"""
Intention Brick gRPC 功能測試
"""

import asyncio
from typing import AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.core.brick import get_service_info_handler, unary_handler
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ModelInfo,
    ServiceInfoResponse,
)
from llmbrick.protocols.models.bricks.intention_types import (
    IntentionRequest,
    IntentionResponse,
)
from llmbrick.servers.grpc.server import GrpcServer


class _TestIntentionBrick(IntentionBrick):
    """測試用的 Intention Brick"""

    @unary_handler
    async def unary_handler(self, request: IntentionRequest) -> IntentionResponse:
        await asyncio.sleep(0.1)
        # 回傳 results 欄位，模擬意圖判斷
        from llmbrick.protocols.models.bricks.intention_types import IntentionResult

        result = IntentionResult(intent_category="test", confidence=0.88)
        return IntentionResponse(
            results=[result], error=ErrorDetail(code=0, message="No error", detail="")
        )

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        return ServiceInfoResponse(
            service_name="TestIntentionBrick",
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
    intention_brick = _TestIntentionBrick()
    server = GrpcServer(port=50120)
    server.register_service(intention_brick)
    assert server.server is not None
    assert server.port == 50120


@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
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
async def grpc_client(
    grpc_server: AsyncIterator[None],
) -> AsyncIterator[_TestIntentionBrick]:
    client_brick = _TestIntentionBrick.toGrpcClient(remote_address="127.0.0.1:50121")
    yield client_brick
    await client_brick._grpc_channel.close()


@pytest.mark.asyncio
async def test_unary(grpc_client: _TestIntentionBrick) -> None:
    request = IntentionRequest(text="意圖測試", client_id="cid")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert isinstance(response.results, list)
    assert response.results[0].intent_category == "test"
    assert response.results[0].confidence > 0.8


@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestIntentionBrick) -> None:
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestIntentionBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)
