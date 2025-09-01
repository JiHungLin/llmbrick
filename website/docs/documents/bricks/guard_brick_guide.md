# GuardBrick

本指南詳細說明 [llmbrick/bricks/guard/base_guard.py](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/guard/base_guard.py#L1) 中 GuardBrick 的設計理念、架構、安裝方式、實作範例、API 詳解、常見錯誤與最佳實踐。適合初學者與團隊成員快速上手與深入應用。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

GuardBrick 是 LLMBrick 框架中專為「意圖防護」設計的安全組件，主要解決以下問題：

- **用戶輸入安全檢查**：自動偵測潛在攻擊、惡意內容或不當輸入。
- **標準化安全 API**：提供統一的 gRPC 服務介面，便於微服務集成。
- **可擴展性**：允許自訂檢查邏輯與靈敏度，適應不同應用場景。
- **錯誤與狀態管理**：統一回傳安全檢查結果與錯誤訊息。

### 🔧 核心功能特色

- **僅支援 Unary 與 GetServiceInfo**：專注於單次請求與服務資訊查詢，簡潔高效。
- **gRPC 標準協定**：與多語言、多平台輕鬆整合。
- **自訂靈敏度**：可根據需求調整攻擊偵測靈敏度。
- **易於擴展**：可繼承並自訂檢查邏輯。

---

## 專案結構圖與模組詳解

### 架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── bricks/
│   │   └── guard/
│   │       └── base_guard.py         # GuardBrick 主體
│   ├── protocols/
│   │   ├── grpc/
│   │   │   └── guard/
│   │   │       ├── guard.proto       # gRPC 協定定義
│   │   │       ├── guard_pb2.py      # Protobuf 生成
│   │   │       └── guard_pb2_grpc.py # gRPC 服務存根
│   │   └── models/
│   │       └── bricks/
│   │           └── guard_types.py    # Guard 資料模型
│   └── core/
│       └── brick.py                  # BaseBrick 抽象基礎
├── examples/
│   └── guard_brick_define/
│       ├── my_brick.py               # 自訂 GuardBrick 範例
│       ├── grpc_server.py            # gRPC 服務端範例
│       ├── grpc_client.py            # gRPC 客戶端範例
│       └── local_use.py              # 本地測試範例
```

### 核心模組說明

#### 1. [GuardBrick](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/guard/base_guard.py#L17)
- **職責**：專為安全檢查設計的 Brick，僅支援 `unary` 與 `get_service_info` 兩種 handler。
- **繼承**：自 [BaseBrick](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L1)。
- **限制**：不支援 streaming handler（如 input/output/bidi streaming）。

#### 2. [guard.proto](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/guard/guard.proto#L1)
- **定義 gRPC 服務**：`GuardService`，僅有 `Unary` 與 `GetServiceInfo` 兩個方法。
- **資料結構**：`GuardRequest`, `GuardResponse`, `GuardResult`。

#### 3. [guard_types.py](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/guard_types.py#L1)
- **資料模型**：Python 端的 `GuardRequest`, `GuardResponse`, `GuardResult`，與 Protobuf 對應。

#### 4. 範例程式
- [my_brick.py](https://github.com/JiHungLin/llmbrick/blob/main/examples/guard_brick_define/my_brick.py#L1)：自訂檢查邏輯。
- [grpc_server.py](https://github.com/JiHungLin/llmbrick/blob/main/examples/guard_brick_define/grpc_server.py#L1)：如何啟動 gRPC 服務。
- [grpc_client.py](https://github.com/JiHungLin/llmbrick/blob/main/examples/guard_brick_define/grpc_client.py#L1)：如何呼叫 gRPC 服務。
- [local_use.py](https://github.com/JiHungLin/llmbrick/blob/main/examples/guard_brick_define/local_use.py#L1)：本地直接呼叫。

---

## 安裝與環境設定指南

### 依賴需求

```bash
# 必要依賴
pip install llmbrick grpcio grpcio-tools protobuf
```

### 自動化安裝步驟

1. **安裝 LLMBrick**
   ```bash
   pip install llmbrick
   # 或從源碼安裝
   git clone https://github.com/JiHungLin/llmbrick.git
   cd llmbrick
   pip install -e .
   ```

2. **驗證安裝**
   ```python
   from llmbrick.bricks.guard.base_guard import GuardBrick
   print("✅ GuardBrick 安裝成功！")
   ```

3. **開發環境設定（可選）**
   ```bash
   export LLMBRICK_LOG_LEVEL=INFO
   export LLMBRICK_GRPC_PORT=50051
   ```

---

## 逐步範例：從基礎到進階

### 1. 自訂 GuardBrick 實作

[my_brick.py](https://github.com/JiHungLin/llmbrick/blob/main/examples/guard_brick_define/my_brick.py#L1)
```python
from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse, GuardResult
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from llmbrick.core.error_codes import ErrorCodes

class MyGuardBrick(GuardBrick):
    def __init__(self, sensitivity: float = 0.5, verbose: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.sensitivity = sensitivity
        self.verbose = verbose

    @unary_handler
    async def check(self, request: GuardRequest) -> GuardResponse:
        text = (request.text or "").lower()
        is_attack = "attack" in text or "攻擊" in text
        confidence = 0.99 if is_attack else 0.1
        detail = "Detected attack" if is_attack else "Safe"
        if is_attack and confidence < self.sensitivity:
            is_attack = False
            detail = "Below sensitivity threshold"
        result = GuardResult(is_attack=is_attack, confidence=confidence, detail=detail)
        if self.verbose:
            print(f"[MyGuardBrick] Input: {text}, is_attack: {is_attack}, confidence: {confidence}, detail: {detail}")
        return GuardResponse(results=[result], error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"))

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="MyGuardBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message=f"Sensitivity: {self.sensitivity}, Verbose: {self.verbose}")
        )
```

### 2. 本地測試範例

[local_use.py](https://github.com/JiHungLin/llmbrick/blob/main/examples/guard_brick_define/local_use.py#L1)
```python
import asyncio
from my_brick import MyGuardBrick
from llmbrick.protocols.models.bricks.guard_types import GuardRequest

async def main():
    brick = MyGuardBrick(sensitivity=0.5, verbose=True)

    print("=== Unary Method ===")
    request = GuardRequest(text="This is a normal message.")
    response = await brick.run_unary(request)
    print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")

    request = GuardRequest(text="This is an attack!")
    response = await brick.run_unary(request)
    print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")

    info = await brick.run_get_service_info()
    print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. gRPC 服務端啟動

[grpc_server.py](https://github.com/JiHungLin/llmbrick/blob/main/examples/guard_brick_define/grpc_server.py#L1)
```python
from my_brick import MyGuardBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyGuardBrick(sensitivity=0.7, verbose=True)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    print("🚀 gRPC 服務器啟動中...")
    grpc_server.run()
```

### 4. gRPC 客戶端呼叫

[grpc_client.py](https://github.com/JiHungLin/llmbrick/blob/main/examples/guard_brick_define/grpc_client.py#L1)
```python
import asyncio
from my_brick import MyGuardBrick
from llmbrick.protocols.models.bricks.guard_types import GuardRequest

async def main():
    client_brick = MyGuardBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        sensitivity=0.7,
        verbose=False
    )

    info = await client_brick.run_get_service_info()
    print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")

    request = GuardRequest(text="This is a normal message.")
    response = await client_brick.run_unary(request)
    print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")

    request = GuardRequest(text="This is an attack!")
    response = await client_brick.run_unary(request)
    print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 核心 API / 類別 / 函式深度解析

### [GuardBrick](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/guard/base_guard.py#L17) 類別

#### 類別簽名與繼承關係

```python
class GuardBrick(BaseBrick[GuardRequest, GuardResponse]):
    brick_type = BrickType.GUARD
    allowed_handler_types = {"unary", "get_service_info"}
```

#### 支援的 Handler

- `unary`：單次請求檢查（必須實作）
- `get_service_info`：查詢服務資訊（必須實作）
- **不支援**：input_streaming, output_streaming, bidi_streaming（呼叫會拋出 NotImplementedError）

#### 主要方法

- [toGrpcClient()](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/guard/base_guard.py#L75)
  - 轉換為 gRPC 客戶端，連接遠端 Guard 服務。
  - 參數：`remote_address`（如 `"127.0.0.1:50051"`），可傳遞自訂參數如 `sensitivity`、`verbose`。
  - 回傳：配置好的 GuardBrick 實例，可直接呼叫 `run_unary`、`run_get_service_info`。

- [run_unary()](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L233)
  - 執行單次安全檢查，回傳 `GuardResponse`。

- [run_get_service_info()](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L245)
  - 查詢服務資訊，回傳 `ServiceInfoResponse`。

#### 資料模型

- [GuardRequest](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/guard_types.py#L11)
  - 欄位：`text`, `client_id`, `session_id`, `request_id`, `source_language`
- [GuardResult](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/guard_types.py#L43)
  - 欄位：`is_attack`, `confidence`, `detail`
- [GuardResponse](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/guard_types.py#L67)
  - 欄位：`results`（List[GuardResult]）, `error`

#### gRPC 協定

[guard.proto](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/guard/guard.proto#L1)
```protobuf
service GuardService {
  rpc GetServiceInfo(ServiceInfoRequest) returns (ServiceInfoResponse);
  rpc Unary(GuardRequest) returns (GuardResponse);
}
```

---

## 常見錯誤與 Troubleshooting

- **呼叫不支援的 handler**  
  嘗試註冊或呼叫 `input_streaming`、`output_streaming`、`bidi_streaming` 會直接丟出 `NotImplementedError`。
  - 解法：僅實作與呼叫 `unary` 與 `get_service_info`。

- **gRPC 連線失敗**  
  - 檢查 `remote_address` 是否正確，gRPC 服務端是否啟動。
  - 檢查防火牆與網路設定。

- **回傳結果為空或格式錯誤**  
  - 確認自訂 handler 回傳正確的資料模型（如 `GuardResponse`）。

- **靈敏度參數未生效**  
  - 檢查初始化時 `sensitivity` 參數是否正確傳遞。

---

## 最佳實踐與進階技巧

- **自訂靈敏度與日誌**  
  - 依應用場景調整 `sensitivity`，開發階段可開啟 `verbose=True` 觀察判斷細節。

- **gRPC 部署建議**  
  - 生產環境建議使用固定 port，並加強網路安全。
  - 可結合 Docker 部署多個 GuardBrick 實例。

- **單元測試**  
  - 建議針對 `unary` handler 撰寫多組測試案例，覆蓋正常、攻擊、邊界情境。

---

## FAQ / 進階問答

### Q1: GuardBrick 可以支援串流模式嗎？
**A**: 不行。GuardBrick 僅支援 `unary` 與 `get_service_info`，呼叫其他 handler 會直接丟出錯誤。

### Q2: 如何自訂攻擊判斷邏輯？
**A**: 繼承 GuardBrick，實作自己的 `unary_handler`，在其中撰寫自訂判斷規則即可。

### Q3: 可以同時啟動多個 GuardBrick 服務嗎？
**A**: 可以。每個服務可用不同 port 或不同設定啟動，彼此獨立。

### Q4: 如何與其他 Brick 組合？
**A**: GuardBrick 可與其他 Brick（如 LLMBrick、CommonBrick）組合於同一 gRPC 服務，或串接於微服務架構中。

---

## 參考資源與延伸閱讀

- [LLMBrick 官方文件](https://github.com/JiHungLin/llmbrick)
- [gRPC Python 官方文件](https://grpc.io/docs/languages/python/)
- [Protocol Buffer 官方文件](https://developers.google.com/protocol-buffers)
- [GuardBrick 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/guard_brick_define)
- [問題回報與討論](https://github.com/JiHungLin/llmbrick/issues)

---

GuardBrick 是 LLMBrick 框架中安全防護的基石，適合用於各類 AI 應用的輸入檢查與防護。建議搭配單元測試與日誌觀察，確保安全邏輯正確運作。

*本指南持續更新中，歡迎社群貢獻與討論！*
