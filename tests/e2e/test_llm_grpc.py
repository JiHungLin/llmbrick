"""
LLM Brick gRPC 功能測試
"""
import asyncio
from typing import AsyncIterator
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse
import pytest_asyncio

class _TestLLMBrick(LLMBrick):
    """測試用的 LLM Brick"""
    def __init__(self, default_prompt:str , **kwargs):
        super().__init__(default_prompt=default_prompt, **kwargs)

    @unary_handler
    async def unary_handler(self, request: LLMRequest) -> LLMResponse:
        await asyncio.sleep(0.1)
        # 回傳 text, tokens, is_final
        tokens = list(request.prompt) if request.prompt else []
        return LLMResponse(
            text=f"回應: {request.prompt}",
            tokens=tokens,
            is_final=True
        )

    @output_streaming_handler
    async def output_streaming_handler(self, request: LLMRequest) -> AsyncIterator[LLMResponse]:
        words = ["這", "是", "流式", "回應"]
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)
            yield LLMResponse(
                text=word,
                tokens=[word],
                is_final=(i == len(words) - 1)
            )

    @get_service_info_handler
    async def get_service_info_handler(self):
        await asyncio.sleep(0.01)
        return type("ServiceInfo", (), {
            "service_name": "TestLLMBrick",
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
    llm_brick = _TestLLMBrick(default_prompt="測試助手")
    server = GrpcServer(port=50060)
    server.register_service(llm_brick)
    assert server.server is not None
    assert server.port == 50060

@pytest_asyncio.fixture
async def grpc_server():
    llm_brick = _TestLLMBrick(default_prompt="測試助手")
    server = GrpcServer(port=50061)
    server.register_service(llm_brick)
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
    client_brick = _TestLLMBrick.toGrpcClient(remote_address="127.0.0.1:50061")
    yield client_brick
    await client_brick._grpc_channel.close()

@pytest.mark.asyncio
async def test_unary(grpc_client):
    request = LLMRequest(prompt="單一請求")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert "回應" in response.text
    assert isinstance(response.tokens, list)
    assert response.is_final is True

# @pytest.mark.asyncio
# async def test_output_streaming(grpc_client):
#     stream_req = LLMRequest(prompt="流式請求")
#     results = []
#     async for resp in grpc_client.run_output_streaming(stream_req):
#         results.append(resp.text)
#         assert isinstance(resp.tokens, list)
#     assert results == ["這", "是", "流式", "回應"]

# @pytest.mark.asyncio
# async def test_get_service_info(grpc_client):
#     info = await grpc_client.run_get_service_info()
#     assert info.service_name == "TestLLMBrick"
#     assert info.version == "9.9.9"
#     assert isinstance(info.models, list)