"""
Common Brick gRPC 功能測試
"""
import asyncio
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, input_streaming_handler, bidi_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse

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


@pytest.mark.asyncio
async def test_common_grpc_client():
    """測試 Common gRPC 客戶端功能"""
    common_brick = _TestCommonBrick(verbose=False)
    server = GrpcServer(port=50056)
    server.register_service(common_brick)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    try:
        client_brick = _TestCommonBrick.toGrpcClient(remote_address="127.0.0.1:50056", verbose=False)
        request = CommonRequest(data={"test": "data"})
        response = await client_brick.run_unary(request)
        assert response is not None
        assert response.data["processed"] is True
        # stream_request = CommonRequest(data={"count": 2})
        # stream_responses = []
        # async for chunk in client_brick.run_output_streaming(stream_request):
        #     stream_responses.append(chunk)
        # assert len(stream_responses) == 2
        await client_brick._grpc_channel.close()
    finally:
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass