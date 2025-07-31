"""
Retrieval Brick gRPC 功能測試
"""

import asyncio
from typing import AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.core.brick import get_service_info_handler, unary_handler
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ModelInfo,
    ServiceInfoResponse,
)
from llmbrick.protocols.models.bricks.retrieval_types import (
    RetrievalRequest,
    RetrievalResponse,
)
from llmbrick.servers.grpc.server import GrpcServer


class _TestRetrievalBrick(RetrievalBrick):
    """測試用的 Retrieval Brick"""

    @unary_handler
    async def unary_handler(self, request: RetrievalRequest) -> RetrievalResponse:
        await asyncio.sleep(0.1)
        # 回傳 documents 欄位，模擬檢索結果
        from llmbrick.protocols.models.bricks.retrieval_types import Document

        doc = Document(doc_id="doc1", title="標題", snippet="片段", score=0.95)
        return RetrievalResponse(
            documents=[doc], error=ErrorDetail(code=0, message="No error", detail="")
        )

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        return ServiceInfoResponse(
            service_name="TestRetrievalBrick",
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
    retrieval_brick = _TestRetrievalBrick()
    server = GrpcServer(port=50140)
    server.register_service(retrieval_brick)
    assert server.server is not None
    assert server.port == 50140


@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
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
async def grpc_client(
    grpc_server: AsyncIterator[None],
) -> AsyncIterator[_TestRetrievalBrick]:
    client_brick = _TestRetrievalBrick.toGrpcClient(remote_address="127.0.0.1:50141")
    yield client_brick
    await client_brick._grpc_channel.close()


@pytest.mark.asyncio
async def test_unary(grpc_client: _TestRetrievalBrick) -> None:
    request = RetrievalRequest(query="檢索關鍵字", client_id="cid")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert isinstance(response.documents, list)
    assert response.documents[0].doc_id == "doc1"
    assert response.documents[0].score > 0.9


@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestRetrievalBrick) -> None:
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestRetrievalBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)
