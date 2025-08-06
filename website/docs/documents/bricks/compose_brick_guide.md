# ComposeBrick 完整使用指南

本指南詳細說明 [llmbrick/bricks/compose/base_compose.py](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/compose/base_compose.py#L1) 中的 ComposeBrick 實作，這是 LLMBrick 框架中專為「多文件統整、格式轉換、摘要翻譯」等複合型任務設計的高階組件。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

ComposeBrick 旨在解決以下場景的需求：

- **多文件統整**：將多份文件（如搜尋結果、摘要、段落）彙整為一份結構化資料。
- **格式轉換**：支援多種目標格式（如 JSON、HTML、Markdown），方便下游應用。
- **語言轉換/翻譯**：可於統整過程中進行語言轉換，支援多語系應用。
- **gRPC 標準化服務**：提供統一的 gRPC 介面，便於跨語言、跨服務串接。
- **高效串流支援**：針對大型資料可用流式（streaming）方式逐步產生結果，提升效能與用戶體驗。

### 🔧 核心功能特色

- **三種通訊模式**：Unary（單次）、Output Streaming（流式輸出）、GetServiceInfo（服務資訊查詢）
- **嚴格型別資料模型**：明確定義 Document、ComposeRequest、ComposeResponse
- **gRPC 協定自動對應**：與 Protocol Buffer 完美對接
- **可擴展處理器註冊**：支援動態/靜態註冊處理器
- **錯誤處理標準化**：回應皆含 ErrorDetail，便於追蹤與除錯

---

## 專案結構圖與模組詳解

### 整體架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── bricks/
│   │   └── compose/
│   │       ├── __init__.py
│   │       └── base_compose.py         # ComposeBrick 主體實作
│   ├── protocols/
│   │   ├── grpc/
│   │   │   └── compose/
│   │   │       ├── compose.proto       # Protocol Buffer 定義
│   │   │       ├── compose_pb2.py      # 自動生成的訊息類別
│   │   │       └── compose_pb2_grpc.py # gRPC 服務存根
│   │   └── models/
│   │       └── bricks/
│   │           └── compose_types.py    # Compose 資料模型
│   └── core/
│       └── brick.py                    # BaseBrick 抽象基礎類別
```

### 核心模組詳細說明

#### 1. [BaseBrick](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L1) - 抽象基礎類別

- **職責**：所有 Brick 的基礎類別，定義標準介面、型別、裝飾器與執行流程。
- **泛型支援**：`BaseBrick[InputT, OutputT]`，型別安全。
- **處理器管理**：自動註冊與管理多種 handler。
- **錯誤處理**：統一異常捕獲與日誌。

#### 2. [ComposeBrick](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/compose/base_compose.py#L1) - 複合統整 Brick

- **職責**：多文件統整、格式轉換、翻譯等複合型任務的標準服務。
- **gRPC 對應**：僅支援 `Unary`、`OutputStreaming`、`GetServiceInfo` 三種 handler。
- **型別限制**：僅允許註冊 `unary`、`output_streaming`、`get_service_info` 三種處理器。
- **gRPC 客戶端轉換**：`toGrpcClient()` 可自動產生 gRPC client。

#### 3. [compose.proto](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/compose/compose.proto#L1) - gRPC 協定定義

- **Document**：單一文件結構
- **ComposeRequest**：多文件統整請求
- **ComposeResponse**：統整結果
- **ComposeService**：gRPC 服務，含三個方法

#### 4. [compose_types.py](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/compose_types.py#L1) - 資料模型

- **Document**：文件物件
- **ComposeRequest**：請求物件
- **ComposeResponse**：回應物件，含 output 與 error 欄位

---

## 安裝與環境設定指南

### 依賴需求

ComposeBrick 需依賴以下核心套件：

```bash
# 必要依賴
grpcio>=1.50.0
grpcio-tools>=1.50.0
protobuf>=4.21.0
google-protobuf>=4.21.0
```

### 自動化安裝步驟

#### 1. 安裝 LLMBrick 套件

```bash
# 從 PyPI 安裝
pip install llmbrick

# 或從源碼安裝
git clone https://github.com/JiHungLin/llmbrick.git
cd llmbrick
pip install -e .
```

#### 2. 驗證安裝

```python
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse

print("✅ ComposeBrick 安裝成功！")
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

### 1. 最簡單的 ComposeBrick 使用

```python
import asyncio
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse, Document

async def basic_example():
    # 建立 ComposeBrick 實例
    brick = ComposeBrick()

    # 註冊單次統整處理器
    @brick.unary()
    async def compose_handler(request: ComposeRequest) -> ComposeResponse:
        # 將所有文件標題串接
        titles = [doc.title for doc in request.input_documents]
        output = {
            "summary": "；".join(titles),
            "format": request.target_format or "plain"
        }
        return ComposeResponse(output=output)

    # 執行請求
    docs = [
        Document(doc_id="1", title="文件A", snippet="內容A"),
        Document(doc_id="2", title="文件B", snippet="內容B"),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")
    response = await brick.run_unary(request)
    print(f"統整結果: {response.output}")

asyncio.run(basic_example())
```

### 2. 類別繼承方式定義 ComposeBrick

```python
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse, Document
from llmbrick.core.brick import unary_handler, output_streaming_handler
from typing import AsyncIterator

class MyComposeBrick(ComposeBrick):
    """自訂複合統整 Brick 範例"""

    @unary_handler
    async def summarize_titles(self, request: ComposeRequest) -> ComposeResponse:
        titles = [doc.title for doc in request.input_documents]
        return ComposeResponse(output={"summary": "、".join(titles)})

    @output_streaming_handler
    async def stream_snippets(self, request: ComposeRequest) -> AsyncIterator[ComposeResponse]:
        for doc in request.input_documents:
            yield ComposeResponse(output={"doc_id": doc.doc_id, "snippet": doc.snippet})

# 使用範例
async def advanced_example():
    brick = MyComposeBrick()
    docs = [
        Document(doc_id="1", title="A", snippet="內容A"),
        Document(doc_id="2", title="B", snippet="內容B"),
    ]
    request = ComposeRequest(input_documents=docs)
    # 單次統整
    response = await brick.run_unary(request)
    print("摘要:", response.output)
    # 流式輸出
    async for resp in brick.run_output_streaming(request):
        print("流式片段:", resp.output)

import asyncio
asyncio.run(advanced_example())
```

### 3. gRPC 服務端建立與部署

```python
# grpc_server.py
import asyncio
from llmbrick.servers.grpc.server import GrpcServer
from my_compose_brick import MyComposeBrick  # 需自訂

async def start_grpc_server():
    server = GrpcServer(port=50052)
    brick = MyComposeBrick()
    server.register_service(brick)
    print("🚀 ComposeBrick gRPC 服務器啟動中...")
    await server.start()

if __name__ == "__main__":
    asyncio.run(start_grpc_server())
```

### 4. gRPC 客戶端連接與使用

```python
# grpc_client.py
import asyncio
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, Document

async def grpc_client_example():
    # 建立 gRPC 客戶端
    client = ComposeBrick.toGrpcClient("localhost:50052")
    docs = [
        Document(doc_id="1", title="A", snippet="內容A"),
        Document(doc_id="2", title="B", snippet="內容B"),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")
    # 單次請求
    response = await client.run_unary(request)
    print("gRPC 統整結果:", response.output)
    # 流式請求
    async for resp in client.run_output_streaming(request):
        print("gRPC 流式片段:", resp.output)

asyncio.run(grpc_client_example())
```

---

## 核心 API / 類別 / 函式深度解析

### [ComposeBrick](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/compose/base_compose.py#L17) 類別

#### 類別簽名與繼承關係

```python
class ComposeBrick(BaseBrick[ComposeRequest, ComposeResponse]):
    brick_type = BrickType.COMPOSE
    allowed_handler_types = {"unary", "output_streaming", "get_service_info"}
```

- **僅允許三種 handler**：unary、output_streaming、get_service_info
- **不支援 input_streaming、bidi_streaming**（呼叫會拋出 NotImplementedError）

#### [toGrpcClient()](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/compose/base_compose.py#L67) - gRPC 客戶端轉換

```python
@classmethod
def toGrpcClient(cls, remote_address: str, **kwargs) -> ComposeBrick
```

- **功能**：產生一個可直接呼叫 gRPC 服務的 ComposeBrick 實例
- **參數**：
  - `remote_address: str` - 伺服器位址（如 "localhost:50052"）
  - `**kwargs` - 傳遞給建構子的其他參數
- **回傳**：gRPC 客戶端型態的 ComposeBrick
- **注意**：每次呼叫都會建立新的 gRPC channel，適合短期用，長期建議自行管理連線池

#### 標準執行方法

##### [run_unary()](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L233) - 單次請求

```python
async def run_unary(self, input_data: ComposeRequest) -> ComposeResponse
```
- **功能**：執行單次統整/轉換任務
- **參數**：`input_data` 為 ComposeRequest
- **回傳**：ComposeResponse

##### [run_output_streaming()](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L258) - 流式輸出

```python
async def run_output_streaming(self, input_data: ComposeRequest) -> AsyncIterator[ComposeResponse]
```
- **功能**：將多份文件逐步流式輸出
- **回傳**：異步迭代器，逐步產生 ComposeResponse

##### [run_get_service_info()](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L245) - 服務資訊查詢

```python
async def run_get_service_info(self) -> ServiceInfoResponse
```
- **功能**：查詢服務名稱、版本、支援模型等資訊

#### 資料模型

##### [Document](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/compose_types.py#L11)

```python
@dataclass
class Document:
    doc_id: str
    title: str
    snippet: str
    score: float
    metadata: Dict[str, Any]
```

##### [ComposeRequest](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/compose_types.py#L33)

```python
@dataclass
class ComposeRequest:
    input_documents: List[Document]
    target_format: str
    client_id: str
    session_id: str
    request_id: str
    source_language: str
```

##### [ComposeResponse](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/compose_types.py#L72)

```python
@dataclass
class ComposeResponse:
    output: Dict[str, Any]
    error: Optional[ErrorDetail]
```

---

## 常見錯誤與排解

- **註冊不支援的 handler**  
  - 僅允許註冊 `unary`、`output_streaming`、`get_service_info`，否則會拋出 NotImplementedError。
- **gRPC 連線失敗**  
  - 檢查 remote_address 是否正確、gRPC server 是否啟動。
- **資料型別不符**  
  - 請確保 input_documents 為 Document 物件列表，output 為 dict。
- **Protocol Buffer 版本不符**  
  - 請確保 grpcio、protobuf 版本與專案需求一致。

---

## 效能優化與最佳實踐

- **流式輸出**：對於大量文件，建議使用 output_streaming，減少記憶體壓力。
- **gRPC 客戶端重用**：長期大量請求時，建議自行管理 channel，避免頻繁建立/關閉。
- **資料驗證**：在 handler 內部加強對 input_documents、target_format 等欄位的檢查。
- **錯誤回報**：務必填寫 ComposeResponse.error，便於前後端協作除錯。

---

## FAQ / 進階問答

### Q1: ComposeBrick 與 CommonBrick 差異？

**A**：ComposeBrick 專為「多文件統整、格式轉換」等複合型任務設計，僅支援 unary/output_streaming，且資料模型更嚴謹（Document/ComposeRequest/ComposeResponse）。CommonBrick 則為通用型，支援所有通訊模式。

### Q2: 可以串接 LLMBrick/GuardBrick 嗎？

**A**：可以。ComposeBrick 可作為前置/後置處理，與其他 Brick 組合實現更複雜的 AI pipeline。

### Q3: 如何自訂 output 格式？

**A**：在 handler 內部依據 request.target_format 動態產生 output（如 JSON、HTML、Markdown），並填入 ComposeResponse.output。

### Q4: 為什麼 input_streaming/bidi_streaming 會報錯？

**A**：ComposeBrick 僅設計支援 unary/output_streaming，呼叫 input_streaming/bidi_streaming 會直接拋出 NotImplementedError，請改用支援的模式。

---

## 參考資源與延伸閱讀

- [LLMBrick 框架介紹](../../intro.md)
- [gRPC Server 使用指南](../servers/grpc_server_guide.md)
- [BaseBrick API 文件](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L1)
- [ComposeBrick 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/compose_brick_define)
- [Protocol Buffer 官方文件](https://developers.google.com/protocol-buffers)
- [gRPC Python 官方文件](https://grpc.io/docs/languages/python/)
- [asyncio 官方文件](https://docs.python.org/3/library/asyncio.html)
- [問題回報](https://github.com/JiHungLin/llmbrick/issues)

---

ComposeBrick 是構建多文件統整、格式轉換、AI 輔助摘要等應用的強大基石。熟練掌握其用法，能大幅提升 AI 產品的開發效率與可維護性。

*本指南持續更新中，歡迎社群貢獻與討論！*
