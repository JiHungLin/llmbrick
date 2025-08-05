---
sidebar_position: 4
sidebar_label: 意圖分類 IntentionBrick 定義
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/intention_brick_define)

# 定義與使用 IntentionBrick

本教學將說明如何在 LLMBrick 框架中自訂、實作並使用意圖分類型 IntentionBrick。內容涵蓋本地端呼叫與 gRPC 服務兩種情境，並針對常見方法型態（Unary、Service Info）提供完整範例與說明。

---

## 1. 什麼是 IntentionBrick？

IntentionBrick 是 LLMBrick 框架中專為「意圖分類」設計的 Brick 類型，適合用來實作各種自然語言意圖辨識、分類等 AI/LLM 功能模組。其介面設計簡潔，專注於單一文本的意圖判斷，並回傳分類結果與信心分數。

---

## 2. 實作自訂 IntentionBrick

首先，建立一個繼承自 `IntentionBrick` 的自訂類別，並實作主要方法：

```python
# examples/intention_brick_define/my_brick.py
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.intention_types import (
    IntentionRequest, IntentionResponse, IntentionResult
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail, ServiceInfoResponse, ModelInfo
)
from llmbrick.core.error_codes import ErrorCodes

class MyIntentionBrick(IntentionBrick):
    """
    自訂意圖分類 Brick，實作簡單的意圖判斷邏輯。
    """
    def __init__(self, model_name: str = "demo_model", res_prefix: str = "my_intention", **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.res_prefix = res_prefix
        # 定義意圖關鍵字對應表
        self.intent_patterns = {
            "你好": "greet",
            "hello": "greet",
            "hi": "greet",
            "再見": "goodbye",
            "bye": "goodbye",
            "查詢": "query",
            "search": "query",
            "幫助": "help",
            "help": "help"
        }

    @unary_handler
    async def process(self, input_data: IntentionRequest) -> IntentionResponse:
        """
        處理輸入文本並返回意圖分類結果
        """
        if not input_data.text:
            return IntentionResponse(
                error=ErrorDetail(
                    code=ErrorCodes.PARAMETER_INVALID,
                    message="Input text is required."
                )
            )
        text = input_data.text.lower()
        found_intent = None
        for pattern, intent in self.intent_patterns.items():
            if pattern in text:
                found_intent = intent
                break
        if found_intent:
            result = IntentionResult(
                intent_category=found_intent,
                confidence=0.9
            )
        else:
            result = IntentionResult(
                intent_category="unknown",
                confidence=0.3
            )
        return IntentionResponse(
            results=[result],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def get_service_info_method(self) -> ServiceInfoResponse:
        """
        回傳服務資訊
        """
        model_info = ModelInfo(
            model_id=self.model_name,
            version="1.0",
            supported_languages=["en", "zh"],
            support_streaming=False,
            description="A simple intention classification model supporting basic intents like greet, goodbye, query, and help."
        )
        return ServiceInfoResponse(
            service_name=f"{self.res_prefix}Service",
            version="1.0",
            models=[model_info],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

---

## 3. 本地端呼叫範例

可直接於 Python 程式中實例化並呼叫 IntentionBrick，適合單元測試或嵌入式應用：

```python
# examples/intention_brick_define/local_use.py
from llmbrick.core.error_codes import ErrorCodes
from my_brick import MyIntentionBrick
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest
import asyncio

async def main():
    # 初始化 IntentionBrick
    my_brick = MyIntentionBrick(
        model_name="demo_model",
        res_prefix="local_test",
        verbose=False
    )

    print("=== Get Service Info ===")
    service_info = await my_brick.run_get_service_info()
    print(service_info)

    print("\n\n=== Normal Cases ===")
    test_texts = [
        "你好，請問一下",  # 預期: greet
        "我想要查詢資料",  # 預期: query
        "謝謝，再見",      # 預期: goodbye
        "我需要幫助",      # 預期: help
        "隨機文本測試"     # 預期: unknown
    ]
    for text in test_texts:
        print(f"\nInput text: {text}")
        request = IntentionRequest(text=text, client_id="test_client")
        response = await my_brick.run_unary(request)
        if response.error and response.error.code != ErrorCodes.SUCCESS:
            print(f"Error: {response.error.message}")
        else:
            result = response.results[0]
            print(f"Intent: {result.intent_category}")
            print(f"Confidence: {result.confidence}")

    print("\n\n=== Error Cases ===")
    # 測試錯誤情況 - 空文本
    request = IntentionRequest(text="", client_id="test_client")
    response = await my_brick.run_unary(request)
    if response.error:
        print(f"Error (expected): {response.error.message}")

    # 測試錯誤情況 - None 文本
    request = IntentionRequest(text=None, client_id="test_client")
    response = await my_brick.run_unary(request)
    if response.error:
        print(f"Error (expected): {response.error.message}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 常見錯誤處理

- 若輸入文本為空或 None，會回傳帶有 `error` 欄位的 `IntentionResponse`，可據此進行例外處理。

---

## 4. 以 gRPC 方式提供服務

### 啟動 gRPC 伺服器

將自訂 IntentionBrick 註冊到 gRPC 伺服器，對外提供遠端呼叫：

```python
# examples/intention_brick_define/grpc_server.py
from my_brick import MyIntentionBrick
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

# 建立 gRPC 伺服器實例
grpc_server = GrpcServer(port=50051)

# 初始化 IntentionBrick
my_brick = MyIntentionBrick(
    model_name="grpc_demo_model",
    res_prefix="grpc_test",
    verbose=True  # 啟用詳細日誌以便於除錯
)

# 註冊服務
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    print("Starting gRPC server on port 50051...")
    try:
        asyncio.run(grpc_server.start())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
```

---

## 5. 以 gRPC Client 呼叫遠端 Brick

可透過 `IntentionBrick.toGrpcClient` 產生遠端代理物件，並以 async 方式呼叫各種方法：

```python
# examples/intention_brick_define/grpc_client.py
from llmbrick.core.error_codes import ErrorCodes
from my_brick import MyIntentionBrick
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest
import asyncio

async def main():
    # 使用 toGrpcClient 建立遠端客戶端
    my_brick = MyIntentionBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        verbose=False
    )

    print("=== Get Service Info ===")
    try:
        service_info = await my_brick.run_get_service_info()
        print(service_info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n\n=== Normal Cases ===")
    test_cases = [
        "你好，我有個問題",      # 預期: greet
        "help me please",       # 預期: help
        "我要查詢訂單資料",      # 預期: query
        "bye bye",             # 預期: goodbye
        "這是測試文本"          # 預期: unknown
    ]
    for text in test_cases:
        try:
            print(f"\nTesting text: {text}")
            request = IntentionRequest(text=text, client_id="grpc_client")
            response = await my_brick.run_unary(request)
            if response.error and response.error.code != ErrorCodes.SUCCESS:
                print(f"Error: {response.error.message}")
            else:
                result = response.results[0]
                print(f"Intent: {result.intent_category}")
                print(f"Confidence: {result.confidence}")
        except Exception as e:
            print(f"Error processing request: {e}")

    print("\n\n=== Error Cases ===")
    # 測試空文本
    try:
        print("\nTesting empty text:")
        request = IntentionRequest(text="", client_id="grpc_client")
        response = await my_brick.run_unary(request)
        print(f"Error (expected): {response.error.message}")
    except Exception as e:
        print(f"Error processing request: {e}")

    # 測試 None 文本
    try:
        print("\nTesting None text:")
        request = IntentionRequest(text=None, client_id="grpc_client")
        response = await my_brick.run_unary(request)
        print(f"Error (expected): {response.error.message}")
    except Exception as e:
        print(f"Error processing request: {e}")

if __name__ == "__main__":
    print("Connecting to gRPC server at 127.0.0.1:50051...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"Client error: {e}")
```

---

## 6. 方法型態總覽

| 方法型態      | 裝飾器                  | 說明                   | 範例呼叫方式                |
|---------------|-------------------------|------------------------|-----------------------------|
| Unary         | `@unary_handler`        | 一次請求/回應          | `await run_unary(request)`  |
| Service Info  | `@get_service_info_handler` | 查詢服務資訊      | `await run_get_service_info()` |

> IntentionBrick 主要支援 Unary 與 Service Info 兩種方法型態，專注於單一文本意圖分類。

---

## 7. 實作建議與最佳實踐

- **型別註記**：建議明確標註所有方法的輸入/輸出型別，提升可讀性與維護性。
- **錯誤處理**：善用 `ErrorDetail` 回傳標準化錯誤資訊，方便前後端協作。
- **非同步設計**：所有方法皆建議使用 async/await，確保高效能與可擴充性。
- **意圖映射**：可依實際需求擴充 `intent_patterns`，或串接更進階的 NLP 模型。

---

## 8. 完整範例程式碼

請參考 [`examples/intention_brick_define/`](https://github.com/JiHungLin/llmbrick/tree/main/examples/intention_brick_define) 目錄下的完整範例，包含本地端與 gRPC 兩種用法，並涵蓋所有常見方法型態。

---

## 9. 常見問題

- **Q: 如何擴充自訂意圖分類邏輯？**  
  A: 可於 `MyIntentionBrick.__init__` 或 `process` 方法中自訂意圖關鍵字、規則，或串接外部 NLP/LLM 模型進行分類。

---

本教學涵蓋了 IntentionBrick 的完整定義、實作與使用流程，適合初學者與進階開發者快速上手 LLMBrick 框架的意圖分類模組開發。