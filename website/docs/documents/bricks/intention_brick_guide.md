# IntentionBrick 完整使用指南

本指南詳細說明 [`llmbrick/bricks/intention/base_intention.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/intention/base_intention.py#L1) 中的 IntentionBrick 實作，這是 LLMBrick 框架中專為「意圖檢查」與「用戶行為保護」設計的專用組件。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

IntentionBrick 主要用於：
- **用戶意圖辨識**：自動判斷輸入內容屬於聊天、指令、問題等哪一類型。
- **安全防護**：可作為前置檢查，阻擋惡意或不當請求。
- **標準化意圖服務**：提供統一的 gRPC 服務協定，便於多語言、多平台整合。
- **高可擴展性**：可自訂意圖分類邏輯，並與其他 Brick 組件協作。

### 🔧 核心功能特色

- **僅支援 Unary 與 GetServiceInfo**：專注於單次請求與服務查詢，簡潔高效。
- **gRPC 標準協定**：與多種語言、平台無縫串接。
- **嚴格型別資料模型**：明確定義請求與回應格式，降低誤用風險。
- **自動客戶端生成**：一鍵轉換為 gRPC 客戶端，便於跨服務調用。
- **錯誤處理標準化**：所有回應皆含有統一的錯誤資訊。

---

## 專案結構圖與模組詳解

### 整體架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── bricks/
│   │   └── intention/
│   │       ├── __init__.py
│   │       └── base_intention.py      # IntentionBrick 主體實作
│   ├── protocols/
│   │   ├── grpc/
│   │   │   └── intention/
│   │   │       ├── intention.proto    # Protocol Buffer 定義
│   │   │       ├── intention_pb2.py   # 自動生成的訊息類別
│   │   │       └── intention_pb2_grpc.py # gRPC 服務存根
│   │   └── models/
│   │       └── bricks/
│   │           └── intention_types.py # IntentionBrick 資料類型
```

### 核心模組詳細說明

#### 1. [`IntentionBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/intention/base_intention.py#L17) - 意圖檢查專用 Brick

- **職責**：專為意圖辨識與安全檢查設計，僅允許 `unary` 及 `get_service_info` 兩種 handler。
- **繼承自**：`BaseBrick[IntentionRequest, IntentionResponse]`
- **gRPC 服務類型**：`intention`
- **限制**：不支援 streaming handler（如 output_streaming、input_streaming、bidi_streaming）

#### 2. [`intention.proto`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/intention/intention.proto#L1) - gRPC 協定定義

- **訊息類型**：
  - `IntentionRequest`：用戶輸入、來源、session 等資訊
  - `IntentionResult`：意圖分類與信度
  - `IntentionResponse`：多個意圖結果與錯誤資訊
- **服務方法**：
  - `GetServiceInfo`：查詢服務資訊
  - `Unary`：單次意圖檢查

#### 3. [`intention_types.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/intention_types.py#L1) - 資料模型

- `IntentionRequest`：封裝請求欄位，含轉換方法
- `IntentionResult`：單一意圖分類結果
- `IntentionResponse`：回應多個意圖結果與錯誤

---

## 安裝與環境設定指南

### 依賴需求

IntentionBrick 需要以下核心依賴：

```bash
grpcio>=1.50.0
grpcio-tools>=1.50.0
protobuf>=4.21.0
google-protobuf>=4.21.0
```

### 自動化安裝步驟

#### 1. 安裝 LLMBrick 套件

```bash
pip install llmbrick
# 或從源碼安裝
git clone https://github.com/JiHungLin/llmbrick.git
cd llmbrick
pip install -e .
```

#### 2. 驗證安裝

```python
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest, IntentionResponse

print("✅ IntentionBrick 安裝成功！")
```

#### 3. 開發環境設定

```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 設定環境變數（可選）
export LLMBRICK_LOG_LEVEL=INFO
export LLMBRICK_GRPC_PORT=50051
```

---

## 逐步範例：從基礎到進階

### 1. 最簡單的 IntentionBrick 使用

```python
import asyncio
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest, IntentionResponse

async def basic_example():
    # 建立 IntentionBrick 實例
    brick = IntentionBrick()

    # 使用裝飾器定義意圖檢查邏輯
    @brick.unary()
    async def check_intention(request: IntentionRequest) -> IntentionResponse:
        # 假設簡單分類：只要有 "?" 就判斷為 question
        if "?" in request.text:
            return IntentionResponse(
                results=[{"intent_category": "question", "confidence": 0.95}],
                error=None
            )
        else:
            return IntentionResponse(
                results=[{"intent_category": "chat", "confidence": 0.8}],
                error=None
            )

    # 執行請求
    request = IntentionRequest(text="How are you?")
    response = await brick.run_unary(request)
    print(f"意圖: {response.results[0].intent_category}, 信度: {response.results[0].confidence}")

asyncio.run(basic_example())
```

### 2. gRPC 客戶端連接與使用

```python
import asyncio
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest

async def grpc_client_example():
    # 建立 gRPC 客戶端
    client = IntentionBrick.toGrpcClient("localhost:50051")
    print("🔗 連接到 gRPC 服務器...")

    # 查詢服務資訊
    info = await client.run_get_service_info()
    print(f"服務名稱: {info.service_name}, 版本: {info.version}")

    # 單次意圖檢查
    request = IntentionRequest(text="請問天氣如何？")
    response = await client.run_unary(request)
    if response.error is None or response.error.code == 200:
        for result in response.results:
            print(f"意圖: {result.intent_category}, 信度: {result.confidence}")
    else:
        print(f"❌ 錯誤: {response.error.message}")

asyncio.run(grpc_client_example())
```

### 3. gRPC 服務端建立與部署

```python
# grpc_server.py
import asyncio
from llmbrick.servers.grpc.server import GrpcServer
from my_intention_brick import MyIntentionBrick  # 需自訂

async def start_grpc_server():
    server = GrpcServer(port=50051)
    brick = MyIntentionBrick()
    server.register_service(brick)
    print("🚀 gRPC 服務器啟動中...")
    await server.start()

if __name__ == "__main__":
    asyncio.run(start_grpc_server())
```

---

## 核心 API / 類別 / 函式深度解析

### [`IntentionBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/intention/base_intention.py#L17) 類別

#### 類別簽名與繼承關係

```python
class IntentionBrick(BaseBrick[IntentionRequest, IntentionResponse]):
    brick_type = BrickType.INTENTION
    allowed_handler_types = {"unary", "get_service_info"}
```

#### 只允許的 Handler

- `unary`：單次意圖檢查
- `get_service_info`：查詢服務資訊

**不支援**：`output_streaming`、`input_streaming`、`bidi_streaming`（調用會直接拋出 NotImplementedError）

#### [`toGrpcClient()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/intention/base_intention.py#L79) - gRPC 客戶端轉換

```python
@classmethod
def toGrpcClient(cls, remote_address: str, **kwargs) -> IntentionBrick
```

- **功能**：將 IntentionBrick 轉換為異步 gRPC 客戶端
- **參數**：
  - `remote_address: str` - gRPC 伺服器地址（如 "localhost:50051"）
  - `**kwargs` - 額外初始化參數
- **回傳**：配置為 gRPC 客戶端的 IntentionBrick 實例

#### [`IntentionRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/intention_types.py#L11)

```python
@dataclass
class IntentionRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""
```

#### [`IntentionResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/intention_types.py#L61)

```python
@dataclass
class IntentionResponse:
    results: List[IntentionResult] = field(default_factory=list)
    error: Optional[ErrorDetail] = None
```

#### [`IntentionResult`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/intention_types.py#L45)

```python
@dataclass
class IntentionResult:
    intent_category: str = ""
    confidence: float = 0.0
```

---

## 常見錯誤與排解

### 1. 調用不支援的 Handler

- **錯誤訊息**：`NotImplementedError: IntentionBrick does not support output_streaming handler.`
- **原因**：IntentionBrick 僅允許 `unary` 與 `get_service_info`，其他 handler 會直接拋出例外。
- **解法**：僅註冊/調用 `unary` 或 `get_service_info`。

### 2. gRPC 連線失敗

- **錯誤訊息**：`grpc.aio._call.AioRpcError: ...`
- **原因**：伺服器未啟動、port 錯誤、防火牆阻擋等。
- **解法**：確認伺服器已啟動且 port 正確，並檢查網路連線。

### 3. 輸入資料格式錯誤

- **錯誤訊息**：`TypeError` 或回應 error 欄位有錯誤碼
- **原因**：`IntentionRequest` 欄位缺失或型別錯誤
- **解法**：確保所有必要欄位皆正確填寫

---

## 效能優化與最佳實踐

- **只實作必要的 handler**：避免多餘的 streaming handler 定義。
- **gRPC 客戶端重複使用**：長期連線建議共用 channel，減少連線建立開銷。
- **錯誤處理統一**：所有回應務必填寫 error 欄位，便於前端或其他服務統一處理。
- **資料驗證**：在 handler 內部加強輸入資料驗證，避免異常傳遞到 gRPC 層。

---

## FAQ / 進階問答

### Q1: IntentionBrick 可以用來做什麼？

**A**: 適合用於聊天機器人、API Gateway、內容審查等場景，作為前置意圖分類與安全檢查。

### Q2: 可以自訂意圖分類邏輯嗎？

**A**: 可以！只需在 `unary` handler 內實作自訂分類規則，回傳對應的 `IntentionResult`。

### Q3: 如果需要串流處理怎麼辦？

**A**: IntentionBrick 僅設計為單次請求，若需串流請考慮使用 CommonBrick 或其他支援 streaming 的 Brick。

### Q4: 如何與其他 Brick 組合？

**A**: 可在 API Gateway 先用 IntentionBrick 檢查，再根據意圖分流到 LLMBrick、GuardBrick 等其他組件。

---

## 參考資源與延伸閱讀

- [IntentionBrick 原始碼](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/intention/base_intention.py#L1)
- [gRPC 協定定義 intention.proto](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/intention/intention.proto#L1)
- [IntentionRequest/Response 資料模型](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/intention_types.py#L1)
- [LLMBrick 框架介紹](../../intro.md)
- [GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/intention_brick_define)
- [問題回報](https://github.com/JiHungLin/llmbrick/issues)
- [討論區](https://github.com/JiHungLin/llmbrick/discussions)

---

IntentionBrick 是打造安全、可擴展 AI 應用的關鍵組件。建議深入理解其限制與設計理念，並善用其標準化協定與型別安全，提升服務品質與維護效率。

*本指南持續更新中，歡迎參與社群討論與貢獻！*
