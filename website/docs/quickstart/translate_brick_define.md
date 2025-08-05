---
sidebar_position: 8
sidebar_label: 翻譯 TranslateBrick 定義
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/translate_brick_define)

# 定義與使用 TranslateBrick

本教學將說明如何在 LLMBrick 框架中自訂、實作並使用 TranslateBrick，並提供本地端與 gRPC 服務兩種情境的完整範例。內容涵蓋常見方法型態（Unary、Output Streaming、Service Info）之實作與呼叫方式。

## 什麼是 TranslateBrick？

TranslateBrick 是 LLMBrick 框架中專為「翻譯」任務設計的 Brick 類型，適合用來實作各種自訂的翻譯模型或服務。它預設支援多種 RPC 方法型態，並可輕鬆串接至本地或遠端服務。

---

## 1. 實作自訂 TranslateBrick

首先，建立一個繼承自 `TranslateBrick` 的自訂類別，並實作各種方法：

```python
# examples/translate_brick_define/my_brick.py
from typing import AsyncIterator
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.protocols.models.bricks.translate_types import (
    TranslateRequest,
    TranslateResponse,
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo,
)
from llmbrick.core.error_codes import ErrorCodes
from llmbrick.core.brick import (
    unary_handler,
    output_streaming_handler,
    get_service_info_handler,
)

class MyTranslateBrick(TranslateBrick):
    """
    MyTranslateBrick 是一個自訂的 TranslateBrick 實作範例。
    支援 unary、output streaming 與 service info 方法。
    """

    def __init__(
        self,
        model_name: str = "my_translate_model",
        default_target_language: str = "zh",
        verbose: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.default_target_language = default_target_language
        self.verbose = verbose

    @unary_handler
    async def unary_translate(self, request: TranslateRequest) -> TranslateResponse:
        # 單次請求/回應
        text = request.text or ""
        target_lang = request.target_language or self.default_target_language
        if not text:
            return TranslateResponse(
                text="",
                tokens=[],
                language_code=target_lang,
                is_final=True,
                error=ErrorDetail(
                    code=ErrorCodes.PARAMETER_INVALID,
                    message="Input text is required.",
                ),
            )
        # Echo translation (for demo)
        return TranslateResponse(
            text=f"{text} (to {target_lang})",
            tokens=[1, 2, 3],
            language_code=target_lang,
            is_final=True,
            error=ErrorDetail(
                code=ErrorCodes.SUCCESS,
                message="Success",
            ),
        )

    @output_streaming_handler
    async def stream_translate(self, request: TranslateRequest) -> AsyncIterator[TranslateResponse]:
        # 輸出串流，每個單字分段回傳
        text = request.text or ""
        target_lang = request.target_language or self.default_target_language
        if not text:
            yield TranslateResponse(
                text="",
                tokens=[],
                language_code=target_lang,
                is_final=True,
                error=ErrorDetail(
                    code=ErrorCodes.PARAMETER_INVALID,
                    message="Input text is required.",
                ),
            )
            return

        words = text.split()
        for i, word in enumerate(words):
            yield TranslateResponse(
                text=f"{word} (t{i})",
                tokens=[i],
                language_code=target_lang,
                is_final=(i == len(words) - 1),
                error=ErrorDetail(
                    code=ErrorCodes.SUCCESS,
                    message="Success",
                ),
            )

    @get_service_info_handler
    async def service_info(self) -> ServiceInfoResponse:
        # 回傳服務資訊
        model_info = ModelInfo(
            model_id=self.model_name,
            version="1.0",
            supported_languages=["en", "zh"],
            support_streaming=True,
            description="A demo translation model that echoes input text.",
        )
        return ServiceInfoResponse(
            service_name="MyTranslateBrickService",
            version="1.0",
            models=[model_info],
            error=ErrorDetail(
                code=ErrorCodes.SUCCESS,
                message="Success",
            ),
        )
```

---

## 2. 本地端呼叫範例

可直接於 Python 程式中實例化並呼叫 TranslateBrick，適合單元測試或嵌入式應用：

```python
# examples/translate_brick_define/local_use.py
from llmbrick.protocols.models.bricks.translate_types import TranslateRequest
from my_brick import MyTranslateBrick
import asyncio

async def main():
    brick = MyTranslateBrick(model_name="demo_model", default_target_language="zh", verbose=True)

    print("=== Get Service Info ===")
    try:
        service_info = await brick.run_get_service_info()
        print(service_info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n\n=== Unary Method ===")
    try:
        print("Normal case:")
        request = TranslateRequest(
            text="Hello, world!",
            model_id="demo_model",
            target_language="zh",
            client_id="test",
            session_id="s1",
            request_id="r1",
            source_language="en",
        )
        response = await brick.run_unary(request)
        print(response)

        print("\nError case:")
        request = TranslateRequest(
            text="",
            model_id="demo_model",
            target_language="zh",
            client_id="test",
            session_id="s1",
            request_id="r2",
            source_language="en",
        )
        response = await brick.run_unary(request)
        print(response)
    except Exception as e:
        print(f"Error in unary call: {e}")

    print("\n\n=== Output Streaming Method ===")
    try:
        print("Normal case:")
        request = TranslateRequest(
            text="This is a streaming test",
            model_id="demo_model",
            target_language="zh",
            client_id="test",
            session_id="s1",
            request_id="r3",
            source_language="en",
        )
        async for resp in brick.run_output_streaming(request):
            await asyncio.sleep(0.3)
            print(resp)

        print("\nError case:")
        request = TranslateRequest(
            text="",
            model_id="demo_model",
            target_language="zh",
            client_id="test",
            session_id="s1",
            request_id="r4",
            source_language="en",
        )
        async for resp in brick.run_output_streaming(request):
            await asyncio.sleep(0.3)
            print(resp)
    except Exception as e:
        print(f"Error in output streaming: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 常見錯誤處理

- 輸入資料不正確時，會回傳帶有 `error` 欄位的 `TranslateResponse`，可據此進行例外處理。

---

## 3. 以 gRPC 方式提供服務

### 啟動 gRPC 伺服器

將自訂 TranslateBrick 註冊到 gRPC 伺服器，對外提供遠端呼叫：

```python
# examples/translate_brick_define/grpc_server.py
from my_brick import MyTranslateBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50071)
my_brick = MyTranslateBrick(
    model_name="demo_model",
    default_target_language="zh",
    verbose=True,
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    import asyncio
    asyncio.run(grpc_server.start())
```

---

## 4. 以 gRPC Client 呼叫遠端 TranslateBrick

可透過 `MyTranslateBrick.toGrpcClient` 產生遠端代理物件，並以 async 方式呼叫各種方法：

```python
# examples/translate_brick_define/grpc_client.py
from my_brick import MyTranslateBrick
from llmbrick.protocols.models.bricks.translate_types import TranslateRequest

if __name__ == "__main__":
    # 建立 gRPC client
    my_brick = MyTranslateBrick.toGrpcClient(remote_address="127.0.0.1:50071", verbose=False)
    import asyncio

    print("=== Get Service Info ===")
    def run_get_service_info_example():
        async def example():
            service_info = await my_brick.run_get_service_info()
            print(service_info)
        asyncio.run(example())

    run_get_service_info_example()

    print("\n\n=== Unary Method ===")
    def run_unary_example(is_test_error=False):
        async def example():
            request = TranslateRequest(
                text="Hello, gRPC!" if not is_test_error else "",
                model_id="demo_model",
                target_language="zh",
                client_id="test",
                session_id="s1",
                request_id="r1" if not is_test_error else "r2",
                source_language="en",
            )
            response = await my_brick.run_unary(request)
            print(response)
        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)
    print("Error case:")
    run_unary_example(is_test_error=True)

    print("\n\n=== Output Streaming Method ===")
    def run_output_streaming_example(is_test_error=False):
        async def example():
            request = TranslateRequest(
                text="Streaming gRPC test" if not is_test_error else "",
                model_id="demo_model",
                target_language="zh",
                client_id="test",
                session_id="s1",
                request_id="r3" if not is_test_error else "r4",
                source_language="en",
            )
            async for resp in my_brick.run_output_streaming(request):
                await asyncio.sleep(0.3)
                print(resp)
        asyncio.run(example())

    print("Normal case:")
    run_output_streaming_example(is_test_error=False)
    print("Error case:")
    run_output_streaming_example(is_test_error=True)
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

## 7. 完整範例程式碼

請參考 [`examples/translate_brick_define/`](https://github.com/JiHungLin/llmbrick/tree/main/examples/translate_brick_define) 目錄下的完整範例，包含本地端與 gRPC 兩種用法，並涵蓋所有常見方法型態。

---

## 8. 常見問題

- **Q: 如何擴充自訂欄位？**  
  A: 於 `MyTranslateBrick.__init__` 或各方法中自訂屬性與邏輯即可，並可透過 `TranslateRequest` 傳遞自訂欄位。

---

本教學涵蓋了 TranslateBrick 的完整定義、實作與使用流程，適合初學者與進階開發者快速上手 LLMBrick 框架的自訂翻譯模組開發。