# RectifyBrick

本指南詳細說明 [`llmbrick/bricks/rectify/base_rectify.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/rectify/base_rectify.py#L1) 中 RectifyBrick 的設計理念、架構、用法與最佳實踐。RectifyBrick 是 LLMBrick 框架中專為「文本校正」打造的標準組件，支援 gRPC 服務，並提供統一的請求/回應資料模型。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

RectifyBrick 旨在解決以下問題：

- **標準化文本校正服務**：提供統一的 API 與協定，讓各種校正模型能快速整合。
- **gRPC 服務化**：內建 gRPC 服務協定，支援跨語言、跨平台部署。
- **嚴格型別安全**：明確定義請求/回應資料結構，減少錯誤。
- **易於擴展與維護**：只需專注於校正邏輯，通訊、錯誤處理、服務資訊查詢皆自動化。

---

## 專案結構圖與模組詳解

### 整體架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── bricks/
│   │   └── rectify/
│   │       ├── __init__.py
│   │       └── base_rectify.py         # RectifyBrick 主體實作
│   ├── protocols/
│   │   ├── grpc/
│   │   │   └── rectify/
│   │   │       ├── rectify.proto       # Protocol Buffer 定義
│   │   │       ├── rectify_pb2.py      # 自動生成的訊息類別
│   │   │       └── rectify_pb2_grpc.py # 自動生成的服務存根
│   │   └── models/
│   │       └── bricks/
│   │           └── rectify_types.py    # Rectify 資料模型
│   └── servers/
│       └── grpc/
│           └── server.py              # gRPC 服務器（共用）
├── examples/
│   └── rectify_brick_define/
│       ├── grpc_server.py             # RectifyBrick gRPC 服務端範例
│       ├── grpc_client.py             # RectifyBrick gRPC 客戶端範例
│       ├── local_use.py               # 本地呼叫範例
│       └── my_brick.py                # 自訂 RectifyBrick 實作
```

### 核心模組詳細說明

#### 1. [`RectifyBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/rectify/base_rectify.py#L17) - 校正服務主體

- **職責**：專為「文本校正」設計的 Brick，僅支援 `unary`（單次請求）與 `get_service_info`（服務資訊查詢）兩種 handler。
- **繼承**：自 [`BaseBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py)。
- **型別安全**：明確限定輸入為 [`RectifyRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/rectify_types.py#L11)，輸出為 [`RectifyResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/rectify_types.py#L43)。
- **gRPC 對應**：僅對應 `Unary` 與 `GetServiceInfo` 兩個 gRPC 方法。

#### 2. [`rectify.proto`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/rectify/rectify.proto#L1) - Protocol Buffer 定義

- **訊息結構**：
  - `RectifyRequest`：包含 `text`、`client_id`、`session_id`、`request_id`、`source_language`。
  - `RectifyResponse`：包含 `corrected_text` 及 `error`。
- **服務定義**：
  - `GetServiceInfo`：查詢服務資訊。
  - `Unary`：執行文本校正。

#### 3. [`rectify_types.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/rectify_types.py#L11) - 資料模型

- `RectifyRequest`：Python 資料類型，對應 gRPC 請求。
- `RectifyResponse`：Python 資料類型，對應 gRPC 回應，內含校正後文本與錯誤資訊。

---

## 安裝與執行指南

### 依賴需求

RectifyBrick 需依賴以下核心套件：

```bash
grpcio>=1.50.0
grpcio-tools>=1.50.0
protobuf>=4.21.0
google-protobuf>=4.21.0
```

### 自動化安裝步驟

1. 安裝 LLMBrick 套件

```bash
pip install llmbrick
# 或從源碼安裝
git clone https://github.com/JiHungLin/llmbrick.git
cd llmbrick
pip install -e .
```

2. 驗證安裝

```python
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse

print("✅ RectifyBrick 安裝成功！")
```

3. 開發環境設定（可選）

```bash
pip install -r requirements-dev.txt
export LLMBRICK_LOG_LEVEL=INFO
export LLMBRICK_GRPC_PORT=50051
```

---

## 逐步範例：從基礎到進階

### 1. 最簡單的 RectifyBrick 使用

```python
import asyncio
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse

async def basic_example():
    brick = RectifyBrick()

    @brick.unary()
    async def simple_rectify(request: RectifyRequest) -> RectifyResponse:
        # 假設只做簡單大寫校正
        corrected = request.text.upper()
        return RectifyResponse(corrected_text=corrected)

    request = RectifyRequest(text="hello rectify")
    response = await brick.run_unary(request)
    print(f"校正結果: {response.corrected_text}")

asyncio.run(basic_example())
```

### 2. 類別繼承方式定義 RectifyBrick

```python
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse
from llmbrick.protocols.models.bricks.common_types import ServiceInfoResponse, ModelInfo, ErrorDetail
from llmbrick.core.error_codes import ErrorCodes
from llmbrick.core.brick import unary_handler, get_service_info_handler

class MyRectifyBrick(RectifyBrick):
    """自訂文本校正 Brick"""

    @unary_handler
    async def rectify(self, request: RectifyRequest) -> RectifyResponse:
        if not request.text:
            return RectifyResponse(
                corrected_text="",
                error=ErrorCodes.parameter_invalid("text", "文本不得為空")
            )
        # 假設校正邏輯：去除多餘空白並首字大寫
        corrected = request.text.strip().capitalize()
        return RectifyResponse(corrected_text=corrected, error=ErrorCodes.success())

    @get_service_info_handler
    async def get_service_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="MyRectifyService",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="basic_rectify",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=False,
                    description="簡易文本校正模型"
                )
            ],
            error=ErrorCodes.success()
        )
```

### 3. gRPC 服務端建立與部署

```python
# examples/rectify_brick_define/grpc_server.py
import asyncio
from llmbrick.servers.grpc.server import GrpcServer
from examples.rectify_brick_define.my_brick import MyRectifyBrick

server = GrpcServer(port=50051)
rectify_brick = MyRectifyBrick()
server.register_service(rectify_brick)

if __name__ == "__main__":
    print("🚀 RectifyBrick gRPC 服務器啟動中...")
    server.run()
```

### 4. gRPC 客戶端連接與使用

```python
# examples/rectify_brick_define/grpc_client.py
import asyncio
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest

async def grpc_client_example():
    client = RectifyBrick.toGrpcClient("localhost:50051")
    print("🔗 連接到 RectifyBrick gRPC 服務器...")

    # 1. 查詢服務資訊
    info = await client.run_get_service_info()
    print(f"服務名稱: {info.service_name}, 版本: {info.version}")

    # 2. 單次校正請求
    request = RectifyRequest(text="hello rectify grpc")
    response = await client.run_unary(request)
    print(f"校正結果: {response.corrected_text}")

if __name__ == "__main__":
    asyncio.run(grpc_client_example())
```

---

## 核心 API / 類別 / 函式深度解析

### [`RectifyBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/rectify/base_rectify.py#L17) 類別

#### 類別簽名與繼承關係

```python
class RectifyBrick(BaseBrick[RectifyRequest, RectifyResponse]):
    brick_type = BrickType.RECTIFY
    allowed_handler_types = {"unary", "get_service_info"}
```

- **僅允許** `unary` 與 `get_service_info` 兩種 handler。
- 其他 handler（如 `input_streaming`, `output_streaming`, `bidi_streaming`）會直接丟出 `NotImplementedError`。

#### [`toGrpcClient()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/rectify/base_rectify.py#L77) - gRPC 客戶端轉換

```python
@classmethod
def toGrpcClient(cls, remote_address: str, **kwargs) -> RectifyBrick
```

- **功能**：將 RectifyBrick 轉換為異步 gRPC 客戶端，連接遠端服務。
- **參數**：
  - `remote_address: str` - gRPC 伺服器位址（如 `"localhost:50051"`）
  - `**kwargs` - 傳遞給建構子的額外參數
- **回傳**：配置為 gRPC 客戶端的 RectifyBrick 實例
- **內部實作**：自動註冊 `unary` 與 `get_service_info` 處理器，並建立 gRPC channel 與存根。

#### [`RectifyRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/rectify_types.py#L11) / [`RectifyResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/rectify_types.py#L43)

- `RectifyRequest` 欄位：
  - `text`: str - 欲校正的原始文本
  - `client_id`, `session_id`, `request_id`, `source_language`: 輔助資訊
- `RectifyResponse` 欄位：
  - `corrected_text`: str - 校正後文本
  - `error`: Optional[ErrorDetail] - 錯誤資訊

#### gRPC 協定層

- [`rectify.proto`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/rectify/rectify.proto#L1) 定義：

```protobuf
service RectifyService {
  rpc GetServiceInfo(ServiceInfoRequest) returns (ServiceInfoResponse);
  rpc Unary(RectifyRequest) returns (RectifyResponse);
}
```

---

## 常見錯誤與排除

- **嘗試註冊不支援的 handler**（如 output_streaming）：會收到 `NotImplementedError`，請僅使用 `unary` 與 `get_service_info`。
- **gRPC 連線失敗**：請確認伺服器位址與 port 正確，且防火牆未阻擋。
- **資料型別不符**：請確保請求/回應皆使用 `RectifyRequest`/`RectifyResponse`。
- **未實作 handler**：若未註冊 `unary` handler，呼叫 `run_unary` 會報錯。

---

## 最佳實踐與進階技巧

- **只實作必要 handler**：RectifyBrick 僅需實作 `unary` 與 `get_service_info`，其餘 handler 請勿註冊。
- **型別安全**：務必使用 `RectifyRequest`/`RectifyResponse`，避免混用其他 Brick 型別。
- **gRPC 客戶端重用**：長期大量請求時，建議自行管理 channel 連線池。
- **錯誤處理**：善用 `ErrorCodes` 統一回傳錯誤資訊，提升可維護性。

---

## FAQ / 進階問答

### Q1: RectifyBrick 可以支援串流處理嗎？

**A**：不行。RectifyBrick 僅支援單次請求（unary）與服務資訊查詢（get_service_info），如需串流請改用 CommonBrick 或其他支援串流的 Brick。

### Q2: RectifyBrick 適合哪些應用場景？

**A**：適合所有「單句/單段文本校正」的服務，如拼字修正、語法校正、簡易文法優化等。

### Q3: RectifyBrick 如何與其他 Brick 協作？

**A**：可與 LLMBrick、GuardBrick 等組合，作為多階段處理流程中的一環。例如：先用 LLMBrick 生成文本，再用 RectifyBrick 校正。

### Q4: RectifyBrick 的 gRPC 協定是否可擴充？

**A**：如需擴充協定，建議 fork 專案後修改 [`rectify.proto`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/rectify/rectify.proto#L1) 並重新產生 pb2 檔案。

---

## 參考資源與延伸閱讀

- [RectifyBrick 實作](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/rectify/base_rectify.py#L1)
- [gRPC 協定定義](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/rectify/rectify.proto#L1)
- [Rectify 資料模型](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/rectify_types.py#L1)
- [範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/rectify_brick_define)
- [LLMBrick 官方文件](../../intro.md)
- [問題回報](https://github.com/JiHungLin/llmbrick/issues)

---

RectifyBrick 是打造高品質文本校正服務的最佳起點。善用本指南，能讓你快速上手並開發出穩定、可維護的校正微服務！

*本手冊持續更新中，歡迎社群貢獻與討論！*
