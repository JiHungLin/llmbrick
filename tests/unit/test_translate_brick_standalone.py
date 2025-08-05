"""
TranslateBrick 單機版功能測試

此測試文件展示 TranslateBrick 在單機模式下的各種使用方式，
為開發人員提供清晰的使用範例和最佳實踐。

注意：TranslateBrick 支援本地和 gRPC 兩種模式：
- 本地模式：直接創建實例 `brick = TranslateBrick()`
- gRPC 模式：使用 `TranslateBrick.toGrpcClient(address)` 創建客戶端
兩種模式的 API 完全相同，可以無縫切換。
"""

import asyncio
from typing import AsyncIterator

import pytest

from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.core.brick import (
    unary_handler,
    output_streaming_handler,
    get_service_info_handler,
)
from llmbrick.protocols.models.bricks.translate_types import (
    TranslateRequest,
    TranslateResponse,
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ModelInfo,
    ServiceInfoResponse,
)
from llmbrick.core.error_codes import ErrorCodes

class SimpleTranslateBrick(TranslateBrick):
    """
    簡單的翻譯服務 Brick
    展示基本的 unary、output_streaming 和 get_service_info 功能
    """

    @unary_handler
    async def echo_translate(self, request: TranslateRequest) -> TranslateResponse:
        await asyncio.sleep(0.01)
        return TranslateResponse(
            text=f"{request.text} (translated to {request.target_language})",
            tokens=[1, 2, 3],
            language_code=request.target_language,
            is_final=True,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

    @output_streaming_handler
    async def stream_translate(self, request: TranslateRequest) -> AsyncIterator[TranslateResponse]:
        for i, word in enumerate(request.text.split()):
            await asyncio.sleep(0.01)
            yield TranslateResponse(
                text=f"{word} (t{i})",
                tokens=[i],
                language_code=request.target_language,
                is_final=(i == len(request.text.split()) - 1),
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
            )

    @get_service_info_handler
    async def service_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleTranslateBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="simple-translator",
                    version="1.0.0",
                    supported_languages=["en", "zh"],
                    support_streaming=True,
                    description="Simple streaming translator",
                )
            ],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

@pytest.mark.asyncio
async def test_unary_translate():
    brick = SimpleTranslateBrick(verbose=False)
    request = TranslateRequest(
        text="Hello world",
        model_id="simple-translator",
        target_language="zh",
        client_id="test",
        session_id="s1",
        request_id="r1",
        source_language="en",
    )
    response = await brick.run_unary(request)
    assert response.text.endswith("(translated to zh)")
    assert response.language_code == "zh"
    assert response.is_final
    assert response.error.code == ErrorCodes.SUCCESS

@pytest.mark.asyncio
async def test_output_streaming_translate():
    brick = SimpleTranslateBrick(verbose=False)
    request = TranslateRequest(
        text="Hello world",
        model_id="simple-translator",
        target_language="en",
        client_id="test",
        session_id="s1",
        request_id="r2",
        source_language="zh",
    )
    results = []
    async for resp in brick.run_output_streaming(request):
        results.append(resp.text)
    assert results == ["Hello (t0)", "world (t1)"]

@pytest.mark.asyncio
async def test_get_service_info():
    brick = SimpleTranslateBrick(verbose=False)
    info = await brick.run_get_service_info()
    assert info.service_name == "SimpleTranslateBrick"
    assert info.models[0].model_id == "simple-translator"

@pytest.mark.asyncio
async def test_not_implemented_handlers():
    brick = SimpleTranslateBrick(verbose=False)
    request = TranslateRequest(
        text="test",
        model_id="simple-translator",
        target_language="en",
        client_id="test",
        session_id="s1",
        request_id="r3",
        source_language="zh",
    )
    # input_streaming
    with pytest.raises(NotImplementedError):
        await brick.run_input_streaming(iter([request]))
    # bidi_streaming
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_bidi_streaming(iter([request])):
            pass

@pytest.mark.asyncio
async def test_error_handling():
    class ErrorBrick(TranslateBrick):
        @unary_handler
        async def error_handler(self, request: TranslateRequest) -> TranslateResponse:
            return TranslateResponse(
                text="",
                tokens=[],
                language_code="",
                is_final=True,
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message="Simulated error", detail="Test error"),
            )
    brick = ErrorBrick(verbose=False)
    request = TranslateRequest(
        text="fail",
        model_id="simple-translator",
        target_language="en",
        client_id="test",
        session_id="s1",
        request_id="r4",
        source_language="zh",
    )
    response = await brick.run_unary(request)
    assert response.error.code == ErrorCodes.INTERNAL_ERROR
    assert "Simulated error" in response.error.message