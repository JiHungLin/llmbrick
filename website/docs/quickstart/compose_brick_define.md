---
sidebar_position: 7
sidebar_label: 組合轉換 ComposeBrick 定義
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/compose_brick_define)

# 定義與使用 ComposeBrick

本教學將詳細說明如何在 LLMBrick 框架中自訂、實作並使用 ComposeBrick。內容涵蓋本地端呼叫與 gRPC 服務兩種情境，並針對常見方法型態（Unary、Output Streaming、Service Info）提供完整範例與說明。

---

## 1. 什麼是 ComposeBrick？

ComposeBrick 是 LLMBrick 框架中專為「多文件組合、摘要、格式轉換」等應用場景設計的 Brick 類型。它支援多種 RPC 方法型態，並可自訂描述前綴（desc_prefix）與預設格式（default_format），適合用於文件彙整、批次處理等需求。

---

## 2. 實作自訂 ComposeBrick

首先，建立一個繼承自 `ComposeBrick` 的自訂類別，並實作各種方法：

```python
# examples/compose_brick_define/my_brick.py
from typing import AsyncIterator
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.core.error_codes import ErrorCodes

class MyComposeBrick(ComposeBrick):
    """
    MyComposeBrick 是一個自訂的 ComposeBrick 範例，展示 unary、output_streaming、get_service_info 三種模式。
    支援自訂描述前綴(desc_prefix)與預設格式(default_format)。
    """

    def __init__(self, desc_prefix: str = "ComposeResult", default_format: str = "json", **kwargs):
        super().__init__(**kwargs)
        self.desc_prefix = desc_prefix
        self.default_format = default_format

    @unary_handler
    async def unary_process(self, request: ComposeRequest) -> ComposeResponse:
        try:
            count = len(request.input_documents)
            fmt = request.target_format or self.default_format
            return ComposeResponse(
                output={
                    "desc": f"{self.desc_prefix}: 共 {count} 筆文件, 格式: {fmt}",
                    "count": count,
                    "format": fmt
                },
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
        except Exception as e:
            return ComposeResponse(
                output={},
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message=f"Error: {e}")
            )

    @output_streaming_handler
    async def stream_titles(self, request: ComposeRequest) -> AsyncIterator[ComposeResponse]:
        try:
            for idx, doc in enumerate(request.input_documents):
                yield ComposeResponse(
                    output={
                        "desc": f"{self.desc_prefix}: 第{idx+1}筆",
                        "index": idx,
                        "title": getattr(doc, "title", ""),
                        "format": request.target_format or self.default_format
                    },
                    error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
                )
        except Exception as e:
            yield ComposeResponse(
                output={},
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message=f"Error: {e}")
            )

    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="MyComposeBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message=f"Default format: {self.default_format}, Desc prefix: {self.desc_prefix}")
        )
```

---

## 3. 本地端呼叫範例

直接於 Python 程式中實例化並呼叫 ComposeBrick，適合單元測試或嵌入式應用：

```python
# examples/compose_brick_define/local_use.py
import asyncio
from my_brick import MyComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest

async def main():
    brick = MyComposeBrick(desc_prefix="DemoPrefix", default_format="yaml", verbose=False)
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "B", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")

    print("=== Unary Method ===")
    try:
        response = await brick.run_unary(request)
        print(f"Unary result: {response.output.get('count')}, desc: {response.output.get('desc')}, error: {response.error}")
    except Exception as e:
        print(f"Error in unary: {e}")

    print("\n=== Output Streaming Method ===")
    try:
        async for response in brick.run_output_streaming(request):
            print(f"Stream output: {response.output}, error: {response.error}")
    except Exception as e:
        print(f"Error in output streaming: {e}")

    print("\n=== Get Service Info ===")
    try:
        info = await brick.run_get_service_info()
        print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")
    except Exception as e:
        print(f"Error in get_service_info: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. 以 gRPC 方式提供服務

### 啟動 gRPC 伺服器

將自訂 ComposeBrick 註冊到 gRPC 伺服器，對外提供遠端呼叫：

```python
# examples/compose_brick_define/grpc_server.py
from my_brick import MyComposeBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyComposeBrick(desc_prefix="GRPCServer", default_format="xml", verbose=True)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    import asyncio
    asyncio.run(grpc_server.start())
```

---

### gRPC Client 呼叫遠端 ComposeBrick

可透過 `ComposeBrick.toGrpcClient` 產生遠端代理物件，並以 async 方式呼叫各種方法：

```python
# examples/compose_brick_define/grpc_client.py
from my_brick import MyComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest
import asyncio

async def main():
    client_brick = MyComposeBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        desc_prefix="GRPCClient",
        default_format="csv",
        verbose=False
    )
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "B", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")

    print("=== Get Service Info ===")
    try:
        info = await client_brick.run_get_service_info()
        print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n=== Unary Method ===")
    try:
        response = await client_brick.run_unary(request)
        print(f"Unary result: {response.output.get('count')}, desc: {response.output.get('desc')}, error: {response.error}")
    except Exception as e:
        print(f"Error in unary: {e}")

    print("\n=== Output Streaming Method ===")
    try:
        async for response in client_brick.run_output_streaming(request):
            print(f"Stream output: {response.output}, error: {response.error}")
    except Exception as e:
        print(f"Error in output streaming: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. 方法型態總覽

| 方法型態                | 裝飾器                      | 說明                         | 範例呼叫方式                        |
|-------------------------|-----------------------------|------------------------------|-------------------------------------|
| Unary                   | `@unary_handler`            | 一次請求/回應                | `await run_unary(request)`          |
| Output Streaming        | `@output_streaming_handler` | 一次輸入，多次回應            | `async for r in run_output_streaming(request)` |
| Service Info            | `@get_service_info_handler` | 查詢服務資訊                  | `await run_get_service_info()`      |

---

## 6. 實作建議與最佳實踐

- **型別註記**：建議明確標註所有方法的輸入/輸出型別，提升可讀性與維護性。
- **錯誤處理**：善用 `ErrorDetail` 回傳標準化錯誤資訊，方便前後端協作。
- **非同步設計**：所有方法皆建議使用 async/await，確保高效能與可擴充性。
- **串流處理**：串流方法可用於大量資料、長時間任務等場景，善用 async generator。

---

## 7. 常見問題

- **Q: 如何自訂回應格式或描述？**  
  A: 於 `MyComposeBrick.__init__` 設定 `desc_prefix` 與 `default_format`，或於方法中依需求調整。

- **Q: 如何串接多個 ComposeBrick？**  
  A: 可於伺服器端註冊多個 Brick，或於 client 端建立多個代理物件。

---

本教學涵蓋了 ComposeBrick 的定義、實作與使用流程，適合初學者與進階開發者快速上手 LLMBrick 框架的組合型模組開發。完整範例請參考 [`examples/compose_brick_define/`](https://github.com/JiHungLin/llmbrick/tree/main/examples/compose_brick_define) 目錄。