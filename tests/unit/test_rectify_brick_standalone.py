"""
RectifyBrick 單機版功能測試

此測試文件展示 RectifyBrick 在單機模式下的各種使用方式，
為開發人員提供清晰的使用範例和最佳實踐。

注意：RectifyBrick 支援本地和 gRPC 兩種模式：
- 本地模式：直接創建實例 `brick = RectifyBrick()`
- gRPC 模式：使用 `RectifyBrick.toGrpcClient(address)` 創建客戶端
兩種模式的 API 完全相同，可以無縫切換。
"""

import asyncio
import pytest

from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ModelInfo, ServiceInfoResponse

class SimpleRectifyBrick(RectifyBrick):
    """
    簡單的文本校正服務 Brick
    展示基本的 unary 和 get_service_info 功能
    """

    @unary_handler
    async def rectify_handler(self, request: RectifyRequest) -> RectifyResponse:
        """簡單校正處理器：將文本轉大寫"""
        await asyncio.sleep(0.01)  # 模擬處理時間
        if not request.text:
            return RectifyResponse(
                corrected_text="",
                error=ErrorDetail(code=400, message="Text is empty")
            )
        return RectifyResponse(
            corrected_text=request.text.upper(),
            error=ErrorDetail(code=0, message="Success")
        )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        """服務信息處理器"""
        return ServiceInfoResponse(
            service_name="SimpleRectifyBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="rectify-v1",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=False,
                    description="Simple rectify service",
                )
            ],
            error=ErrorDetail(code=0, message="Success"),
        )

@pytest.mark.asyncio
async def test_simple_rectify_unary():
    """測試簡單校正服務"""
    brick = SimpleRectifyBrick(verbose=False)
    request = RectifyRequest(text="hello world", client_id="cli", session_id="s1", request_id="r1", source_language="en")
    response = await brick.run_unary(request)
    assert response.error.code == 0
    assert response.corrected_text == "HELLO WORLD"

@pytest.mark.asyncio
async def test_simple_rectify_empty_text():
    """測試空字串校正"""
    brick = SimpleRectifyBrick(verbose=False)
    request = RectifyRequest(text="", client_id="cli", session_id="s1", request_id="r1", source_language="en")
    response = await brick.run_unary(request)
    assert response.error.code == 400
    assert response.corrected_text == ""

@pytest.mark.asyncio
async def test_simple_rectify_service_info():
    """測試服務信息獲取"""
    brick = SimpleRectifyBrick(verbose=False)
    info = await brick.run_get_service_info()
    assert info.service_name == "SimpleRectifyBrick"
    assert info.version == "1.0.0"
    assert len(info.models) == 1
    assert info.models[0].model_id == "rectify-v1"

def test_handler_registration():
    """測試處理器註冊機制"""
    brick = SimpleRectifyBrick(verbose=False)
    assert brick._unary_handler is not None
    assert brick._get_service_info_handler is not None

@pytest.mark.asyncio
async def test_not_implemented_handlers():
    """測試未實現的 streaming handler"""
    brick = SimpleRectifyBrick(verbose=False)
    request = RectifyRequest(text="test", client_id="cli", session_id="s1", request_id="r1", source_language="en")
    with pytest.raises(NotImplementedError):
        await brick.run_input_streaming(iter([request]))
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_output_streaming(request):
            pass
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_bidi_streaming(iter([request])):
            pass