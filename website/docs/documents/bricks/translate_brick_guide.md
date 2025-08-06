# TranslateBrick

本指南詳細說明 [`llmbrick/bricks/translate/base_translate.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/translate/base_translate.py#L1) 中的 TranslateBrick 實作，這是 LLMBrick 框架中專為「翻譯/轉換」場景設計的高階組件。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

TranslateBrick 旨在解決以下問題：

- **標準化翻譯服務**：提供統一的翻譯請求/回應介面，支援多語言、多模型。
- **gRPC 雲端服務化**：內建 gRPC 協定，支援單次請求與流式輸出，適合高效能、低延遲的翻譯應用。
- **嚴格型別安全**：明確限制僅允許三種 handler（unary、output_streaming、get_service_info），避免誤用。
- **易於擴展與整合**：可快速整合各類翻譯模型，並可作為微服務部署。

---

## 專案結構圖與模組詳解

### 整體架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── bricks/
│   │   └── translate/
│   │       └── base_translate.py      # TranslateBrick 主體實作
│   ├── protocols/
│   │   ├── grpc/
│   │   │   └── translate/
│   │   │       ├── translate.proto    # Protocol Buffer 定義
│   │   │       ├── translate_pb2.py   # 自動生成的訊息類別
│   │   │       └── translate_pb2_grpc.py # gRPC 服務存根
│   │   └── models/
│   │       └── bricks/
│   │           └── translate_types.py # TranslateRequest/Response 資料模型
```

### 核心模組詳細說明

#### 1. [`TranslateBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/translate/base_translate.py#L17) - 翻譯專用 Brick

- **職責**：提供標準化的翻譯請求/回應處理，支援單次請求與流式輸出。
- **核心特性**：
  - 僅允許 `unary`、`output_streaming`、`get_service_info` 三種 handler
  - 內建 `toGrpcClient()`，可一鍵轉換為 gRPC 客戶端
  - 嚴格型別檢查，避免誤用不支援的 handler
  - 支援多模型、多語言參數

#### 2. gRPC 協定層

- **[Protocol Buffer 定義](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/translate/translate.proto#L1)**：
  ```protobuf
  service TranslateService {
    rpc GetServiceInfo(ServiceInfoRequest) returns (ServiceInfoResponse);
    rpc Unary(TranslateRequest) returns (TranslateResponse);
    rpc OutputStreaming(TranslateRequest) returns (stream TranslateResponse);
  }
  ```
- **[gRPC 產生檔](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/translate/translate_pb2_grpc.py#L1)**：自動處理 Python 物件與 protobuf 轉換。

#### 3. 資料模型系統

- **[`TranslateRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/translate_types.py#L11)**：
  ```python
  @dataclass
  class TranslateRequest:
      text: str = ""
      model_id: str = ""
      target_language: str = ""
      client_id: str = ""
      session_id: str = ""
      request_id: str = ""
      source_language: str = ""
  ```
- **[`TranslateResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/translate_types.py#L51)**：
  ```python
  @dataclass
  class TranslateResponse:
      text: str = ""
      tokens: List[str] = field(default_factory=list)
      language_code: str = ""
      is_final: bool = False
      error: Optional[ErrorDetail] = None
  ```

---

## 安裝與環境設定指南

### 依賴需求

TranslateBrick 需要以下核心依賴：

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
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.protocols.models.bricks.translate_types import TranslateRequest, TranslateResponse

print("✅ TranslateBrick 安裝成功！")
```

#### 3. 開發環境設定

```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 設定環境變數（可選）
export LLMBRICK_LOG_LEVEL=INFO
export LLMBRICK_GRPC_PORT=50052
```

---

## 逐步範例：從基礎到進階

### 1. 最簡單的 TranslateBrick 使用

```python
import asyncio
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.protocols.models.bricks.translate_types import TranslateRequest, TranslateResponse

async def basic_example():
    brick = TranslateBrick()

    @brick.unary()
    async def simple_translate(request: TranslateRequest) -> TranslateResponse:
        # 假設直接回傳大寫
        return TranslateResponse(
            text=request.text.upper(),
            tokens=request.text.upper().split(),
            language_code=request.target_language or "en",
            is_final=True
        )

    req = TranslateRequest(text="hello world", target_language="en")
    resp = await brick.run_unary(req)
    print(f"翻譯結果: {resp.text}, 語言: {resp.language_code}")

asyncio.run(basic_example())
```

### 2. gRPC 客戶端連接與使用

```python
import asyncio
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.protocols.models.bricks.translate_types import TranslateRequest

async def grpc_client_example():
    # 連接到 gRPC 服務端
    client = TranslateBrick.toGrpcClient("localhost:50052")
    print("🔗 連接到 gRPC 服務器...")

    # 1. 查詢服務資訊
    info = await client.run_get_service_info()
    print(f"服務名稱: {info.service_name}, 版本: {info.version}")

    # 2. 單次翻譯請求
    req = TranslateRequest(text="hello grpc", target_language="zh-tw")
    resp = await client.run_unary(req)
    print(f"翻譯結果: {resp.text}")

    # 3. 流式翻譯
    req = TranslateRequest(text="streaming translation", target_language="en")
    async for resp in client.run_output_streaming(req):
        print(f"流式片段: {resp.text}, is_final: {resp.is_final}")

asyncio.run(grpc_client_example())
```

### 3. gRPC 服務端建立與部署

```python
# grpc_server.py
import asyncio
from llmbrick.servers.grpc.server import GrpcServer
from my_translate_brick import MyTranslateBrick  # 需自訂

async def start_grpc_server():
    server = GrpcServer(port=50052)
    translate_brick = MyTranslateBrick()
    server.register_service(translate_brick)
    print("🚀 gRPC 服務器啟動中... 監聽 localhost:50052")
    await server.start()

if __name__ == "__main__":
    asyncio.run(start_grpc_server())
```

---

## 核心 API / 類別 / 函式深度解析

### [`TranslateBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/translate/base_translate.py#L17) 類別

#### 類別簽名與繼承關係

```python
class TranslateBrick(BaseBrick[TranslateRequest, TranslateResponse]):
    brick_type = BrickType.TRANSLATE
    allowed_handler_types = {"unary", "output_streaming", "get_service_info"}
```

#### 支援的 Handler

- `unary`：單次請求/回應
- `output_streaming`：單一請求，多次流式回應
- `get_service_info`：查詢服務資訊
- **不支援**：`input_streaming`、`bidi_streaming`（呼叫會丟出 NotImplementedError）

#### [`toGrpcClient()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/translate/base_translate.py#L69) - gRPC 客戶端轉換

```python
@classmethod
def toGrpcClient(cls, remote_address: str, **kwargs) -> TranslateBrick
```
- **參數**：
  - `remote_address: str` - gRPC 伺服器位址（如 "localhost:50052"）
  - `**kwargs` - 傳遞給建構子的額外參數
- **回傳**：配置為 gRPC 客戶端的 TranslateBrick 實例
- **用途**：自動註冊所有支援的 handler，並將請求轉為 gRPC 呼叫

#### Handler 實作範例

```python
@brick.unary()
async def my_translate(request: TranslateRequest) -> TranslateResponse:
    # ... 處理邏輯 ...
    return TranslateResponse(text="翻譯結果", tokens=["翻", "譯", "結", "果"], language_code="zh-tw", is_final=True)
```

#### 資料模型

- [`TranslateRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/translate_types.py#L11)
  - `text`: str - 需翻譯內容
  - `model_id`: str - 指定模型
  - `target_language`: str - 目標語言
  - `client_id`, `session_id`, `request_id`, `source_language`: 識別與追蹤欄位

- [`TranslateResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/translate_types.py#L51)
  - `text`: str - 翻譯結果
  - `tokens`: List[str] - 分詞結果（流式時可用）
  - `language_code`: str - 回應語言
  - `is_final`: bool - 是否為最終片段
  - `error`: Optional[ErrorDetail] - 錯誤資訊

---

## 常見錯誤與排除

- **呼叫不支援的 handler**  
  嘗試註冊 `input_streaming` 或 `bidi_streaming` 會丟出 NotImplementedError  
  解法：僅使用 `unary`、`output_streaming`、`get_service_info`。

- **gRPC 連線失敗**  
  - 檢查伺服器位址與 port 是否正確
  - 確認伺服器已啟動且防火牆未阻擋

- **資料型別不符**  
  - 請確保傳入的請求/回應皆為 `TranslateRequest`/`TranslateResponse` 型別

- **流式回應未正確結束**  
  - 檢查 `is_final` 欄位，並正確處理流式結束

---

## 最佳實踐與進階技巧

- **明確指定模型與語言**：建議每次請求都帶上 `model_id` 與 `target_language`，提升多模型、多語言支援彈性。
- **流式輸出最佳化**：長文本建議使用 `output_streaming`，可即時回饋翻譯片段，提升用戶體驗。
- **服務資訊查詢**：可用 `run_get_service_info()` 查詢支援的模型、語言與版本，動態調整前端選項。
- **錯誤處理統一**：所有回應皆帶有 `error` 欄位，建議前端/客戶端統一處理錯誤顯示。

---

## FAQ / 進階問答

### Q1: TranslateBrick 可以用於哪些場景？

**A**: 適用於各類翻譯、語言轉換、字幕生成、跨語言聊天等場景，尤其適合需要高效能、低延遲的雲端服務。

### Q2: 為什麼不支援 input_streaming/bidi_streaming？

**A**: TranslateBrick 設計上僅針對單向翻譯流程，避免複雜的多向互動，提升穩定性與易用性。如需雙向串流，建議使用 CommonBrick 或 LLMBrick。

### Q3: 如何自訂支援的語言/模型？

**A**: 可於 `get_service_info` handler 回傳自訂的模型資訊，前端可據此動態顯示支援語言與模型。

### Q4: 如何串接第三方翻譯 API？

**A**: 在 `unary` 或 `output_streaming` handler 內呼叫第三方 API，並將結果包裝為 `TranslateResponse` 回傳即可。

---

## 參考資源與延伸閱讀

- [TranslateBrick 原始碼](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/translate/base_translate.py#L1)
- [gRPC 協定定義](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/translate/translate.proto#L1)
- [資料模型定義](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/translate_types.py#L1)
- [LLMBrick 官方文件](../../intro.md)
- [gRPC Python 官方文件](https://grpc.io/docs/languages/python/)
- [GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/translate_brick_define)
- [問題回報](https://github.com/JiHungLin/llmbrick/issues)

---

TranslateBrick 是打造多語言 AI 應用的關鍵組件，掌握其用法能大幅提升開發效率與系統穩定性。如有問題，歡迎參與社群討論！
