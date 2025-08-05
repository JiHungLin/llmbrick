"""
RetrievalBrick 單機版功能測試

此測試文件展示 RetrievalBrick 在單機模式下的各種使用方式，
為開發人員提供清晰的使用範例和最佳實踐。

注意：RetrievalBrick 支援本地和 gRPC 兩種模式：
- 本地模式：直接創建實例 `brick = RetrievalBrick()`
- gRPC 模式：使用 `RetrievalBrick.toGrpcClient(address)` 創建客戶端
兩種模式的 API 完全相同，可以無縫切換。
"""

import asyncio
import pytest

from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ModelInfo,
    ServiceInfoResponse,
)
from llmbrick.protocols.models.bricks.retrieval_types import (
    RetrievalRequest,
    RetrievalResponse,
    Document,
)
from llmbrick.core.error_codes import ErrorCodes

class SimpleRetrievalBrick(RetrievalBrick):
    """簡單的 RetrievalBrick 實作，展示基本功能"""

    @unary_handler
    async def search(self, request: RetrievalRequest) -> RetrievalResponse:
        await asyncio.sleep(0.01)
        doc = Document(doc_id="d1", title="標題", snippet="內容", score=0.88)
        return RetrievalResponse(
            documents=[doc],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleRetrievalBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="retrieval-v1",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=False,
                    description="Simple retrieval service",
                )
            ],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

@pytest.mark.asyncio
async def test_unary():
    """測試 run_unary 正常情境"""
    brick = SimpleRetrievalBrick()
    req = RetrievalRequest(query="test", client_id="cid")
    resp = await brick.run_unary(req)
    assert resp.error.code == 0
    assert len(resp.documents) == 1
    assert resp.documents[0].doc_id == "d1"

@pytest.mark.asyncio
async def test_get_service_info():
    """測試 run_get_service_info 正常情境"""
    brick = SimpleRetrievalBrick()
    info = await brick.run_get_service_info()
    assert info.service_name == "SimpleRetrievalBrick"
    assert info.version == "1.0.0"
    assert len(info.models) == 1
    assert info.models[0].model_id == "retrieval-v1"

def test_handler_not_implemented():
    """測試未註冊 handler 時應拋出 NotImplementedError"""
    class PartialBrick(RetrievalBrick):
        pass
    brick = PartialBrick()
    req = RetrievalRequest(query="test", client_id="cid")
    with pytest.raises(NotImplementedError):
        asyncio.run(brick.run_unary(req))
    with pytest.raises(NotImplementedError):
        asyncio.run(brick.run_get_service_info())

def test_handler_not_async():
    """測試 handler 非 async 時應拋出 TypeError"""
    class BadBrick(RetrievalBrick):
        @unary_handler
        def bad_search(self, request: RetrievalRequest):
            return RetrievalResponse(documents=[], error=ErrorDetail(code=ErrorCodes.SUCCESS, message="ok"))
    brick = BadBrick()
    req = RetrievalRequest(query="test", client_id="cid")
    with pytest.raises(TypeError):
        asyncio.run(brick.run_unary(req))

@pytest.mark.asyncio
async def test_error_response():
    """測試回傳 error 的情境"""
    class ErrorBrick(RetrievalBrick):
        @unary_handler
        async def search(self, request: RetrievalRequest) -> RetrievalResponse:
            return RetrievalResponse(
                documents=[],
                error=ErrorDetail(code=400, message="Bad request", detail="Invalid query"),
            )
    brick = ErrorBrick()
    req = RetrievalRequest(query="", client_id="cid")
    resp = await brick.run_unary(req)
    assert resp.error.code == 400
    assert "Bad request" in resp.error.message

@pytest.mark.asyncio
async def test_concurrent_requests():
    """測試並發請求處理"""
    class CounterBrick(RetrievalBrick):
        def __init__(self):
            super().__init__()
            self.counter = 0

        @unary_handler
        async def search(self, request: RetrievalRequest) -> RetrievalResponse:
            self.counter += 1
            await asyncio.sleep(0.01)
            return RetrievalResponse(
                documents=[],
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message=f"count={self.counter}"),
            )
    brick = CounterBrick()
    async def make_req():
        req = RetrievalRequest(query="q", client_id="cid")
        return await brick.run_unary(req)
    results = await asyncio.gather(*(make_req() for _ in range(5)))
    assert all(r.error.code == 0 for r in results)
    assert brick.counter == 5