# ComposeBrick 使用指南

## 目錄
- [概述](#概述)
- [架構設計](#架構設計)
- [快速開始](#快速開始)
- [單機版使用](#單機版使用)
- [gRPC 版使用](#grpc-版使用)
- [無縫切換示例](#無縫切換示例)
- [最佳實踐](#最佳實踐)
- [錯誤處理](#錯誤處理)
- [性能考慮](#性能考慮)
- [常見問題](#常見問題)
- [總結](#總結)

## 概述

ComposeBrick 是 LLMBrick 框架中專為「資料統整、轉換、翻譯」等複合型服務設計的核心組件。  
它提供統一的異步處理介面，支援本地調用和遠端 gRPC 調用的無縫切換。  
**僅支援三種處理模式**：
- Unary（單次請求-回應）
- Output Streaming（單次請求-流式回應）
- GetServiceInfo（服務資訊查詢）

## 架構設計

### 設計模式

1. **裝飾器模式**：使用 `@unary_handler`, `@output_streaming_handler`, `@get_service_info_handler` 註冊處理函數
2. **適配器模式**：`ComposeGrpcWrapper` 提供 gRPC 與本地調用的適配
3. **工廠模式**：`toGrpcClient()` 動態創建 gRPC 客戶端
4. **策略模式**：支援本地/遠端多種調用策略

### 核心組件

```
ComposeBrick (核心類)
├── BaseBrick (基礎類)
├── ComposeGrpcWrapper (gRPC 包裝器)
├── ComposeRequest/ComposeResponse (數據模型)
└── 處理器裝飾器 (@unary_handler, @output_streaming_handler, @get_service_info_handler)
```

## 快速開始

### 基本安裝

```python
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
```

### 最簡單的 ComposeBrick 實現

```python
class SimpleCompose(ComposeBrick):
    @unary_handler
    async def process(self, request: ComposeRequest) -> ComposeResponse:
        return ComposeResponse(
            output={"message": f"文件數量: {len(request.input_documents)}"},
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleCompose",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

## 單機版使用

### 1. 創建和使用 ComposeBrick

```python
import asyncio
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest

async def main():
    brick = SimpleCompose(verbose=False)
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "B", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")
    response = await brick.run_unary(request)
    print(f"Response: {response.output['message']}")

asyncio.run(main())
```

### 2. 實現所有支援的處理模式

```python
from typing import AsyncIterator

class FullFeatureCompose(ComposeBrick):
    @unary_handler
    async def unary_process(self, request: ComposeRequest) -> ComposeResponse:
        return ComposeResponse(
            output={"count": len(request.input_documents)},
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @output_streaming_handler
    async def stream_titles(self, request: ComposeRequest) -> AsyncIterator[ComposeResponse]:
        for idx, doc in enumerate(request.input_documents):
            yield ComposeResponse(
                output={"index": idx, "title": doc.title},
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )

    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="FullFeatureCompose",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

### 3. 使用範例

```python
async def demonstrate_all_modes():
    brick = FullFeatureCompose(verbose=False)
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "B", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]

    # 1. Unary 調用
    response = await brick.run_unary(ComposeRequest(input_documents=docs, target_format="json"))
    print(f"Unary result: {response.output['count']}")  # 2

    # 2. Output Streaming
    async for response in brick.run_output_streaming(ComposeRequest(input_documents=docs, target_format="json")):
        print(f"Stream output: {response.output}")

    # 3. GetServiceInfo
    info = await brick.run_get_service_info()
    print(f"Service name: {info.service_name}")
```

## gRPC 版使用

### 1. 服務端設置

```python
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

async def start_grpc_server():
    brick = FullFeatureCompose(verbose=True)
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

asyncio.run(start_grpc_server())
```

### 2. 客戶端使用

```python
async def use_grpc_client():
    client_brick = FullFeatureCompose.toGrpcClient(
        remote_address="127.0.0.1:50051",
        verbose=False
    )
    try:
        docs = [
            type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        ]
        response = await client_brick.run_unary(
            ComposeRequest(input_documents=docs, target_format="json")
        )
        print(f"gRPC result: {response.output['count']}")  # 1

        async for response in client_brick.run_output_streaming(
            ComposeRequest(input_documents=docs, target_format="json")
        ):
            print(f"gRPC stream: {response.output}")

asyncio.run(use_grpc_client())
```

## 無縫切換示例

ComposeBrick 支援本地與遠端（gRPC）兩種模式，API 完全一致：

```python
# 本地使用
local_brick = FullFeatureCompose(verbose=False)

# 遠端使用
remote_brick = FullFeatureCompose.toGrpcClient("127.0.0.1:50051", verbose=False)

async def process_data(brick, docs):
    request = ComposeRequest(input_documents=docs, target_format="json")
    return await brick.run_unary(request)

docs = [
    type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
]
result1 = await process_data(local_brick, docs)
result2 = await process_data(remote_brick, docs)
```

## 最佳實踐

### 1. 嚴格使用 async function

- 所有 handler 必須是 async function，且加上正確型別註解。
- 回傳型別必須為 ComposeResponse 或 ServiceInfoResponse。
- 若 handler 未正確註冊或型別錯誤，會在 runtime 報錯。

### 2. 錯誤處理

- handler 內部務必做好錯誤處理，回傳標準化的 error 結構。
- 建議使用 ErrorDetail，並明確標註 code/message。

### 3. 測試覆蓋

- 建議同時測試本地與 gRPC 兩種模式，確保一致性。
- 可參考 `tests/unit/test_compose_brick_standalone.py` 及 `tests/e2e/test_compose_grpc.py`。

### 4. 不支援的 handler

- ComposeBrick 僅支援 unary、output_streaming、get_service_info，若註冊 input_streaming 或 bidi_streaming 會直接丟出 NotImplementedError。

### 5. 文件與型別設計

- 輸入文件（input_documents）建議使用 dataclass 或 namedtuple，需包含 doc_id、title、snippet、score、metadata 等欄位。

## 錯誤處理

- ComposeGrpcWrapper 會自動將 handler 例外轉換為 gRPC error response，方便除錯。
- handler 回傳型別錯誤時，會有明確的錯誤訊息。
- 建議所有 handler 都要有 try/except 包裝，並回傳 ErrorDetail。

## 性能考慮

- 建議在 output_streaming handler 中使用 async for/yield，避免一次回傳大量資料造成記憶體壓力。
- 可利用 asyncio.Semaphore 控制並發數量。

## 常見問題

### Q1: 為什麼 input_streaming/bidi_streaming 會報錯？
A: ComposeBrick 僅支援 unary、output_streaming、get_service_info，其他 handler 會直接丟出 NotImplementedError。

### Q2: handler 必須是 async function 嗎？
A: 是，所有 handler 必須是 async function，否則會在 runtime 報錯。

### Q3: 如何自訂輸入文件型別？
A: 輸入文件建議使用 dataclass 或 namedtuple，需包含 doc_id、title、snippet、score、metadata 等欄位。

### Q4: 如何切換本地與遠端？
A: 只需分別用 `ComposeBrick()` 或 `ComposeBrick.toGrpcClient(address)` 建立實例，API 完全一致。

## 總結

ComposeBrick 提供聚焦於資料統整/轉換/翻譯的高效異步服務框架，  
其主要優點包括：
1. **統一 API**：本地與遠端調用完全一致
2. **明確聚焦**：僅支援最常用的三種模式，簡潔易懂
3. **優雅錯誤處理**：自動型別檢查與錯誤回報
4. **高性能**：基於 asyncio 的高效異步處理
5. **易於測試**：介面清晰、測試工具齊全

建議開發人員嚴格遵循 async function 定義、型別註解與錯誤處理最佳實踐，  
即可輕鬆打造穩定、靈活的 Compose 服務。