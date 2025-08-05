# RetrievalBrick 使用指南

## 目錄
- [概述](#概述)
- [架構設計](#架構設計)
- [快速開始](#快速開始)
- [單機版使用](#單機版使用)
- [gRPC 版使用](#grpc-版使用)
- [最佳實踐](#最佳實踐)
- [錯誤處理](#錯誤處理)
- [常見問題](#常見問題)

## 概述

RetrievalBrick 是 LLMBrick 框架中專為「檢索」設計的元件，提供統一的異步處理介面，支援本地調用和遠程 gRPC 調用的無縫切換。  
**僅支援兩種處理模式：**
- Unary（單次請求-回應）
- GetServiceInfo（服務資訊查詢）

不支援 streaming handler，註冊其他 handler 會直接拋出 NotImplementedError。

## 架構設計

### 設計模式

1. **裝飾器模式**：使用 `@unary_handler`, `@get_service_info_handler` 註冊處理函數
2. **適配器模式**：`RetrievalGrpcWrapper` 提供 gRPC 和本地調用之間的適配
3. **工廠模式**：`toGrpcClient()` 動態創建 gRPC 客戶端
4. **策略模式**：支援本地/遠端多種調用策略

### 核心組件

```
RetrievalBrick (核心類)
├── BaseBrick (基礎類)
├── RetrievalGrpcWrapper (gRPC 包裝器)
├── RetrievalRequest/RetrievalResponse (數據模型)
└── 處理器裝飾器 (@unary_handler, @get_service_info_handler)
```

gRPC 服務與 Brick Handler 對應表：

| gRPC 方法         | Brick Handler         |
|-------------------|----------------------|
| GetServiceInfo    | get_service_info     |
| Unary             | unary                |

## 快速開始

### 基本安裝

```python
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.retrieval_types import (
    RetrievalRequest, RetrievalResponse
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail, ServiceInfoResponse
)
```

### 最簡單的 RetrievalBrick 實現

```python
class SimpleRetrievalBrick(RetrievalBrick):
    @unary_handler
    async def search(self, request: RetrievalRequest) -> RetrievalResponse:
        return RetrievalResponse(
            documents=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleRetrievalBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

## 單機版使用

```python
import asyncio
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest

async def main():
    brick = SimpleRetrievalBrick()
    req = RetrievalRequest(query="test", client_id="cid")
    resp = await brick.run_unary(req)
    print(resp.documents)
    info = await brick.run_get_service_info()
    print(info.service_name)

asyncio.run(main())
```

## gRPC 版使用

### 1. 服務端設置

```python
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

async def start_grpc_server():
    brick = SimpleRetrievalBrick()
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

asyncio.run(start_grpc_server())
```

### 2. 客戶端使用

```python
async def use_grpc_client():
    client_brick = SimpleRetrievalBrick.toGrpcClient(
        remote_address="127.0.0.1:50051"
    )
    req = RetrievalRequest(query="test", client_id="cid")
    resp = await client_brick.run_unary(req)
    print(resp.documents)

asyncio.run(use_grpc_client())
```

### 3. 無縫切換示例

```python
# 本地使用
local_brick = SimpleRetrievalBrick()
# 遠端使用
remote_brick = SimpleRetrievalBrick.toGrpcClient("127.0.0.1:50051")

async def process(brick, query):
    req = RetrievalRequest(query=query, client_id="cid")
    return await brick.run_unary(req)

result1 = await process(local_brick, "foo")
result2 = await process(remote_brick, "bar")
```

## 最佳實踐

### 1. handler 必須為 async function

所有 handler（unary, get_service_info）都必須是 async function，否則會在執行時遇到 TypeError。

```python
class BadBrick(RetrievalBrick):
    @unary_handler
    def bad_search(self, request: RetrievalRequest):  # 錯誤：缺少 async
        return RetrievalResponse(documents=[], error=ErrorDetail(code=ErrorCodes.SUCCESS, message="ok"))
# 執行 brick.run_unary() 會拋出 TypeError
```

### 2. 錯誤處理建議

建議在 handler 內妥善處理異常，並回傳 ErrorDetail，避免未捕獲異常導致 gRPC 連線中斷。

```python
@unary_handler
async def robust_search(self, request: RetrievalRequest) -> RetrievalResponse:
    try:
        # 檢索邏輯
        ...
        return RetrievalResponse(documents=[...], error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"))
    except ValueError as e:
        return RetrievalResponse(documents=[], error=ErrorDetail(code=400, message=str(e)))
    except Exception as e:
        return RetrievalResponse(documents=[], error=ErrorDetail(code=500, message="Internal error", detail=str(e)))
```

### 3. 型別安全與 IDE 補全

建議明確標註 handler 的 input/output 型別，提升 IDE 補全與可維護性。

## 錯誤處理

- handler 未註冊時，執行對應 run_xxx 會拋出 NotImplementedError
- handler 非 async function，執行時會拋出 TypeError
- 回傳 error 請使用 ErrorDetail，並明確標註 code/message

## 常見問題

### Q1: 可以註冊 streaming handler 嗎？
A: RetrievalBrick 僅支援 unary 與 get_service_info，註冊 streaming handler 會直接拋出 NotImplementedError。

### Q2: handler 必須是 async function 嗎？
A: 是，否則會在執行時遇到 TypeError。

### Q3: 如何切換本地與 gRPC 模式？
A: 只需分別用 `RetrievalBrick()` 或 `RetrievalBrick.toGrpcClient(address)`，API 完全一致。

### Q4: 如何測試 RetrievalBrick？
A: 參考 `tests/unit/test_retrieval_brick_standalone.py`（單機）與 `tests/e2e/test_retrieval_grpc.py`（gRPC）範例。

---

RetrievalBrick 提供統一、直覺的檢索服務開發體驗，建議遵循本指南最佳實踐，確保服務穩定、易於維護。