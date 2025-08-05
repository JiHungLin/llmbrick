---
sidebar_position: 2
sidebar_label: 防護型 GuardBrick 定義
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/guard_brick_define)

# 定義與使用 GuardBrick

本教學將說明如何在 LLMBrick 框架中自訂、實作並使用防護型 GuardBrick。內容涵蓋本地端呼叫與 gRPC 服務兩種情境，並針對常見方法型態（Unary、Service Info）提供完整範例與說明。

## 什麼是 GuardBrick？

GuardBrick 是 LLMBrick 框架中專為「攻擊偵測」、「內容防護」等場景設計的 Brick 類型。  
它預設支援 `unary`（單次請求/回應）與 `get_service_info`（查詢服務資訊）兩種方法型態，適合用來實作自訂的安全檢查、內容過濾等功能模組。

---

## 1. 實作自訂 GuardBrick

首先，建立一個繼承自 `GuardBrick` 的自訂類別，並實作必要方法：

```python
# examples/guard_brick_define/my_brick.py
from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse, GuardResult
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from llmbrick.core.error_codes import ErrorCodes

class MyGuardBrick(GuardBrick):
    """
    MyGuardBrick 是一個自訂的 GuardBrick 範例，僅支援 unary 與 get_service_info 兩種 handler。
    可自訂靈敏度(sensitivity)與 verbose 參數。
    """
    def __init__(self, sensitivity: float = 0.5, verbose: bool = False, **kwargs):
        """
        :param sensitivity: 攻擊偵測靈敏度 (0~1)
        :param verbose: 是否輸出詳細日誌
        """
        super().__init__(**kwargs)
        self.sensitivity = sensitivity
        self.verbose = verbose

    @unary_handler
    async def check(self, request: GuardRequest) -> GuardResponse:
        """
        檢查輸入文字是否為攻擊，並回傳 GuardResponse。
        """
        try:
            text = (request.text or "").lower()
            is_attack = "attack" in text or "攻擊" in text
            confidence = 0.99 if is_attack else 0.1
            detail = "Detected attack" if is_attack else "Safe"
            # 根據 sensitivity 調整判斷
            if is_attack and confidence < self.sensitivity:
                is_attack = False
                detail = "Below sensitivity threshold"
            result = GuardResult(
                is_attack=is_attack,
                confidence=confidence,
                detail=detail
            )
            if self.verbose:
                print(f"[MyGuardBrick] Input: {text}, is_attack: {is_attack}, confidence: {confidence}, detail: {detail}")
            return GuardResponse(
                results=[result],
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
        except Exception as e:
            return GuardResponse(
                results=[],
                error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message="Internal error", detail=str(e))
            )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        """
        回傳服務資訊。
        """
        return ServiceInfoResponse(
            service_name="MyGuardBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message=f"Sensitivity: {self.sensitivity}, Verbose: {self.verbose}")
        )
```

---

## 2. 本地端呼叫範例

直接於 Python 程式中實例化並呼叫 GuardBrick，適合單元測試或嵌入式應用：

```python
# examples/guard_brick_define/local_use.py
import asyncio
from my_brick import MyGuardBrick
from llmbrick.protocols.models.bricks.guard_types import GuardRequest

async def main():
    brick = MyGuardBrick(sensitivity=0.5, verbose=True)

    print("=== Unary Method ===")
    try:
        print("Normal case:")
        request = GuardRequest(text="This is a normal message.")
        response = await brick.run_unary(request)
        print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")

        print("\nAttack case:")
        request = GuardRequest(text="This is an attack!")
        response = await brick.run_unary(request)
        print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")
    except Exception as e:
        print(f"Error in unary: {e}")

    print("\n=== Get Service Info ===")
    try:
        info = await brick.run_get_service_info()
        print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")
    except Exception as e:
        print(f"Error in get_service_info: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 常見錯誤處理

- 若輸入資料格式不正確，會回傳帶有 `error` 欄位的 `GuardResponse`，可據此進行例外處理。

---

## 3. 以 gRPC 方式提供服務

### 啟動 gRPC 伺服器

將自訂 GuardBrick 註冊到 gRPC 伺服器，對外提供遠端呼叫：

```python
# examples/guard_brick_define/grpc_server.py
from my_brick import MyGuardBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyGuardBrick(sensitivity=0.7, verbose=True)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    import asyncio
    asyncio.run(grpc_server.start())
```

---

## 4. 以 gRPC Client 呼叫遠端 GuardBrick

可透過 `GuardBrick.toGrpcClient` 產生遠端代理物件，並以 async 方式呼叫各種方法：

```python
# examples/guard_brick_define/grpc_client.py
import asyncio
from my_brick import MyGuardBrick
from llmbrick.protocols.models.bricks.guard_types import GuardRequest

async def main():
    client_brick = MyGuardBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        sensitivity=0.7,
        verbose=False
    )

    print("=== Get Service Info ===")
    try:
        info = await client_brick.run_get_service_info()
        print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n=== Unary Method ===")
    try:
        print("Normal case:")
        request = GuardRequest(text="This is a normal message.")
        response = await client_brick.run_unary(request)
        print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")

        print("\nAttack case:")
        request = GuardRequest(text="This is an attack!")
        response = await client_brick.run_unary(request)
        print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")
    except Exception as e:
        print(f"Error in unary: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. 方法型態總覽

| 方法型態      | 裝飾器                    | 說明                 | 範例呼叫方式                |
|---------------|---------------------------|----------------------|-----------------------------|
| Unary         | `@unary_handler`          | 一次請求/回應        | `await run_unary(request)`  |
| Service Info  | `@get_service_info_handler` | 查詢服務資訊        | `await run_get_service_info()` |

---

## 6. 實作建議與最佳實踐

- **型別註記**：建議明確標註所有方法的輸入/輸出型別，提升可讀性與維護性。
- **錯誤處理**：善用 `ErrorDetail` 回傳標準化錯誤資訊，方便前後端協作。
- **非同步設計**：所有方法皆建議使用 async/await，確保高效能與可擴充性。
- **靈敏度參數**：可依需求調整 `sensitivity`，以適應不同攻擊偵測場景。

---

## 7. 完整範例程式碼

請參考 [`examples/guard_brick_define/`](https://github.com/JiHungLin/llmbrick/tree/main/examples/guard_brick_define) 目錄下的完整範例，包含本地端與 gRPC 兩種用法。

---

## 8. 常見問題

- **Q: 如何自訂判斷邏輯？**  
  A: 於 `MyGuardBrick.check` 方法中實作自訂攻擊偵測邏輯，並可根據 `sensitivity` 動態調整判斷標準。

---

本教學涵蓋了 GuardBrick 的完整定義、實作與使用流程，適合初學者與進階開發者快速上手 LLMBrick 框架的安全防護模組開發。