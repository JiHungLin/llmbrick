"""
ComposeBrick 單機版功能測試

此測試文件展示 ComposeBrick 在單機模式下的各種使用方式，
為開發人員提供清晰的使用範例和最佳實踐。

注意：ComposeBrick 支援本地和 gRPC 兩種模式：
- 本地模式：直接創建實例 `brick = ComposeBrick()`
- gRPC 模式：使用 `ComposeBrick.toGrpcClient(address)` 創建客戶端
兩種模式的 API 完全相同，可以無縫切換。
"""

import asyncio
from typing import AsyncIterator

import pytest

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


class SimpleComposeBrick(ComposeBrick):
    """
    簡單的 Compose 服務 Brick
    展示基本的 unary 和 get_service_info 功能
    """

    @unary_handler
    async def echo_handler(self, request: ComposeRequest) -> ComposeResponse:
        """簡單回音處理器"""
        await asyncio.sleep(0.01)  # 模擬處理時間
        return ComposeResponse(
            output={
                "echo": [doc.title for doc in request.input_documents],
                "target_format": request.target_format,
            },
            error=ErrorDetail(code=0, message="Success"),
        )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        """服務信息處理器"""
        return ServiceInfoResponse(
            service_name="SimpleComposeBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="compose-v1",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=True,
                    description="Simple compose service",
                )
            ],
            error=ErrorDetail(code=0, message="Success"),
        )


class StreamingComposeBrick(ComposeBrick):
    """
    支援 output_streaming 的 Compose 服務 Brick
    """

    @output_streaming_handler
    async def stream_titles_handler(
        self, request: ComposeRequest
    ) -> AsyncIterator[ComposeResponse]:
        """流式回傳每個文件標題"""
        for idx, doc in enumerate(request.input_documents):
            await asyncio.sleep(0.01)
            yield ComposeResponse(
                output={"index": idx, "title": doc.title},
                error=ErrorDetail(code=0, message="Success"),
            )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="StreamingComposeBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success"),
        )


@pytest.mark.asyncio
async def test_simple_compose_unary():
    """測試簡單 ComposeBrick 的 unary 調用"""
    brick = SimpleComposeBrick(verbose=False)
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "B", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")
    response = await brick.run_unary(request)
    assert response.error.code == 0
    assert response.output["echo"] == ["A", "B"]
    assert response.output["target_format"] == "json"


@pytest.mark.asyncio
async def test_simple_compose_service_info():
    """測試服務信息獲取"""
    brick = SimpleComposeBrick(verbose=False)
    info = await brick.run_get_service_info()
    assert info.service_name == "SimpleComposeBrick"
    assert info.version == "1.0.0"
    assert len(info.models) == 1
    assert info.models[0].model_id == "compose-v1"


@pytest.mark.asyncio
async def test_streaming_compose_output_streaming():
    """測試 output_streaming"""
    brick = StreamingComposeBrick(verbose=False)
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "X", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "Y", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="markdown")
    results = []
    async for response in brick.run_output_streaming(request):
        assert response.error.code == 0
        results.append(response.output["title"])
    assert results == ["X", "Y"]


@pytest.mark.asyncio
async def test_not_implemented_handlers():
    """測試未實現的 handler"""
    class PartialComposeBrick(ComposeBrick):
        @unary_handler
        async def only_unary(self, request: ComposeRequest) -> ComposeResponse:
            return ComposeResponse(
                output={"msg": "unary only"},
                error=ErrorDetail(code=0, message="Success"),
            )

    brick = PartialComposeBrick(verbose=False)
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "T", "snippet": "", "score": 1.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")
    # unary 應該工作
    response = await brick.run_unary(request)
    assert response.output["msg"] == "unary only"
    # output_streaming 應該拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_output_streaming(request):
            pass
    # get_service_info 應該拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        await brick.run_get_service_info()


def test_brick_initialization():
    """測試 Brick 初始化和配置"""
    brick1 = SimpleComposeBrick()
    assert brick1._verbose is True
    assert brick1.brick_name == "SimpleComposeBrick"
    brick2 = StreamingComposeBrick(verbose=False)
    assert brick2._verbose is False


def test_handler_registration():
    """測試處理器註冊機制"""
    brick = StreamingComposeBrick(verbose=False)
    assert brick._output_streaming_handler is not None
    assert brick._get_service_info_handler is not None
    # unary handler 未註冊
    assert brick._unary_handler is None