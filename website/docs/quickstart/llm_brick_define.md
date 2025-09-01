---
sidebar_position: 5
sidebar_label: LLMBrick 定義
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/llm_brick_define)

# 定義與使用 LLMBrick

本教學將說明如何在 LLMBrick 框架中自訂、實作並使用 LLMBrick，涵蓋本地端呼叫與 gRPC 服務兩種情境，並針對常見方法型態（Unary、Output Streaming、Service Info）提供完整範例與說明。

---

## 1. 什麼是 LLMBrick？

LLMBrick 是專為語言模型（LLM）應用設計的 Brick 類型，適合用來實作各種自訂的 LLM 功能模組。  
LLMBrick 預設支援 prompt、context、流式回應等常見 LLM 互動模式，並可輕鬆串接至本地或遠端服務。

---

## 2. 實作自訂 LLMBrick

首先，建立一個繼承自 `LLMBrick` 的自訂類別，並實作各種方法：

```python
# examples/llm_brick_define/my_brick.py
from typing import List, AsyncIterator
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse, Context
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse, ModelInfo
from llmbrick.core.error_codes import ErrorCodes
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler

class MyLLMBrick(LLMBrick):
    """
    MyLLMBrick 是 LLMBrick 的自訂範例，展示 echo、流式回應與服務資訊查詢。
    支援 default_prompt、model_id、supported_languages、version、description 等初始化參數。
    """
    def __init__(
        self,
        default_prompt: str = "Say something",
        model_id: str = "my-llm-model",
        supported_languages: List[str] = None,
        version: str = "1.0.0",
        description: str = "A simple LLMBrick example that echoes prompt and streams output.",
        **kwargs
    ):
        super().__init__(default_prompt=default_prompt, **kwargs)
        self.model_id = model_id
        self.supported_languages = supported_languages or ["en", "zh"]
        self.version = version
        self.description = description

    @unary_handler
    async def echo(self, request: LLMRequest) -> LLMResponse:
        """
        單次請求-回應：回傳 prompt 或 default_prompt，tokens 為字串列表。
        """
        prompt = request.prompt or self.default_prompt
        if not isinstance(request.context, list):
            error = ErrorDetail(
                code=ErrorCodes.PARAMETER_INVALID,
                message="context 必須為 List[Context]"
            )
            return LLMResponse(text="", tokens=[], is_final=True, error=error)
        if not prompt:
            error = ErrorDetail(
                code=ErrorCodes.PARAMETER_INVALID,
                message="prompt 不可為空"
            )
            return LLMResponse(text="", tokens=[], is_final=True, error=error)
        tokens = prompt.split()
        return LLMResponse(
            text=f"Echo: {prompt}",
            tokens=tokens,
            is_final=True,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @output_streaming_handler
    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMResponse]:
        """
        單次請求-流式回應：將 prompt 拆成多段流式回傳。
        """
        prompt = request.prompt or self.default_prompt
        if not prompt:
            yield LLMResponse(
                text="",
                tokens=[],
                is_final=True,
                error=ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="prompt 不可為空")
            )
            return
        words = prompt.split()
        for idx, word in enumerate(words):
            yield LLMResponse(
                text=word,
                tokens=[word],
                is_final=(idx == len(words) - 1),
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        """
        回傳本 Brick 的服務資訊。
        """
        model_info = ModelInfo(
            model_id=self.model_id,
            version=self.version,
            supported_languages=self.supported_languages,
            support_streaming=True,
            description=self.description
        )
        return ServiceInfoResponse(
            service_name="MyLLMBrick",
            version=self.version,
            models=[model_info],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

---

## 3. 本地端呼叫範例

直接於 Python 程式中實例化並呼叫 LLMBrick，適合單元測試或嵌入式應用：

```python
# examples/llm_brick_define/local_use.py
import asyncio
from my_brick import MyLLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, Context

async def main():
    brick = MyLLMBrick(default_prompt="Hello LLM", model_id="local-llm", supported_languages=["en", "zh"])

    print("=== Get Service Info ===")
    try:
        info = await brick.run_get_service_info()
        print(info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n=== Unary Method ===")
    try:
        print("Normal case:")
        req = LLMRequest(prompt="Test prompt", context=[Context(role="user", content="Hi")])
        resp = await brick.run_unary(req)
        print(resp)

        print("Error case (empty prompt):")
        req = LLMRequest(prompt="", context=[Context(role="user", content="Hi")])
        resp = await brick.run_unary(req)
        print(resp)

        print("Error case (context type error):")
        req = LLMRequest(prompt="Test", context=None)  # type: ignore
        resp = await brick.run_unary(req)
        print(resp)
    except Exception as e:
        print(f"Error in unary call: {e}")

    print("\n=== Output Streaming Method ===")
    try:
        print("Normal case:")
        req = LLMRequest(prompt="Stream this text", context=[])
        async for resp in brick.run_output_streaming(req):
            await asyncio.sleep(0.2)
            print(resp)

        print("Error case (empty prompt):")
        req = LLMRequest(prompt="", context=[])
        async for resp in brick.run_output_streaming(req):
            await asyncio.sleep(0.2)
            print(resp)
    except Exception as e:
        print(f"Error in output streaming: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 常見錯誤處理

- 輸入資料不正確時，會回傳帶有 `error` 欄位的 `LLMResponse`，可據此進行例外處理。

---

## 4. 以 gRPC 方式提供服務

### 啟動 gRPC 伺服器

將自訂 LLMBrick 註冊到 gRPC 伺服器，對外提供遠端呼叫：

```python
# examples/llm_brick_define/grpc_server.py
from my_brick import MyLLMBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyLLMBrick(
    default_prompt="gRPC default prompt",
    model_id="grpc-llm",
    supported_languages=["en", "zh"],
    version="1.0.0",
    description="gRPC LLMBrick example"
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()
```

---

## 5. 以 gRPC Client 呼叫遠端 LLMBrick

可透過 `LLMBrick.toGrpcClient` 產生遠端代理物件，並以 async 方式呼叫各種方法：

```python
# examples/llm_brick_define/grpc_client.py
from my_brick import MyLLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, Context

if __name__ == "__main__":
    import asyncio

    # 建立 gRPC client
    my_brick = MyLLMBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        default_prompt="gRPC client prompt",
        model_id="grpc-client-llm"
    )

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
                req = LLMRequest(prompt="", context=[Context(role="user", content="")])
            else:
                req = LLMRequest(prompt="Hello from gRPC client", context=[Context(role="user", content="Hi")])
            resp = await my_brick.run_unary(req)
            print(resp)
        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)
    print("Error case:")
    run_unary_example(is_test_error=True)

    print("\n=== Output Streaming Method ===")
    def run_output_streaming_example(is_test_error=False):
        async def example():
            if is_test_error:
                req = LLMRequest(prompt="", context=[])
            else:
                req = LLMRequest(prompt="Stream this via gRPC", context=[])
            async for resp in my_brick.run_output_streaming(req):
                await asyncio.sleep(0.2)
                print(resp)
        asyncio.run(example())

    print("Normal case:")
    run_output_streaming_example(is_test_error=False)
    print("Error case:")
    run_output_streaming_example(is_test_error=True)
```

---

## 6. 方法型態總覽

| 方法型態         | 裝飾器                      | 說明                         | 範例呼叫方式                        |
|------------------|-----------------------------|------------------------------|-------------------------------------|
| Unary            | `@unary_handler`            | 一次請求/回應                | `await run_unary(request)`          |
| Output Streaming | `@output_streaming_handler` | 一次輸入，多次回應            | `async for r in run_output_streaming(request)` |
| Service Info     | `@get_service_info_handler` | 查詢服務資訊                  | `await run_get_service_info()`      |

---

## 7. 實作建議與最佳實踐

- **型別註記**：建議明確標註所有方法的輸入/輸出型別，提升可讀性與維護性。
- **錯誤處理**：善用 `ErrorDetail` 回傳標準化錯誤資訊，方便前後端協作。
- **非同步設計**：所有方法皆建議使用 async/await，確保高效能與可擴充性。
- **流式處理**：流式方法可用於大量資料、長時間任務等場景，善用 async generator。

---

## 8. 完整範例程式碼

請參考 [`examples/llm_brick_define/`](https://github.com/JiHungLin/llmbrick/tree/main/examples/llm_brick_define) 目錄下的完整範例，包含本地端與 gRPC 兩種用法，並涵蓋所有常見方法型態。

---

## 9. 常見問題

- **Q: 如何擴充自訂欄位？**  
  A: 於 `MyLLMBrick.__init__` 或各方法中自訂屬性與邏輯即可，並可透過 `LLMRequest` 的 `prompt`、`context` 傳遞自訂資料。

---

本教學涵蓋了 LLMBrick 的完整定義、實作與使用流程，適合初學者與進階開發者快速上手 LLMBrick 框架的自訂 LLM 模組開發。