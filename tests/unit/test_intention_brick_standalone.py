"""
IntentionBrick 單機版功能測試

此測試文件展示 IntentionBrick 在單機模式下的各種使用方式，
為開發人員提供清晰的使用範例和最佳實踐。

注意：IntentionBrick 支援本地和 gRPC 兩種模式：
- 本地模式：直接創建實例 `brick = IntentionBrick()`
- gRPC 模式：使用 `IntentionBrick.toGrpcClient(address)` 創建客戶端
兩種模式的 API 完全相同，可以無縫切換。
"""

import asyncio
import pytest

from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.intention_types import (
    IntentionRequest,
    IntentionResponse,
    IntentionResult,
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ModelInfo,
    ServiceInfoResponse,
)
from llmbrick.core.error_codes import ErrorCodes

class SimpleIntentionBrick(IntentionBrick):
    """
    簡單的 IntentionBrick 實作
    展示基本的 unary 和 get_service_info 功能
    """

    @unary_handler
    async def echo_intention(self, request: IntentionRequest) -> IntentionResponse:
        await asyncio.sleep(0.01)
        return IntentionResponse(
            results=[
                IntentionResult(intent_category="echo", confidence=0.99)
            ],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

    @get_service_info_handler
    async def service_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleIntentionBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="echo-v1",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=False,
                    description="Simple intention service",
                )
            ],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

@pytest.mark.asyncio
async def test_simple_unary():
    """測試簡單 unary handler"""
    brick = SimpleIntentionBrick(verbose=False)
    request = IntentionRequest(text="test", client_id="cid")
    response = await brick.run_unary(request)
    assert response.error.code == ErrorCodes.SUCCESS
    assert response.results[0].intent_category == "echo"
    assert response.results[0].confidence == 0.99

@pytest.mark.asyncio
async def test_service_info():
    """測試 get_service_info handler"""
    brick = SimpleIntentionBrick(verbose=False)
    info = await brick.run_get_service_info()
    assert info.service_name == "SimpleIntentionBrick"
    assert info.version == "1.0.0"
    assert len(info.models) == 1
    assert info.models[0].model_id == "echo-v1"

def test_handler_registration():
    """測試 handler 註冊機制"""
    brick = SimpleIntentionBrick(verbose=False)
    assert brick._unary_handler is not None
    assert brick._get_service_info_handler is not None

@pytest.mark.asyncio
async def test_not_implemented_handlers():
    """測試未實現的 handler"""
    class PartialIntentionBrick(IntentionBrick):
        @unary_handler
        async def only_unary(self, request: IntentionRequest) -> IntentionResponse:
            return IntentionResponse(
                results=[IntentionResult(intent_category="only", confidence=1.0)],
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
            )

    brick = PartialIntentionBrick(verbose=False)
    request = IntentionRequest(text="test", client_id="cid")
    # unary 應該工作
    response = await brick.run_unary(request)
    assert response.results[0].intent_category == "only"
    # get_service_info 應該拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        await brick.run_get_service_info()

@pytest.mark.asyncio
async def test_error_handling():
    """測試 handler 拋出異常時的行為"""
    class ErrorIntentionBrick(IntentionBrick):
        @unary_handler
        async def error_handler(self, request: IntentionRequest) -> IntentionResponse:
            raise ValueError("Test exception")

    brick = ErrorIntentionBrick(verbose=False)
    request = IntentionRequest(text="test", client_id="cid")
    with pytest.raises(ValueError):
        await brick.run_unary(request)