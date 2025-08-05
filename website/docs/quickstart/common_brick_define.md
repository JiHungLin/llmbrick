---
sidebar_position: 1
sidebar_label: 通用型 CommonBrick 定義
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/common_brick_define)


# 定義與使用 CommonBrick

本教學將詳細說明如何在 LLMBrick 框架中自訂、實作並使用通用型 CommonBrick。內容涵蓋本地端呼叫與 gRPC 服務兩種情境，並針對各種常見方法型態（Unary、Input Streaming、Output Streaming、Bidirectional Streaming、Service Info）提供完整範例與說明。

## 什麼是 CommonBrick？

CommonBrick 是 LLMBrick 框架中最基礎、最通用的 Brick 類型，適合用來實作各種自訂的 AI/LLM 功能模組。它預設支援多種 RPC 方法型態，並可輕鬆擴充、串接至本地或遠端服務。

---

## 1. 實作自訂 CommonBrick

首先，建立一個繼承自 `CommonBrick` 的自訂類別，並實作各種方法：

```python
# examples/common_brick_define/my_brick.py
from typing import AsyncIterator
from llmbrick.bricks.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ErrorDetail, ServiceInfoResponse, ModelInfo
from llmbrick.core.error_codes import ErrorCodes
from llmbrick.core.brick import (
    unary_handler,
    input_streaming_handler,
    output_streaming_handler,
    bidi_streaming_handler,
    get_service_info_handler
)

class MyBrick(CommonBrick):
    def __init__(self, my_init_data: str = "", res_prefix: str = "my_brick", **kwargs):
        super().__init__(**kwargs)
        self.my_init_data = my_init_data
        self.res_prefix = res_prefix

    @unary_handler
    async def unary_method(self, input_data: CommonRequest) -> CommonResponse:
        # 單次請求/回應
        output = input_data.data.get("text", "")
        if not output:
            error = ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
            response = CommonResponse(error=error)
        else:
            response = CommonResponse(data={"text": output})
        return response

    @input_streaming_handler
    async def input_streaming_method(self, input_stream: AsyncIterator[CommonRequest]) -> CommonResponse:
        # 輸入串流，回傳單一結果
        has_empty_input = False
        input_data_list = []
        async for input_data in input_stream:
            text = input_data.data.get("text", "")
            if not text:
                has_empty_input = True
            input_data_list.append(text)
        if has_empty_input:
            error = ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
            return CommonResponse(error=error)
        output = "Processed input stream with {} items. Full text: {}".format(len(input_data_list), " ".join(input_data_list))
        return CommonResponse(data={"text": output})

    @output_streaming_handler
    async def output_streaming_method(self, input_data: CommonRequest) -> AsyncIterator[CommonResponse]:
        # 輸入單一請求，回傳串流結果
        text = input_data.data.get("text", "")
        if not text:
            error = ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
            yield CommonResponse(error=error)
            return
        for i in range(5):
            yield CommonResponse(data={"text": f"{text} - part {i + 1}"})

    @bidi_streaming_handler
    async def bidi_streaming_method(self, stream: AsyncIterator[CommonRequest]) -> AsyncIterator[CommonResponse]:
        # 雙向串流
        async for input_data in stream:
            text = input_data.data.get("text", "")
            if not text:
                error = ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
                yield CommonResponse(error=error)
                continue
            yield CommonResponse(data={"text": f"Received: {text}"})

    @get_service_info_handler
    async def get_service_info_method(self) -> ServiceInfoResponse:
        # 回傳服務資訊
        model_info_list = [
            ModelInfo(
                model_id="my_brick_model",
                version="1.0",
                supported_languages=["en", "zh"],
                support_streaming=True,
                description="A model for MyBrick that processes text input and streams output."
            )
        ]
        return ServiceInfoResponse(
            service_name="MyBrickService",
            version="1.0",
            models=model_info_list,
            error=None
        )
```

---

## 2. 本地端呼叫範例

直接於 Python 程式中實例化並呼叫 Brick，適合單元測試或嵌入式應用：

```python
# examples/common_brick_define/local_use.py
from llmbrick.protocols.models.bricks.common_types import CommonRequest
from my_brick import MyBrick
import asyncio

async def main():
    my_brick = MyBrick(my_init_data="Initialization data for local use")

    print("=== Get Service Info ===")
    service_info = await my_brick.run_get_service_info()
    print(service_info)

    print("\n\n=== Unary Method ===")
    request = CommonRequest(data={"text": "Hello, World!"})
    response = await my_brick.run_unary(request)
    print(response)

    print("\n\n=== Input Streaming Method ===")
    async def input_stream():
        for i in range(3):
            yield CommonRequest(data={"text": f"Input {i + 1}"})
    response = await my_brick.run_input_streaming(input_stream())
    print(response)

    print("\n\n=== Output Streaming Method ===")
    request = CommonRequest(data={"text": "Streaming output"})
    async for response in my_brick.run_output_streaming(request):
        print(response)

    print("\n\n=== Bidirectional Streaming Method ===")
    async def bidi_input_stream():
        for i in range(3):
            yield CommonRequest(data={"text": f"Bidirectional input {i + 1}"})
    async for response in my_brick.run_bidi_streaming(bidi_input_stream()):
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### 常見錯誤處理

- 輸入資料不正確時，會回傳帶有 `error` 欄位的 `CommonResponse`，可據此進行例外處理。

---

## 3. 以 gRPC 方式提供服務

### 啟動 gRPC 伺服器

將自訂 Brick 註冊到 gRPC 伺服器，對外提供遠端呼叫：

```python
# examples/common_brick_define/grpc_server.py
from my_brick import MyBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyBrick(
    my_init_data="Initialization data for gRPC server",
    res_prefix="From gRPC server"
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    import asyncio
    asyncio.run(grpc_server.start())
```

---

## 4. 以 gRPC Client 呼叫遠端 Brick

可透過 `CommonBrick.toGrpcClient` 產生遠端代理物件，並以 async 方式呼叫各種方法：

```python
# examples/common_brick_define/grpc_client.py
from my_brick import CommonRequest
from llmbrick.bricks.common import CommonBrick

if __name__ == "__main__":
    my_brick = CommonBrick.toGrpcClient(remote_address="127.0.0.1:50051")
    import asyncio

    print("=== Get Service Info ===")
    async def get_info():
        service_info = await my_brick.run_get_service_info()
        print(service_info)
    asyncio.run(get_info())

    print("\n\n=== Unary Method ===")
    async def unary_example():
        request = CommonRequest(data={"text": "Hello, World!"})
        response = await my_brick.run_unary(request)
        print(response)
    asyncio.run(unary_example())

    # 其餘 Input/Output/Bidirectional Streaming 方法用法同本地端，僅需將 my_brick 換成 gRPC client 代理物件即可
```

---

## 5. 方法型態總覽

| 方法型態                | 裝飾器                  | 說明                         | 範例呼叫方式                |
|-------------------------|-------------------------|------------------------------|-----------------------------|
| Unary                   | `@unary_handler`        | 一次請求/回應                | `await run_unary(request)`  |
| Input Streaming         | `@input_streaming_handler` | 多次輸入，單一回應        | `await run_input_streaming(stream)` |
| Output Streaming        | `@output_streaming_handler` | 一次輸入，多次回應        | `async for r in run_output_streaming(request)` |
| Bidirectional Streaming | `@bidi_streaming_handler`  | 多次輸入，多次回應        | `async for r in run_bidi_streaming(stream)` |
| Service Info            | `@get_service_info_handler` | 查詢服務資訊              | `await run_get_service_info()` |

---

## 6. 實作建議與最佳實踐

- **型別註記**：建議明確標註所有方法的輸入/輸出型別，提升可讀性與維護性。
- **錯誤處理**：善用 `ErrorDetail` 回傳標準化錯誤資訊，方便前後端協作。
- **非同步設計**：所有方法皆建議使用 async/await，確保高效能與可擴充性。
- **串流處理**：串流方法可用於大量資料、長時間任務等場景，善用 async generator。

---

## 7. 完整範例程式碼

請參考 [`examples/common_brick_define/`](https://github.com/JiHungLin/llmbrick/tree/main/examples/common_brick_define) 目錄下的完整範例，包含本地端與 gRPC 兩種用法，並涵蓋所有常見方法型態。

---

## 8. 常見問題

- **Q: 如何擴充自訂欄位？**  
  A: 於 `MyBrick.__init__` 或各方法中自訂屬性與邏輯即可，並可透過 `CommonRequest.data` 傳遞任意結構資料。

- **Q: 如何串接多個 Brick？**  
  A: 可於伺服器端註冊多個 Brick，或於 client 端建立多個代理物件。

---

本教學涵蓋了 CommonBrick 的完整定義、實作與使用流程，適合初學者與進階開發者快速上手 LLMBrick 框架的自訂模組開發。