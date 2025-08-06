---
sidebar_position: 6
sidebar_label: 檢索型 RetrievalBrick 定義
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/retrieval_brick_define)

# 定義與使用 RetrievalBrick

本教學將說明如何在 LLMBrick 框架中自訂、實作並使用檢索型 RetrievalBrick。內容涵蓋本地端呼叫與 gRPC 服務兩種情境，並針對常見方法型態（Unary、Service Info）提供完整範例與說明。

## 什麼是 RetrievalBrick？

RetrievalBrick 是 LLMBrick 框架中專為「檢索」任務設計的 Brick 類型，適合用來實作向量查詢、文件檢索等功能。它預設支援標準的查詢請求/回應格式，並可輕鬆串接本地或遠端服務。

---

## 1. 實作自訂 RetrievalBrick

首先，建立一個繼承自 `RetrievalBrick` 的自訂類別，並實作查詢與服務資訊方法：

```python
# examples/retrieval_brick_define/my_brick.py
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse, Document
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse, ModelInfo
from llmbrick.core.error_codes import ErrorCodes

from typing import List, Optional

class MyRetrievalBrick(RetrievalBrick):
    """
    MyRetrievalBrick 是一個自訂的 RetrievalBrick 範例，支援查詢與服務資訊查詢。
    """

    def __init__(self, index_name: str = "default_index", default_docs: Optional[List[Document]] = None, **kwargs):
        super().__init__(**kwargs)
        self.index_name = index_name
        self.default_docs = default_docs or [
            Document(doc_id="1", title="Hello World", snippet="This is a demo document.", score=0.99),
            Document(doc_id="2", title="LLMBrick", snippet="RetrievalBrick example.", score=0.88),
        ]

    @unary_handler
    async def search(self, request: RetrievalRequest) -> RetrievalResponse:
        """
        處理檢索查詢，回傳文件列表。
        """
        if not request.query:
            return RetrievalResponse(
                documents=[],
                error=ErrorDetail(
                    code=ErrorCodes.PARAMETER_INVALID,
                    message="Query string is required."
                )
            )
        # 模擬查詢，實際應用可連接向量資料庫等
        docs = [
            Document(
                doc_id=f"{self.index_name}-{i+1}",
                title=f"Result {i+1} for '{request.query}'",
                snippet=f"Snippet for '{request.query}', doc {i+1}",
                score=1.0 - i * 0.1
            )
            for i in range(2)
        ]
        return RetrievalResponse(
            documents=docs,
            error=ErrorDetail(
                code=ErrorCodes.SUCCESS,
                message="Success"
            )
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        """
        回傳服務資訊。
        """
        return ServiceInfoResponse(
            service_name="MyRetrievalBrick",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="retrieval-demo",
                    version="1.0",
                    supported_languages=["en", "zh"],
                    support_streaming=False,
                    description="A demo retrieval brick."
                )
            ],
            error=ErrorDetail(
                code=ErrorCodes.SUCCESS,
                message="Success"
            )
        )
```

---

## 2. 本地端呼叫範例

直接於 Python 程式中實例化並呼叫 RetrievalBrick，適合單元測試或嵌入式應用：

```python
# examples/retrieval_brick_define/local_use.py
import asyncio
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest
from my_brick import MyRetrievalBrick

async def main():
    brick = MyRetrievalBrick(index_name="local_index")
    print("=== Get Service Info ===")
    try:
        info = await brick.run_get_service_info()
        print(info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n=== Unary Method ===")
    try:
        print("Normal case:")
        req = RetrievalRequest(query="test query", client_id="cid")
        resp = await brick.run_unary(req)
        print(resp)

        print("\nError case (empty query):")
        req = RetrievalRequest(query="", client_id="cid")
        resp = await brick.run_unary(req)
        print(resp)
    except Exception as e:
        print(f"Error in unary call: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 常見錯誤處理

- 若查詢字串為空，會回傳帶有 `error` 欄位的 `RetrievalResponse`，可據此進行例外處理。

---

## 3. 以 gRPC 方式提供服務

### 啟動 gRPC 伺服器

將自訂 RetrievalBrick 註冊到 gRPC 伺服器，對外提供遠端呼叫：

```python
# examples/retrieval_brick_define/grpc_server.py
from my_brick import MyRetrievalBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyRetrievalBrick(
    index_name="grpc_index"
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()
```

---

## 4. 以 gRPC Client 呼叫遠端 RetrievalBrick

可透過 `RetrievalBrick.toGrpcClient` 產生遠端代理物件，並以 async 方式呼叫各種方法：

```python
# examples/retrieval_brick_define/grpc_client.py
from my_brick import MyRetrievalBrick
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest

if __name__ == "__main__":
    import asyncio

    # 建立 gRPC client
    my_brick = MyRetrievalBrick.toGrpcClient(remote_address="127.0.0.1:50051")

    print("=== Get Service Info ===")
    def run_get_service_info_example():
        async def example():
            info = await my_brick.run_get_service_info()
            print(info)
        asyncio.run(example())

    run_get_service_info_example()

    print("\n=== Unary Method ===")
    def run_unary_example(is_test_error=False):
        async def example():
            if is_test_error:
                req = RetrievalRequest(query="", client_id="cid")
            else:
                req = RetrievalRequest(query="test query", client_id="cid")
            resp = await my_brick.run_unary(req)
            print(resp)
        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)
    print("Error case (empty query):")
    run_unary_example(is_test_error=True)
```

---

## 5. 方法型態總覽

| 方法型態      | 裝飾器                    | 說明                 | 範例呼叫方式                  |
|---------------|---------------------------|----------------------|-------------------------------|
| Unary         | `@unary_handler`          | 一次請求/回應        | `await run_unary(request)`    |
| Service Info  | `@get_service_info_handler` | 查詢服務資訊        | `await run_get_service_info()`|

---

## 6. 實作建議與最佳實踐

- **型別註記**：建議明確標註所有方法的輸入/輸出型別，提升可讀性與維護性。
- **錯誤處理**：善用 `ErrorDetail` 回傳標準化錯誤資訊，方便前後端協作。
- **非同步設計**：所有方法皆建議使用 async/await，確保高效能與可擴充性。
- **查詢邏輯**：可依需求串接向量資料庫、全文檢索引擎等，範例僅為模擬。

---

## 7. 完整範例程式碼

請參考 [`examples/retrieval_brick_define/`](https://github.com/JiHungLin/llmbrick/tree/main/examples/retrieval_brick_define) 目錄下的完整範例，包含本地端與 gRPC 兩種用法。

---

## 8. 常見問題

- **Q: 如何自訂查詢邏輯？**  
  A: 於 `search` 方法中實作實際查詢流程，可串接資料庫、API 或其他檢索服務。

- **Q: 如何擴充回傳欄位？**  
  A: 可於 `Document` 或 `RetrievalResponse` 擴充自訂欄位，並於方法中填入對應資料。

---

本教學涵蓋了 RetrievalBrick 的完整定義、實作與使用流程，適合初學者與進階開發者快速上手 LLMBrick 框架的檢索模組開發。