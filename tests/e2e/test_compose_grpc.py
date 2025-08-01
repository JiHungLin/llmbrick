"""
ComposeBrick gRPC 功能測試
"""

import asyncio
from typing import Any, AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.core.brick import (
    unary_handler,
    output_streaming_handler,
    get_service_info_handler,
)
from llmbrick.protocols.models.bricks.compose_types import (
    ComposeRequest,
    ComposeResponse,
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ModelInfo,
    ServiceInfoResponse,
)
from llmbrick.servers.grpc.server import GrpcServer


class _TestComposeBrick(ComposeBrick):
    """測試用的 Compose Brick"""

    @unary_handler
    async def unary_handler(self, request: ComposeRequest) -> ComposeResponse:
        await asyncio.sleep(0.05)
        error = ErrorDetail(code=0, message="No error")
        return ComposeResponse(
            output={
                "echo": [doc.title for doc in request.input_documents],
                "target_format": request.target_format,
            },
            error=error,
        )

    @output_streaming_handler
    async def output_streaming_handler(
        self, request: ComposeRequest
    ) -> AsyncIterator[ComposeResponse]:
        for idx, doc in enumerate(request.input_documents):
            await asyncio.sleep(0.02)
            error = ErrorDetail(code=0, message="No error")
            yield ComposeResponse(
                output={"index": idx, "title": doc.title},
                error=error,
            )

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        error = ErrorDetail(code=0, message="No error")
        return ServiceInfoResponse(
            service_name="TestComposeBrick",
            version="9.9.9",
            models=[
                ModelInfo(
                    model_id="test-compose",
                    version="1.0",
                    supported_languages=["zh", "en"],
                    support_streaming=True,
                    description="test compose",
                )
            ],
            error=error,
        )


@pytest.mark.asyncio
async def test_async_grpc_server_startup() -> None:
    """測試異步 gRPC 伺服器啟動"""
    print("測試異步 gRPC 伺服器啟動...")

    # 建立測試 Brick
    llm_brick = _TestComposeBrick()

    # 建立伺服器
    server = GrpcServer(port=50057)
    server.register_service(llm_brick)

    # 測試伺服器建立
    assert server.server is not None
    assert server.port == 50057

    print("✓ 伺服器建立成功")


@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
    compose_brick = _TestComposeBrick(verbose=False)
    server = GrpcServer(port=50058)
    server.register_service(compose_brick)
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
async def grpc_client(grpc_server: Any) -> AsyncIterator[_TestComposeBrick]:
    client_brick = _TestComposeBrick.toGrpcClient(
        remote_address="127.0.0.1:50058", verbose=False
    )
    yield client_brick
    await client_brick._grpc_channel.close()


@pytest.mark.asyncio
async def test_unary(grpc_client: _TestComposeBrick) -> None:
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "B", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.output["echo"] == ["A", "B"]
    assert response.output["target_format"] == "json"


@pytest.mark.asyncio
async def test_output_streaming(grpc_client: _TestComposeBrick) -> None:
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "X", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "Y", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="markdown")
    results = []
    async for resp in grpc_client.run_output_streaming(request):
        results.append(resp.output["title"])
    assert results == ["X", "Y"]


@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestComposeBrick) -> None:
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestComposeBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)
    assert info.models[0].model_id == "test-compose"
