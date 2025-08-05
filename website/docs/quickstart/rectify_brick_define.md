---
sidebar_position: 3
sidebar_label: 文本校正 RectifyBrick 定義
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/rectify_brick_define)

# 定義與使用 RectifyBrick

本教學將說明如何在 LLMBrick 框架中自訂、實作並使用 RectifyBrick。內容涵蓋本地端呼叫與 gRPC 服務兩種情境，並針對常見方法型態（Unary、Service Info）提供完整範例與說明。

## 什麼是 RectifyBrick？

RectifyBrick 是 LLMBrick 框架中專為「文本校正」設計的 Brick 類型。適合用來實作各種自訂的校正、轉換、格式化等功能模組。可自訂校正模式、支援語言等初始化參數，並可輕鬆串接至本地或遠端服務。

---

## 1. 實作自訂 RectifyBrick

首先，建立一個繼承自 `RectifyBrick` 的自訂類別，並實作校正邏輯與服務資訊方法：

```python
# examples/rectify_brick_define/my_brick.py
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse, ModelInfo
from llmbrick.core.error_codes import ErrorCodes

class MyRectifyBrick(RectifyBrick):
    """
    MyRectifyBrick 是一個自訂的文本校正 Brick，繼承自 RectifyBrick。
    可自訂校正模式、支援語言等初始化參數。
    """

    def __init__(self, mode: str = "upper", supported_languages=None, description: str = "A simple rectify brick", **kwargs):
        """
        :param mode: 校正模式，預設 upper（可選 lower/reverse）
        :param supported_languages: 支援語言列表
        :param description: 服務描述
        """
        super().__init__(**kwargs)
        self.mode = mode
        self.supported_languages = supported_languages or ["en", "zh"]
        self.description = description

    @unary_handler
    async def rectify_handler(self, request: RectifyRequest) -> RectifyResponse:
        """
        處理單次文本校正請求。
        根據 mode 進行不同的校正處理。
        """
        text = request.text or ""
        if not text:
            return RectifyResponse(
                corrected_text="",
                error=ErrorDetail(code=ErrorCodes.PARAMETER_INVALID, message="Input text is required.")
            )

        if self.mode == "upper":
            corrected = text.upper()
        elif self.mode == "lower":
            corrected = text.lower()
        elif self.mode == "reverse":
            corrected = text[::-1]
        else:
            corrected = text

        return RectifyResponse(
            corrected_text=corrected,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        """
        回傳服務資訊。
        """
        model_info_list = [
            ModelInfo(
                model_id="my_rectify_model",
                version="1.0",
                supported_languages=self.supported_languages,
                support_streaming=False,
                description=self.description
            )
        ]
        return ServiceInfoResponse(
            service_name="MyRectifyBrickService",
            version="1.0",
            models=model_info_list,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

---

## 2. 本地端呼叫範例

直接於 Python 程式中實例化並呼叫 RectifyBrick，適合單元測試或嵌入式應用：

```python
# examples/rectify_brick_define/local_use.py
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest
from my_brick import MyRectifyBrick
import asyncio

async def main():
    # 建立 MyRectifyBrick 實例，可自訂 mode
    brick = MyRectifyBrick(mode="upper", supported_languages=["en", "zh"], description="Demo rectify brick")

    print("=== Get Service Info ===")
    try:
        service_info = await brick.run_get_service_info()
        print(service_info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n\n=== Unary Method ===")
    # 正常案例
    try:
        print("Normal case:")
        request = RectifyRequest(
            text="Hello, World!",
            client_id="cli",
            session_id="s1",
            request_id="r1",
            source_language="en"
        )
        response = await brick.run_unary(request)
        print(response)

        print("\nError case:")
        error_request = RectifyRequest(
            text="",
            client_id="cli",
            session_id="s1",
            request_id="r2",
            source_language="en"
        )
        error_response = await brick.run_unary(error_request)
        print(error_response)
    except Exception as e:
        print(f"Error in unary call: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 常見錯誤處理

- 若輸入 `text` 為空，會回傳帶有 `error` 欄位的 `RectifyResponse`，可據此進行例外處理。

---

## 3. 以 gRPC 方式提供服務

### 啟動 gRPC 伺服器

將自訂 RectifyBrick 註冊到 gRPC 伺服器，對外提供遠端呼叫：

```python
# examples/rectify_brick_define/grpc_server.py
from my_brick import MyRectifyBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyRectifyBrick(
    mode="upper",
    supported_languages=["en", "zh"],
    description="RectifyBrick gRPC server"
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    import asyncio
    asyncio.run(grpc_server.start())
```

---

## 4. 以 gRPC Client 呼叫遠端 RectifyBrick

可透過 `RectifyBrick.toGrpcClient` 產生遠端代理物件，並以 async 方式呼叫各種方法：

```python
# examples/rectify_brick_define/grpc_client.py
from my_brick import MyRectifyBrick
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest

if __name__ == "__main__":
    my_brick = MyRectifyBrick.toGrpcClient(remote_address="127.0.0.1:50051")

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
            if not is_test_error:
                request = RectifyRequest(
                    text="Hello, gRPC!",
                    client_id="cli",
                    session_id="s1",
                    request_id="r1",
                    source_language="en"
                )
            else:
                request = RectifyRequest(
                    text="",
                    client_id="cli",
                    session_id="s1",
                    request_id="r2",
                    source_language="en"
                )
            response = await my_brick.run_unary(request)
            print(response)
        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)
    print("Error case:")
    run_unary_example(is_test_error=True)
```

---

## 5. 方法型態總覽

| 方法型態      | 裝飾器                  | 說明                 | 範例呼叫方式                |
|---------------|-------------------------|----------------------|-----------------------------|
| Unary         | `@unary_handler`        | 一次請求/回應        | `await run_unary(request)`  |
| Service Info  | `@get_service_info_handler` | 查詢服務資訊      | `await run_get_service_info()` |

> RectifyBrick 目前主要支援 Unary 與 Service Info 方法型態。

---

## 6. 實作建議與最佳實踐

- **型別註記**：建議明確標註所有方法的輸入/輸出型別，提升可讀性與維護性。
- **錯誤處理**：善用 `ErrorDetail` 回傳標準化錯誤資訊，方便前後端協作。
- **非同步設計**：所有方法皆建議使用 async/await，確保高效能與可擴充性。
- **自訂模式**：可透過 `mode` 參數自訂校正邏輯（如 upper/lower/reverse）。

---

## 7. 完整範例程式碼

請參考 [`examples/rectify_brick_define/`](https://github.com/JiHungLin/llmbrick/tree/main/examples/rectify_brick_define) 目錄下的完整範例，包含本地端與 gRPC 兩種用法。

---

## 8. 常見問題

- **Q: 如何擴充自訂校正邏輯？**  
  A: 於 `MyRectifyBrick.rectify_handler` 方法中根據 `self.mode` 增加自訂處理分支即可。

- **Q: 如何支援多語言？**  
  A: 於 `supported_languages` 參數傳入語言列表，並於 `service_info_handler` 回傳。

---

本教學涵蓋了 RectifyBrick 的完整定義、實作與使用流程，適合初學者與進階開發者快速上手 LLMBrick 框架的自訂校正模組開發。