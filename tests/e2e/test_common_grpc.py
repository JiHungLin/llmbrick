"""
Common Brick gRPC 功能測試
"""

import asyncio
from typing import Any, AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.common.common import CommonBrick
from llmbrick.core.brick import (
    bidi_streaming_handler,
    get_service_info_handler,
    input_streaming_handler,
    output_streaming_handler,
    unary_handler,
)
from llmbrick.protocols.models.bricks.common_types import (
    CommonRequest,
    CommonResponse,
    ErrorDetail,
    ModelInfo,
    ServiceInfoResponse,
)
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.core.error_codes import ErrorCodes


class _TestCommonBrick(CommonBrick):
    """測試用的 Common Brick"""

    @unary_handler
    async def unary_handler(self, request: CommonRequest) -> CommonResponse:
        await asyncio.sleep(0.1)
        error = ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
        return CommonResponse(
            data={"echo": request.data, "processed": True}, error=error
        )

    @output_streaming_handler
    async def output_streaming_handler(
        self, request: CommonRequest
    ) -> AsyncIterator[CommonResponse]:
        count = request.data.get("count", 3) if request.data else 3
        for i in range(int(count)):
            await asyncio.sleep(0.05)
            error = ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
            yield CommonResponse(
                data={"index": i, "message": f"Stream {i}"}, error=error
            )

    @input_streaming_handler
    async def input_streaming_handler(
        self, request_stream: AsyncIterator[CommonRequest]
    ) -> CommonResponse:
        # 將所有 request.data["val"] 相加
        total = 0
        error = ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
        async for req in request_stream:
            total += int(req.data.get("val", 0)) if req.data else 0
        await asyncio.sleep(0.05)
        return CommonResponse(data={"sum": total}, error=error)

    @bidi_streaming_handler
    async def bidi_streaming_handler(
        self, request_stream: AsyncIterator[CommonRequest]
    ) -> AsyncIterator[CommonResponse]:
        # 每收到一個 request，回傳其 data["val"]*2
        async for req in request_stream:
            val = int(req.data.get("val", 0)) if req.data else 0
            await asyncio.sleep(0.02)
            error = ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
            yield CommonResponse(data={"double": val * 2}, error=error)

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        error = ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
        return ServiceInfoResponse(
            service_name="TestCommonBrick",
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
            error=error,
        )


@pytest.mark.asyncio
async def test_async_grpc_server_startup() -> None:
    """測試異步 gRPC 伺服器啟動"""
    print("測試異步 gRPC 伺服器啟動...")

    # 建立測試 Brick
    llm_brick = _TestCommonBrick()

    # 建立伺服器
    server = GrpcServer(port=50054)
    server.register_service(llm_brick)

    assert len(server._pending_bricks) > 0
    assert server.port == 50054

    print("✓ 伺服器建立成功")


# ----------- 以下為 fixture 與小測試函式 -----------
@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
    common_brick = _TestCommonBrick(verbose=False)
    server = GrpcServer(port=50056)
    server.register_service(common_brick)
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
async def grpc_client(grpc_server: Any) -> AsyncIterator[_TestCommonBrick]:
    client_brick = _TestCommonBrick.toGrpcClient(
        remote_address="127.0.0.1:50056", verbose=False
    )
    yield client_brick


@pytest.mark.asyncio
async def test_unary(grpc_client: _TestCommonBrick) -> None:
    print("== 測試 Unary 方法 ==")
    print(grpc_client)
    request = CommonRequest(data={"test": "data"})
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.data["processed"] is True


@pytest.mark.asyncio
async def test_output_streaming(grpc_client: _TestCommonBrick) -> None:
    stream_req = CommonRequest(data={"count": 2})
    results = []
    async for resp in grpc_client.run_output_streaming(stream_req):
        results.append(resp.data["index"])
    assert results == [0, 1]


@pytest.mark.asyncio
async def test_input_streaming(grpc_client: _TestCommonBrick) -> None:
    async def input_stream() -> AsyncIterator[CommonRequest]:
        for v in [1, 2, 3]:
            yield CommonRequest(data={"val": v})

    input_resp = await grpc_client.run_input_streaming(input_stream())
    assert input_resp.data["sum"] == 6


@pytest.mark.asyncio
async def test_bidi_streaming(grpc_client: _TestCommonBrick) -> None:
    async def bidi_stream() -> AsyncIterator[CommonRequest]:
        for v in [10, 20]:
            yield CommonRequest(data={"val": v})

    doubles = []
    async for resp in grpc_client.run_bidi_streaming(bidi_stream()):
        doubles.append(resp.data["double"])
    assert doubles == [20, 40]


@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestCommonBrick) -> None:
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestCommonBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)
