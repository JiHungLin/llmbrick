"""
LLMBrick 單機版功能測試

此測試文件展示 LLMBrick 在單機模式下的各種使用方式，
為開發人員提供清晰的使用範例和最佳實踐。

注意：LLMBrick 支援本地和 gRPC 兩種模式：
- 本地模式：直接創建實例 `brick = LLMBrick(default_prompt="...")`
- gRPC 模式：使用 `LLMBrick.toGrpcClient(address, default_prompt="...")` 創建客戶端
兩種模式的 API 完全相同，可以無縫切換。
"""

import asyncio
from typing import AsyncIterator

import pytest

from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.core.brick import (
    unary_handler,
    output_streaming_handler,
    get_service_info_handler,
)
from llmbrick.protocols.models.bricks.llm_types import (
    LLMRequest,
    LLMResponse,
)
from llmbrick.protocols.models.bricks.common_types import (
    ServiceInfoResponse,
    ErrorDetail,
    ModelInfo,
)

class SimpleLLMBrick(LLMBrick):
    """
    簡單的 LLM 服務 Brick
    展示基本的 unary、output_streaming 和 get_service_info 功能
    """
    def __init__(self, default_prompt: str = "Say hi", **kwargs):
        super().__init__(default_prompt=default_prompt, **kwargs)

    @unary_handler
    async def echo_unary(self, request: LLMRequest) -> LLMResponse:
        await asyncio.sleep(0.01)
        return LLMResponse(
            text=f"Echo: {request.prompt or self.default_prompt}",
            tokens=["echo"],
            is_final=True,
            error=ErrorDetail(code=0, message="Success"),
        )

    @output_streaming_handler
    async def echo_stream(self, request: LLMRequest) -> AsyncIterator[LLMResponse]:
        for i in range(3):
            await asyncio.sleep(0.01)
            yield LLMResponse(
                text=f"Stream {i}: {request.prompt or self.default_prompt}",
                tokens=[str(i)],
                is_final=(i == 2),
                error=ErrorDetail(code=0, message="Success"),
            )

    @get_service_info_handler
    async def service_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleLLMBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="llm-echo",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=True,
                    description="Simple echo LLM",
                )
            ],
            error=ErrorDetail(code=0, message="Success"),
        )

@pytest.mark.asyncio
async def test_unary():
    brick = SimpleLLMBrick(default_prompt="Hello")
    req = LLMRequest(prompt="Test prompt", context=[])
    resp = await brick.run_unary(req)
    assert resp.text == "Echo: Test prompt"
    assert resp.tokens == ["echo"]
    assert resp.is_final is True
    assert resp.error.code == 0

@pytest.mark.asyncio
async def test_output_streaming():
    brick = SimpleLLMBrick(default_prompt="Hi")
    req = LLMRequest(prompt="Stream test", context=[])
    results = []
    async for resp in brick.run_output_streaming(req):
        results.append((resp.text, resp.tokens))
    assert results == [
        ("Stream 0: Stream test", ["0"]),
        ("Stream 1: Stream test", ["1"]),
        ("Stream 2: Stream test", ["2"]),
    ]

@pytest.mark.asyncio
async def test_get_service_info():
    brick = SimpleLLMBrick(default_prompt="Hi")
    info = await brick.run_get_service_info()
    assert info.service_name == "SimpleLLMBrick"
    assert info.version == "1.0.0"
    assert info.models[0].model_id == "llm-echo"

@pytest.mark.asyncio
async def test_not_implemented_handlers():
    class PartialLLMBrick(LLMBrick):
        @unary_handler
        async def only_unary(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text="Only unary",
                tokens=["only"],
                is_final=True,
                error=ErrorDetail(code=0, message="Success"),
            )

    brick = PartialLLMBrick(default_prompt="X")
    req = LLMRequest(prompt="Y", context=[])

    # output_streaming 未註冊應拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        async for _ in brick.run_output_streaming(req):
            pass

    # get_service_info 未註冊應拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        await brick.run_get_service_info()

@pytest.mark.asyncio
async def test_error_response():
    class ErrorLLMBrick(LLMBrick):
        @unary_handler
        async def error_unary(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text="",
                tokens=[],
                is_final=True,
                error=ErrorDetail(code=500, message="Internal error"),
            )

    brick = ErrorLLMBrick(default_prompt="Z")
    req = LLMRequest(prompt="Err", context=[])
    resp = await brick.run_unary(req)
    assert resp.error.code == 500
    assert "Internal error" in resp.error.message