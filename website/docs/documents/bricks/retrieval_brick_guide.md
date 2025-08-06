# RetrievalBrick

本指南詳細說明 [`llmbrick/bricks/retrieval/base_retrieval.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/retrieval/base_retrieval.py#L1) 中的 RetrievalBrick 實作，這是 LLMBrick 框架中專為「檢索」場景設計的組件。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

RetrievalBrick 旨在解決以下問題：

- **標準化檢索服務**：提供統一的查詢（Retrieval）API，方便整合向量資料庫、知識庫、文件檢索等應用。
- **gRPC 服務對接**：內建 gRPC 協定，支援跨語言、跨平台的高效通訊。
- **嚴格型別與資料結構**：明確定義查詢請求、回應、文件格式，降低整合成本。
- **錯誤處理標準化**：統一錯誤回報格式，便於前後端協作與除錯。

---

## 專案結構圖與模組詳解

### 整體架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── bricks/
│   │   └── retrieval/
│   │       └── base_retrieval.py         # RetrievalBrick 主體實作
│   ├── protocols/
│   │   ├── grpc/
│   │   │   └── retrieval/
│   │   │       ├── retrieval.proto       # Protocol Buffer 定義
│   │   │       ├── retrieval_pb2.py      # 自動生成的訊息類別
│   │   │       └── retrieval_pb2_grpc.py # gRPC 服務存根
│   │   └── models/
│   │       └── bricks/
│   │           └── retrieval_types.py    # Retrieval 資料模型
│   └── core/
│       └── brick.py                      # BaseBrick 抽象基礎類別
├── examples/
│   └── retrieval_brick_define/
│       ├── my_brick.py                   # 自訂 RetrievalBrick 範例
│       ├── grpc_server.py                # gRPC 服務端範例
│       ├── grpc_client.py                # gRPC 客戶端範例
│       └── local_use.py                  # 本地呼叫範例
```

### 核心模組詳細說明

#### 1. [`RetrievalBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/retrieval/base_retrieval.py#L18)

- **職責**：專為「檢索」場景設計的 Brick，僅支援 `unary`（單次查詢）與 `get_service_info`（服務資訊查詢）兩種 handler。
- **gRPC 對應**：
  - `Unary` → `unary` handler
  - `GetServiceInfo` → `get_service_info` handler
- **限制**：不支援 input/output/bidi streaming，調用會直接拋出 NotImplementedError。

#### 2. [`retrieval.proto`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/retrieval/retrieval.proto#L1)

- 定義 Retrieval 服務的 gRPC 介面與資料結構。
- 主要訊息：
  - `RetrievalRequest`：查詢請求
  - `Document`：檢索結果文件
  - `RetrievalResponse`：查詢回應
- 服務介面：
  - `GetServiceInfo`
  - `Unary`

#### 3. [`retrieval_types.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/retrieval_types.py#L10)

- 定義 Python 端的資料模型，與 proto 對應。
- 主要類別：
  - `RetrievalRequest`
  - `Document`
  - `RetrievalResponse`

---

## 安裝與環境設定指南

### 依賴需求

RetrievalBrick 需要以下核心依賴：

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
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse

print("✅ RetrievalBrick 安裝成功！")
```

3. 開發環境設定

```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 設定環境變數（可選）
export LLMBRICK_LOG_LEVEL=INFO
export LLMBRICK_GRPC_PORT=50052
```

---

## 逐步範例：從基礎到進階

### 1. 最簡單的 RetrievalBrick 使用

#### 本地呼叫範例

```python
import asyncio
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse, Document

class MyRetrievalBrick(RetrievalBrick):
    def __init__(self, index_name: str = "default_index", **kwargs):
        super().__init__(**kwargs)
        self.index_name = index_name

    @RetrievalBrick.unary_handler
    async def search(self, request: RetrievalRequest) -> RetrievalResponse:
        if not request.query:
            return RetrievalResponse(
                documents=[],
                error={"code": 400, "message": "Query cannot be empty"}
            )
        # 假設回傳一個靜態文件
        doc = Document(
            doc_id="doc1",
            title="Test Document",
            snippet="This is a test snippet.",
            score=0.99,
            metadata={"source": self.index_name}
        )
        return RetrievalResponse(documents=[doc])

async def main():
    brick = MyRetrievalBrick(index_name="local_index")
    req = RetrievalRequest(query="test query", client_id="cid")
    resp = await brick.run_unary(req)
    print(resp)

asyncio.run(main())
```

### 2. gRPC 服務端建立與部署

```python
# grpc_server.py
import asyncio
from llmbrick.servers.grpc.server import GrpcServer
from examples.retrieval_brick_define.my_brick import MyRetrievalBrick

async def start_grpc_server():
    server = GrpcServer(port=50052)
    brick = MyRetrievalBrick(index_name="grpc_index")
    server.register_service(brick)
    print("🚀 gRPC 服務器啟動中... (localhost:50052)")
    await server.start()

if __name__ == "__main__":
    asyncio.run(start_grpc_server())
```

### 3. gRPC 客戶端連接與使用

```python
# grpc_client.py
import asyncio
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest

async def grpc_client_example():
    client = RetrievalBrick.toGrpcClient("localhost:50052")
    req = RetrievalRequest(query="test query", client_id="cid")
    resp = await client.run_unary(req)
    print(resp)

if __name__ == "__main__":
    asyncio.run(grpc_client_example())
```

---

## 核心 API / 類別 / 函式深度解析

### [`RetrievalBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/retrieval/base_retrieval.py#L18) 類別

#### 類別簽名與繼承關係

```python
class RetrievalBrick(BaseBrick[RetrievalRequest, RetrievalResponse]):
    brick_type = BrickType.RETRIEVAL
    allowed_handler_types = {"unary", "get_service_info"}
```

#### 主要方法

##### [`toGrpcClient()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/retrieval/base_retrieval.py#L80)

- **功能**：將 RetrievalBrick 轉換為異步 gRPC 客戶端。
- **參數**：
  - `remote_address: str` - gRPC 伺服器地址（如 `"localhost:50052"`）
  - `**kwargs` - 額外初始化參數
- **回傳**：配置為 gRPC 客戶端的 RetrievalBrick 實例
- **範例**：
    ```python
    client = RetrievalBrick.toGrpcClient("localhost:50052")
    req = RetrievalRequest(query="test", client_id="cid")
    resp = await client.run_unary(req)
    ```

##### [`run_unary()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L233)

- **功能**：執行單次檢索請求。
- **參數**：`input_data: RetrievalRequest`
- **回傳**：`RetrievalResponse`
- **範例**：
    ```python
    req = RetrievalRequest(query="test", client_id="cid")
    resp = await brick.run_unary(req)
    ```

##### [`run_get_service_info()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L245)

- **功能**：查詢服務資訊。
- **回傳**：`ServiceInfoResponse`
- **範例**：
    ```python
    info = await brick.run_get_service_info()
    print(info.service_name)
    ```

#### 不支援的 Handler

- `input_streaming`, `output_streaming`, `bidi_streaming` 皆會直接丟出 NotImplementedError。
- 參考：[bidi_streaming()](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/retrieval/base_retrieval.py#L40)

---

### 資料模型

#### [`RetrievalRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/retrieval_types.py#L11)

- **欄位**：
  - `query: str` - 查詢字串
  - `max_results: int` - 最大回傳數量
  - `client_id: str`
  - `session_id: str`
  - `request_id: str`
  - `source_language: str`

#### [`Document`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/retrieval_types.py#L48)

- **欄位**：
  - `doc_id: str`
  - `title: str`
  - `snippet: str`
  - `score: float`
  - `metadata: dict`

#### [`RetrievalResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/retrieval_types.py#L70)

- **欄位**：
  - `documents: List[Document]`
  - `error: Optional[ErrorDetail]`

---

## 常見錯誤與排除

- **呼叫不支援的 handler**：如 `run_input_streaming`，會丟出 NotImplementedError。
- **查詢字串為空**：應於 handler 內檢查，並回傳 error code 400。
- **gRPC 連線失敗**：請確認伺服器位址與 port 正確，且 server 已啟動。
- **資料型別不符**：請確保傳入的 request/response 皆為 RetrievalRequest/RetrievalResponse 型別。

---

## 最佳實踐與進階技巧

- **僅註冊 unary/get_service_info handler**，避免註冊其他 handler。
- **查詢參數驗證**：於 handler 內檢查 query、client_id 等必要欄位。
- **gRPC client 建議重複使用**，避免每次都新建 channel。
- **回傳結構建議**：documents 為空時，error 應明確說明原因。

---

## FAQ / 進階問答

### Q1: RetrievalBrick 可以支援串流查詢嗎？

**A**：不行。RetrievalBrick 僅支援 unary（單次請求）與 get_service_info，呼叫其他 handler 會直接丟出 NotImplementedError。

### Q2: 如何自訂檢索邏輯？

**A**：繼承 RetrievalBrick，並以 `@unary_handler` 裝飾自訂 async 方法，回傳 RetrievalResponse。

### Q3: 如何設計文件結構（Document）？

**A**：Document 支援自訂 metadata 欄位，可存放來源、標籤、額外資訊等，建議以 dict 結構存放。

### Q4: 如何處理查詢錯誤？

**A**：於 handler 內回傳 RetrievalResponse，並設置 error 欄位（如 code=400, message="Query cannot be empty"）。

---

## 參考資源與延伸閱讀

- [RetrievalBrick 原始碼](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/retrieval/base_retrieval.py)
- [retrieval.proto 定義](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/retrieval/retrieval.proto)
- [retrieval_types.py 資料模型](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/retrieval_types.py)
- [gRPC Python 官方文件](https://grpc.io/docs/languages/python/)
- [LLMBrick 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/retrieval_brick_define)
- [問題回報](https://github.com/JiHungLin/llmbrick/issues)

---

RetrievalBrick 是構建 AI 檢索應用的標準基石，熟悉其設計與用法，能大幅提升檢索系統的開發效率與穩定性。

---

（如需更進階的串流檢索，請考慮自訂其他 Brick 類型或參考 LLMBrick 進階用法。）

---

*本指南持續更新中，如有問題或建議，歡迎參與社群討論！*
