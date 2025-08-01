"""
CommonBrick 單機版功能測試

此測試文件展示 CommonBrick 在單機模式下的各種使用方式，
為開發人員提供清晰的使用範例和最佳實踐。

注意：CommonBrick 支援本地和 gRPC 兩種模式：
- 本地模式：直接創建實例 `brick = CommonBrick()`
- gRPC 模式：使用 `CommonBrick.toGrpcClient(address)` 創建客戶端
兩種模式的 API 完全相同，可以無縫切換。
"""

import asyncio
from typing import AsyncIterator

import pytest

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


class SimpleEchoBrick(CommonBrick):
    """
    簡單的回音服務 Brick
    展示基本的 unary 和 get_service_info 功能
    """

    @unary_handler
    async def echo_handler(self, request: CommonRequest) -> CommonResponse:
        """簡單回音處理器"""
        await asyncio.sleep(0.01)  # 模擬處理時間
        return CommonResponse(
            data={
                "echo": request.data,
                "message": "Echo response",
                "timestamp": asyncio.get_event_loop().time(),
            },
            error=ErrorDetail(code=0, message="Success"),
        )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        """服務信息處理器"""
        return ServiceInfoResponse(
            service_name="SimpleEchoBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="echo-v1",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=False,
                    description="Simple echo service",
                )
            ],
            error=ErrorDetail(code=0, message="Success"),
        )


class AdvancedProcessingBrick(CommonBrick):
    """
    進階處理服務 Brick
    展示所有四種調用模式的實現
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_count = 0

    @unary_handler
    async def process_handler(self, request: CommonRequest) -> CommonResponse:
        """處理單個請求"""
        self.request_count += 1
        operation = request.data.get("operation", "unknown")
        
        if operation == "add":
            result = request.data.get("a", 0) + request.data.get("b", 0)
        elif operation == "multiply":
            result = request.data.get("a", 1) * request.data.get("b", 1)
        elif operation == "error":
            return CommonResponse(
                data={},
                error=ErrorDetail(
                    code=400, 
                    message="Simulated error", 
                    detail="This is a test error"
                ),
            )
        else:
            result = f"Unknown operation: {operation}"

        return CommonResponse(
            data={
                "result": result,
                "operation": operation,
                "request_count": self.request_count,
            },
            error=ErrorDetail(code=0, message="Success"),
        )

    @output_streaming_handler
    async def stream_numbers_handler(
        self, request: CommonRequest
    ) -> AsyncIterator[CommonResponse]:
        """產生數字流"""
        start = request.data.get("start", 0)
        count = request.data.get("count", 5)
        delay = request.data.get("delay", 0.1)

        for i in range(count):
            await asyncio.sleep(delay)
            yield CommonResponse(
                data={
                    "number": start + i,
                    "index": i,
                    "total": count,
                },
                error=ErrorDetail(code=0, message="Success"),
            )

    @input_streaming_handler
    async def sum_stream_handler(
        self, request_stream: AsyncIterator[CommonRequest]
    ) -> CommonResponse:
        """計算輸入流的總和"""
        total = 0
        count = 0
        
        async for req in request_stream:
            value = req.data.get("value", 0)
            total += value
            count += 1
            await asyncio.sleep(0.01)  # 模擬處理時間

        return CommonResponse(
            data={
                "sum": total,
                "count": count,
                "average": total / count if count > 0 else 0,
            },
            error=ErrorDetail(code=0, message="Success"),
        )

    @bidi_streaming_handler
    async def transform_stream_handler(
        self, request_stream: AsyncIterator[CommonRequest]
    ) -> AsyncIterator[CommonResponse]:
        """雙向流處理：對每個輸入進行轉換並立即回應"""
        async for req in request_stream:
            operation = req.data.get("operation", "double")
            value = req.data.get("value", 0)
            
            await asyncio.sleep(0.05)  # 模擬處理時間
            
            if operation == "double":
                result = value * 2
            elif operation == "square":
                result = value ** 2
            else:
                result = value
                
            yield CommonResponse(
                data={
                    "original": value,
                    "result": result,
                    "operation": operation,
                },
                error=ErrorDetail(code=0, message="Success"),
            )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        """進階服務信息"""
        return ServiceInfoResponse(
            service_name="AdvancedProcessingBrick",
            version="2.0.0",
            models=[
                ModelInfo(
                    model_id="processor-v2",
                    version="2.0.0",
                    supported_languages=["zh", "en", "ja"],
                    support_streaming=True,
                    description="Advanced processing service with streaming support",
                )
            ],
            error=ErrorDetail(code=0, message="Success"),
        )


# ============= 測試案例 =============

@pytest.mark.asyncio
async def test_simple_echo_brick():
    """測試簡單回音服務"""
    brick = SimpleEchoBrick(verbose=False)
    
    # 測試 unary 調用
    request = CommonRequest(data={"message": "Hello, World!"})
    response = await brick.run_unary(request)
    
    assert response.error.code == 0
    assert response.data["echo"]["message"] == "Hello, World!"
    assert "timestamp" in response.data


@pytest.mark.asyncio
async def test_simple_echo_service_info():
    """測試服務信息獲取"""
    brick = SimpleEchoBrick(verbose=False)
    info = await brick.run_get_service_info()
    
    assert info.service_name == "SimpleEchoBrick"
    assert info.version == "1.0.0"
    assert len(info.models) == 1
    assert info.models[0].model_id == "echo-v1"


@pytest.mark.asyncio
async def test_advanced_unary_processing():
    """測試進階單次處理"""
    brick = AdvancedProcessingBrick(verbose=False)
    
    # 測試加法
    add_request = CommonRequest(data={"operation": "add", "a": 10, "b": 5})
    response = await brick.run_unary(add_request)
    assert response.data["result"] == 15
    assert response.data["operation"] == "add"
    
    # 測試乘法
    multiply_request = CommonRequest(data={"operation": "multiply", "a": 3, "b": 4})
    response = await brick.run_unary(multiply_request)
    assert response.data["result"] == 12
    
    # 測試錯誤情況
    error_request = CommonRequest(data={"operation": "error"})
    response = await brick.run_unary(error_request)
    assert response.error.code == 400
    assert "Simulated error" in response.error.message


@pytest.mark.asyncio
async def test_output_streaming():
    """測試輸出流"""
    brick = AdvancedProcessingBrick(verbose=False)
    
    request = CommonRequest(data={"start": 10, "count": 3, "delay": 0.01})
    results = []
    
    async for response in brick.run_output_streaming(request):
        results.append(response.data["number"])
    
    assert results == [10, 11, 12]


@pytest.mark.asyncio
async def test_input_streaming():
    """測試輸入流"""
    brick = AdvancedProcessingBrick(verbose=False)
    
    async def generate_requests():
        for value in [1, 2, 3, 4, 5]:
            yield CommonRequest(data={"value": value})
    
    response = await brick.run_input_streaming(generate_requests())
    
    assert response.data["sum"] == 15
    assert response.data["count"] == 5
    assert response.data["average"] == 3.0


@pytest.mark.asyncio
async def test_bidi_streaming():
    """測試雙向流"""
    brick = AdvancedProcessingBrick(verbose=False)
    
    async def generate_requests():
        operations = [
            {"operation": "double", "value": 5},
            {"operation": "square", "value": 3},
            {"operation": "double", "value": 7},
        ]
        for op in operations:
            yield CommonRequest(data=op)
    
    results = []
    async for response in brick.run_bidi_streaming(generate_requests()):
        results.append({
            "original": response.data["original"],
            "result": response.data["result"],
            "operation": response.data["operation"],
        })
    
    expected = [
        {"original": 5, "result": 10, "operation": "double"},
        {"original": 3, "result": 9, "operation": "square"},
        {"original": 7, "result": 14, "operation": "double"},
    ]
    assert results == expected


@pytest.mark.asyncio
async def test_error_handling():
    """測試錯誤處理機制"""
    
    class ErrorBrick(CommonBrick):
        @unary_handler
        async def error_handler(self, request: CommonRequest) -> CommonResponse:
            error_type = request.data.get("error_type")
            if error_type == "exception":
                raise ValueError("Test exception")
            elif error_type == "error_response":
                return CommonResponse(
                    data={},
                    error=ErrorDetail(code=500, message="Business logic error"),
                )
            else:
                return CommonResponse(
                    data={"status": "ok"},
                    error=ErrorDetail(code=0, message="Success"),
                )
    
    brick = ErrorBrick(verbose=False)
    
    # 測試正常情況
    normal_request = CommonRequest(data={"error_type": "none"})
    response = await brick.run_unary(normal_request)
    assert response.error.code == 0
    
    # 測試業務邏輯錯誤
    error_request = CommonRequest(data={"error_type": "error_response"})
    response = await brick.run_unary(error_request)
    assert response.error.code == 500
    
    # 測試異常情況
    exception_request = CommonRequest(data={"error_type": "exception"})
    with pytest.raises(ValueError):
        await brick.run_unary(exception_request)


@pytest.mark.asyncio
async def test_concurrent_requests():
    """測試並發請求處理"""
    brick = AdvancedProcessingBrick(verbose=False)
    
    async def make_request(value: int) -> int:
        request = CommonRequest(data={"operation": "multiply", "a": value, "b": 2})
        response = await brick.run_unary(request)
        return response.data["result"]
    
    # 並發執行多個請求
    tasks = [make_request(i) for i in range(1, 6)]
    results = await asyncio.gather(*tasks)
    
    assert results == [2, 4, 6, 8, 10]


@pytest.mark.asyncio
async def test_state_management():
    """測試狀態管理"""
    brick = AdvancedProcessingBrick(verbose=False)
    
    # 發送幾個請求，檢查計數器
    for i in range(3):
        request = CommonRequest(data={"operation": "add", "a": i, "b": 1})
        response = await brick.run_unary(request)
        assert response.data["request_count"] == i + 1


def test_brick_initialization():
    """測試 Brick 初始化和配置"""
    
    # 測試預設配置
    brick1 = SimpleEchoBrick()
    assert brick1._verbose is True
    assert brick1.brick_name == "SimpleEchoBrick"
    
    # 測試自定義配置
    brick2 = AdvancedProcessingBrick(verbose=False)
    assert brick2._verbose is False
    assert brick2.request_count == 0


def test_handler_registration():
    """測試處理器註冊機制"""
    brick = AdvancedProcessingBrick(verbose=False)
    
    # 檢查所有處理器都已正確註冊
    assert brick._unary_handler is not None
    assert brick._output_streaming_handler is not None
    assert brick._input_streaming_handler is not None
    assert brick._bidi_streaming_handler is not None
    assert brick._get_service_info_handler is not None


@pytest.mark.asyncio
async def test_not_implemented_handlers():
    """測試未實現的處理器"""
    
    class PartialBrick(CommonBrick):
        @unary_handler
        async def unary_only(self, request: CommonRequest) -> CommonResponse:
            return CommonResponse(
                data={"message": "unary only"},
                error=ErrorDetail(code=0, message="Success"),
            )
    
    brick = PartialBrick(verbose=False)
    
    # unary 應該工作
    request = CommonRequest(data={})
    response = await brick.run_unary(request)
    assert response.data["message"] == "unary only"
    
    # 其他應該拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_output_streaming(request):
            pass
    
    with pytest.raises(NotImplementedError):
        await brick.run_input_streaming(iter([request]))
    
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_bidi_streaming(iter([request])):
            pass

    # get_service_info 應該拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        await brick.run_get_service_info()