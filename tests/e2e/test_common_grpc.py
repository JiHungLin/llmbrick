"""
Common Brick gRPC 功能測試
"""
import asyncio
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, input_streaming_handler, bidi_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ServiceInfoResponse
import pytest_asyncio

class _TestCommonBrick(CommonBrick):
    """測試用的 Common Brick"""

    @unary_handler
    async def unary_handler(self, request: CommonRequest) -> CommonResponse:
        await asyncio.sleep(0.1)
        return CommonResponse(data={
            "echo": request.data,
            "processed": True
        })
    
    @output_streaming_handler
    async def output_streaming_handler(self, request: CommonRequest):
        count = request.data.get("count", 3) if request.data else 3
        for i in range(count):
            await asyncio.sleep(0.05)
            yield CommonResponse(data={
                "index": i,
                "message": f"Stream {i}"
            })

    @input_streaming_handler
    async def input_streaming_handler(self, request_stream) -> CommonResponse:
        # 將所有 request.data["val"] 相加
        total = 0
        async for req in request_stream:
            total += req.data.get("val", 0) if req.data else 0
        await asyncio.sleep(0.05)
        return CommonResponse(data={"sum": total})

    @bidi_streaming_handler
    async def bidi_streaming_handler(self, request_stream):
        # 每收到一個 request，回傳其 data["val"]*2
        async for req in request_stream:
            val = req.data.get("val", 0) if req.data else 0
            await asyncio.sleep(0.02)
            yield CommonResponse(data={"double": val * 2})

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        return ServiceInfoResponse(
            service_name="TestCommonBrick",
            version="9.9.9",
            models=[{
                "model_id": "test",
                "version": "1.0",
                "supported_languages": ["zh", "en"],
                "support_streaming": True,
                "description": "test"
            }]
        )

@pytest.mark.asyncio
async def test_async_grpc_server_startup():
    """測試異步 gRPC 伺服器啟動"""
    print("測試異步 gRPC 伺服器啟動...")
    
    # 建立測試 Brick
    llm_brick = _TestCommonBrick()
    
    # 建立伺服器
    server = GrpcServer(port=50054)
    server.register_service(llm_brick)
    
    # 測試伺服器建立
    assert server.server is not None
    assert server.port == 50054
    
    print("✓ 伺服器建立成功")


# ----------- 以下為 fixture 與小測試函式 -----------
@pytest_asyncio.fixture
async def grpc_server():
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
async def grpc_client(grpc_server) -> _TestCommonBrick:
    client_brick = _TestCommonBrick.toGrpcClient(remote_address="127.0.0.1:50056", verbose=False)
    yield client_brick
    await client_brick._grpc_channel.close()

@pytest.mark.asyncio
async def test_unary(grpc_client: _TestCommonBrick):
    print("== 測試 Unary 方法 ==")
    print(grpc_client)
    request = CommonRequest(data={"test": "data"})
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.data["processed"] is True

# @pytest.mark.asyncio
# async def test_output_streaming(grpc_client: _TestCommonBrick):
#     stream_req = CommonRequest(data={"count": 2})
#     results = []
#     async for resp in grpc_client.run_output_streaming(stream_req):
#         results.append(resp.data["index"])
#     assert results == [0, 1]

# @pytest.mark.asyncio
# async def test_input_streaming(grpc_client: _TestCommonBrick):
#     async def input_stream():
#         for v in [1, 2, 3]:
#             yield CommonRequest(data={"val": v})
#     input_resp = await grpc_client.run_input_streaming(input_stream())
#     assert input_resp.data["sum"] == 6

# @pytest.mark.asyncio
# async def test_bidi_streaming(grpc_client: _TestCommonBrick):
#     async def bidi_stream():
#         for v in [10, 20]:
#             yield CommonRequest(data={"val": v})
#     doubles = []
#     async for resp in grpc_client.run_bidi_streaming(bidi_stream()):
#         doubles.append(resp.data["double"])
#     assert doubles == [20, 40]

@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestCommonBrick):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestCommonBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)

# @pytest.mark.asyncio
# async def test_common_grpc_client():
#     """測試 Common gRPC 客戶端功能"""
#     common_brick = _TestCommonBrick(verbose=False)
#     server = GrpcServer(port=50056)
#     server.register_service(common_brick)
#     server_task = asyncio.create_task(server.start())
#     await asyncio.sleep(0.5)
#     try:
#         client_brick = _TestCommonBrick.toGrpcClient(remote_address="127.0.0.1:50056", verbose=False)
#         request = CommonRequest(data={"test": "data"})
#         response = await client_brick.run_unary(request)
#         assert response is not None
#         assert response.data["processed"] is True
#         # Others methods can be tested similarly

#         # # OutputStreaming
#         # stream_req = CommonRequest(data={"count": 2})
#         # results = []
#         # async for resp in client_brick.run_output_streaming(stream_req):
#         #     results.append(resp.data["index"])
#         # assert results == [0, 1]

#         # # InputStreaming
#         # async def input_stream():
#         #     for v in [1, 2, 3]:
#         #         yield CommonRequest(data={"val": v})
#         # input_resp = await client_brick.run_input_streaming(input_stream())
#         # assert input_resp.data["sum"] == 6

#         # # BidiStreaming
#         # async def bidi_stream():
#         #     for v in [10, 20]:
#         #         yield CommonRequest(data={"val": v})
#         # doubles = []
#         # async for resp in client_brick.run_bidi_streaming(bidi_stream()):
#         #     doubles.append(resp.data["double"])
#         # assert doubles == [20, 40]

#         # # GetServiceInfo
#         # info = await client_brick.run_get_service_info()
#         # assert info["service_name"] == "TestCommonBrick"
#         # assert info["version"] == "9.9.9"
#         # assert isinstance(info["models"], list)

#         await client_brick._grpc_channel.close()
#     finally:
#         await server.stop()
#         server_task.cancel()
#         try:
#             await server_task
#         except asyncio.CancelledError:
#             pass