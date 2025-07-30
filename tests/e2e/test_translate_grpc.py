"""
Translate Brick gRPC 功能測試
"""
import asyncio
from typing import AsyncIterator
import pytest
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.translate_types import TranslateRequest, TranslateResponse
from llmbrick.protocols.models.bricks.common_types import ServiceInfoResponse, ErrorDetail
import pytest_asyncio

class _TestTranslateBrick(TranslateBrick):
    """測試用的 Translate Brick"""

    @unary_handler
    async def unary_handler(self, request: TranslateRequest) -> TranslateResponse:
        await asyncio.sleep(0.1)
        # 回傳 text 欄位，模擬翻譯
        return TranslateResponse(
            text=f"翻譯: {request.text}",
            language_code=request.target_language,
            is_final=True,
            tokens=[ch for ch in request.text],  # 模擬 token 化
            error=ErrorDetail(code=0, message="No error", detail="")
        )

    @output_streaming_handler
    async def output_streaming_handler(self, request: TranslateRequest) -> AsyncIterator[TranslateResponse]:
        # 模擬流式翻譯，將 text 拆字逐步回傳
        text = request.text or "流式翻譯"
        for i, ch in enumerate(text):
            await asyncio.sleep(0.05)
            yield TranslateResponse(
                text=ch,
                tokens=[ch],
                language_code=request.target_language,
                is_final=(i == len(text) - 1),
                error=ErrorDetail(code=0, message="No error", detail="")
            )

    @get_service_info_handler
    async def get_service_info_handler(self):
        await asyncio.sleep(0.01)
        return ServiceInfoResponse(
                service_name="TestTranslateBrick",
                version="9.9.9",
                models=[{
                    "model_id": "test",
                    "version": "1.0",
                    "supported_languages": ["zh", "en"],
                    "support_streaming": True,
                    "description": "test"
                }], error=ErrorDetail(code=0, message="No error")
            )

@pytest.mark.asyncio
async def test_async_grpc_server_startup():
    """測試異步 gRPC 伺服器啟動"""
    translate_brick = _TestTranslateBrick()
    server = GrpcServer(port=50150)
    server.register_service(translate_brick)
    assert server.server is not None
    assert server.port == 50150

@pytest_asyncio.fixture
async def grpc_server():
    translate_brick = _TestTranslateBrick()
    server = GrpcServer(port=50151)
    server.register_service(translate_brick)
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
    client_brick = _TestTranslateBrick.toGrpcClient(remote_address="127.0.0.1:50151")
    yield client_brick
    await client_brick._grpc_channel.close()

@pytest.mark.asyncio
async def test_unary(grpc_client):
    request = TranslateRequest(text="Hello", target_language="zh", client_id="cid")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.text.startswith("翻譯:")
    assert response.language_code == "zh"
    assert response.is_final is True

@pytest.mark.asyncio
async def test_output_streaming(grpc_client):
    stream_req = TranslateRequest(text="Hi", target_language="en")
    results = []
    async for resp in grpc_client.run_output_streaming(stream_req):
        results.append(resp.text)
    assert results == list("Hi")

@pytest.mark.asyncio
async def test_get_service_info(grpc_client):
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestTranslateBrick"
    assert info.version == "9.9.9"
    assert isinstance(info.models, list)