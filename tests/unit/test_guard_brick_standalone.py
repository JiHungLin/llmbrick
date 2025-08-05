"""
GuardBrick 單機版功能測試

此測試文件展示 GuardBrick 在單機模式下的各種使用方式，
為開發人員提供清晰的使用範例和最佳實踐。

注意：GuardBrick 支援本地和 gRPC 兩種模式：
- 本地模式：直接創建實例 `brick = GuardBrick()`
- gRPC 模式：使用 `GuardBrick.toGrpcClient(address)` 創建客戶端
兩種模式的 API 完全相同，可以無縫切換。
"""

import asyncio
import pytest

from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse, GuardResult
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse, ModelInfo
from llmbrick.core.error_codes import ErrorCodes

class SimpleGuardBrick(GuardBrick):
    """
    簡單的 Guard 服務 Brick
    展示基本的 unary 和 get_service_info 功能
    """

    @unary_handler
    async def check_handler(self, request: GuardRequest) -> GuardResponse:
        """簡單意圖檢查處理器"""
        await asyncio.sleep(0.01)  # 模擬處理時間
        is_attack = "attack" in (request.text or "").lower()
        result = GuardResult(
            is_attack=is_attack,
            confidence=0.99 if is_attack else 0.1,
            detail="Detected attack" if is_attack else "Safe"
        )
        return GuardResponse(
            results=[result],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        """服務信息處理器"""
        return ServiceInfoResponse(
            service_name="SimpleGuardBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="guard-v1",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=False,
                    description="Simple guard service"
                )
            ],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

@pytest.mark.asyncio
async def test_simple_guard_unary():
    """測試簡單意圖檢查"""
    brick = SimpleGuardBrick(verbose=False)
    # 正常情境
    request = GuardRequest(text="This is a normal message")
    response = await brick.run_unary(request)
    assert response.error.code == 0
    assert response.results[0].is_attack is False
    # 攻擊情境
    attack_request = GuardRequest(text="This is an attack!")
    attack_response = await brick.run_unary(attack_request)
    assert attack_response.results[0].is_attack is True

@pytest.mark.asyncio
async def test_simple_guard_service_info():
    """測試服務信息獲取"""
    brick = SimpleGuardBrick(verbose=False)
    info = await brick.run_get_service_info()
    assert info.service_name == "SimpleGuardBrick"
    assert info.version == "1.0.0"
    assert len(info.models) == 1
    assert info.models[0].model_id == "guard-v1"

@pytest.mark.asyncio
async def test_guard_error_handling():
    """測試錯誤處理機制"""
    class ErrorGuardBrick(GuardBrick):
        @unary_handler
        async def error_handler(self, request: GuardRequest) -> GuardResponse:
            if request.text == "raise":
                raise ValueError("Test exception")
            elif request.text == "error":
                return GuardResponse(
                    results=[],
                    error=ErrorDetail(code=500, message="Business logic error")
                )
            else:
                return GuardResponse(
                    results=[GuardResult(is_attack=False, confidence=1.0, detail="ok")],
                    error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
                )
    brick = ErrorGuardBrick(verbose=False)
    # 正常情境
    normal_request = GuardRequest(text="normal")
    response = await brick.run_unary(normal_request)
    assert response.error.code == 0
    # 業務邏輯錯誤
    error_request = GuardRequest(text="error")
    response = await brick.run_unary(error_request)
    assert response.error.code == 500
    # 例外情境
    exception_request = GuardRequest(text="raise")
    with pytest.raises(ValueError):
        await brick.run_unary(exception_request)

def test_guard_handler_registration():
    """測試處理器註冊機制"""
    brick = SimpleGuardBrick(verbose=False)
    assert brick._unary_handler is not None
    assert brick._get_service_info_handler is not None

@pytest.mark.asyncio
async def test_guard_not_implemented_handlers():
    """測試未實現的 streaming handler"""
    brick = SimpleGuardBrick(verbose=False)
    request = GuardRequest(text="test")
    # output_streaming
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_output_streaming(request):
            pass
    # input_streaming
    with pytest.raises(NotImplementedError):
        await brick.run_input_streaming(iter([request]))
    # bidi_streaming
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_bidi_streaming(iter([request])):
            pass