"""
Compose Brick gRPC 功能測試
"""

import asyncio
from typing import Any, AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.core.brick import (
    get_service_info_handler,
    output_streaming_handler,
    unary_handler,
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo
)
from llmbrick.protocols.models.bricks.compose_types import (
    ComposeRequest,
    ComposeResponse,
)
from llmbrick.servers.grpc.server import GrpcServer


class _TestComposeBrick(ComposeBrick):
    """測試用的 Compose Brick"""

    @unary_handler
    async def unary_handler(self, request: ComposeRequest) -> ComposeResponse:
        await asyncio.sleep(0.1)
        # 回傳 output 欄位，echo 輸入的 input_documents
        return ComposeResponse(
            output={
                "echo": [doc.to_dict() for doc in request.input_documents],
                "processed": True,
            }
        )

    @output_streaming_handler
    async def output_streaming_handler(
        self, request: ComposeRequest
    ) -> AsyncIterator[ComposeResponse]:
        # 以 input_documents 數量為 count，若沒給則預設 3
        count = len(request.input_documents) if request.input_documents else 3
        for i in range(int(count)):
            await asyncio.sleep(0.05)
            yield ComposeResponse(
                output={"index": i, "message": f"Stream {i}"},
                error=ErrorDetail(code=0, message="", detail=""),
            )

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        return ServiceInfoResponse(
            service_name="TestComposeBrick",
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
    llm_brick = _TestComposeBrick()
    server = GrpcServer(port=50100)
    server.register_service(llm_brick)
    assert server.server is not None
    assert server.port == 50100


@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
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
async def grpc_client(grpc_server: Any) -> AsyncIterator[_TestComposeBrick]:
    client_brick = _TestComposeBrick.toGrpcClient(remote_address="127.0.0.1:50101")
    yield client_brick
    await client_brick._grpc_channel.close()


@pytest.mark.asyncio
async def test_unary(grpc_client: _TestComposeBrick) -> None:
    # 測試 input_documents 欄位
    from llmbrick.protocols.models.bricks.compose_types import Document

    doc = Document(doc_id="1", title="t", snippet="s", score=1.0)
    request = ComposeRequest(input_documents=[doc], target_format="txt")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.output["processed"] is True
    assert isinstance(response.output["echo"], list)


@pytest.mark.asyncio
async def test_output_streaming(grpc_client: _TestComposeBrick) -> None:
    # 測試 input_documents 數量決定 stream 次數
    from llmbrick.protocols.models.bricks.compose_types import Document

    docs = [
        Document(doc_id=str(i), title=f"t{i}", snippet=f"s{i}", score=1.0)
        for i in range(2)
    ]
    stream_req = ComposeRequest(input_documents=docs, target_format="txt")
    results = []
    async for resp in grpc_client.run_output_streaming(stream_req):
        results.append(resp.output["index"])
    assert results == [0, 1]


@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestComposeBrick) -> None:
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestComposeBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)
