"""
LLM Brick gRPC 功能測試
"""
import asyncio
import time
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse

class TestLLMBrick(LLMBrick):
    """測試用的 LLM Brick"""
    grpc_service_type = "llm"
    def __init__(self, **kwargs):
        super().__init__(default_prompt="測試助手", **kwargs)
    async def unary_handler(self, request: LLMRequest) -> LLMResponse:
        await asyncio.sleep(0.1)
        return LLMResponse(
            text=f"回應: {request.prompt}",
            tokens_used=10,
            model="test-llm"
        )
    async def output_streaming_handler(self, request: LLMRequest):
        words = ["這", "是", "流式", "回應"]
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)
            yield LLMResponse(
                text=word,
                tokens_used=i + 1,
                model="test-llm",
                is_final=(i == len(words) - 1)
            )

@pytest.mark.asyncio
async def test_async_grpc_server_startup():
    """測試異步 gRPC 伺服器啟動"""
    llm_brick = TestLLMBrick()
    server = GrpcServer(port=50054)
    server.register_service(llm_brick)
    assert server.server is not None
    assert server.port == 50054

@pytest.mark.asyncio
async def test_llm_grpc_client():
    """測試 LLM gRPC 客戶端功能"""
    llm_brick = TestLLMBrick()
    server = GrpcServer(port=50055)
    server.register_service(llm_brick)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    try:
        client_brick = LLMBrick.toGrpcClient(
            remote_address="127.0.0.1:50055",
            default_prompt="測試客戶端"
        )
        request = LLMRequest(prompt="測試提示")
        response = await client_brick.run_unary(request)
        assert response is not None
        assert "測試提示" in response.text
        stream_responses = []
        async for chunk in client_brick.run_output_streaming(request):
            stream_responses.append(chunk)
        assert len(stream_responses) > 0
        await client_brick._grpc_channel.close()
    finally:
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

@pytest.mark.asyncio
async def test_performance():
    """測試異步性能"""
    llm_brick = TestLLMBrick()
    server = GrpcServer(port=50057)
    server.register_service(llm_brick)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    try:
        clients = []
        for i in range(3):
            client = LLMBrick.toGrpcClient(
                remote_address="127.0.0.1:50057",
                default_prompt=f"客戶端{i}"
            )
            clients.append(client)
        start_time = time.time()
        async def make_request(client, index):
            request = LLMRequest(prompt=f"並發請求 {index}")
            return await client.run_unary(request)
        tasks = [make_request(clients[i % len(clients)], i) for i in range(5)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        duration = end_time - start_time
        assert len(responses) == 5
        assert all(r is not None for r in responses)
        for client in clients:
            await client._grpc_channel.close()
    finally:
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass