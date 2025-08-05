# IntentionBrick 使用指南

## 目錄
- [概述](#概述)
- [架構設計](#架構設計)
- [快速開始](#快速開始)
- [單機版使用](#單機版使用)
- [gRPC 版使用](#grpc-版使用)
- [最佳實踐](#最佳實踐)
- [錯誤處理](#錯誤處理)
- [常見問題](#常見問題)
- [總結](#總結)

## 概述

IntentionBrick 是 LLMBrick 框架中專為「意圖判斷」設計的元件，提供統一的異步處理介面，支援本地調用與遠端 gRPC 調用的無縫切換。  
**僅支援兩種處理模式：**
- Unary（單次請求-回應）
- GetServiceInfo（服務資訊查詢）

## 架構設計

### 設計模式

1. **裝飾器模式**：使用 `@unary_handler`, `@get_service_info_handler` 註冊處理函數
2. **適配器模式**：`IntentionGrpcWrapper` 提供 gRPC 與本地調用之間的適配
3. **工廠模式**：`toGrpcClient()` 動態創建 gRPC 客戶端
4. **策略模式**：支援本地/遠端兩種調用策略

### 核心組件

```
IntentionBrick (核心類)
├── BaseBrick (基礎類)
├── IntentionGrpcWrapper (gRPC 包裝器)
├── IntentionRequest/IntentionResponse/IntentionResult (數據模型)
└── 處理器裝飾器 (@unary_handler, @get_service_info_handler)
```

## 快速開始

### 基本安裝

```python
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.intention_types import (
    IntentionRequest, IntentionResponse, IntentionResult
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail, ServiceInfoResponse
)
```

### 最簡單的 IntentionBrick 實現

```python
class SimpleIntentionBrick(IntentionBrick):
    @unary_handler
    async def process(self, request: IntentionRequest) -> IntentionResponse:
        return IntentionResponse(
            results=[IntentionResult(intent_category="greet", confidence=1.0)],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleIntentionBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

## 單機版使用

### 1. 創建和使用 Brick

```python
import asyncio

async def main():
    brick = SimpleIntentionBrick(verbose=False)
    request = IntentionRequest(text="你好", client_id="cid")
    response = await brick.run_unary(request)
    print(f"Intent: {response.results[0].intent_category}, confidence: {response.results[0].confidence}")

asyncio.run(main())
```

### 2. API 一致性

IntentionBrick 的本地與 gRPC 客戶端 API 完全一致，開發者可無縫切換。

## gRPC 版使用

### 1. 服務端設置

```python
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

async def start_grpc_server():
    brick = SimpleIntentionBrick(verbose=True)
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

asyncio.run(start_grpc_server())
```

### 2. 客戶端使用

```python
async def use_grpc_client():
    client_brick = SimpleIntentionBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        verbose=False
    )
    try:
        request = IntentionRequest(text="hello", client_id="cid")
        response = await client_brick.run_unary(request)
        print(f"gRPC Intent: {response.results[0].intent_category}")

asyncio.run(use_grpc_client())
```

### 3. 無縫切換示例

```python
# 本地使用
local_brick = SimpleIntentionBrick(verbose=False)
# 遠端使用
remote_brick = SimpleIntentionBrick.toGrpcClient("127.0.0.1:50051", verbose=False)

async def process(brick, text):
    request = IntentionRequest(text=text, client_id="cid")
    return await brick.run_unary(request)

result1 = await process(local_brick, "hi")
result2 = await process(remote_brick, "hi")
```

## 最佳實踐

### 1. 僅支援 async handler

所有 handler 必須為 async function，否則會在註冊或執行時出錯。

### 2. 僅支援 unary/get_service_info

IntentionBrick 不支援 streaming handler，註冊其他 handler 會直接拋出 NotImplementedError。

### 3. 錯誤處理建議

- 請務必回傳正確的 ErrorDetail，error.code=ErrorCodes.SUCCESS 代表成功，非 0 代表錯誤。
- handler 若回傳型別錯誤，gRPC wrapper 會自動回傳 error code 500。
- handler 拋出異常時，gRPC 端會回傳 INTERNAL 錯誤。

### 4. 測試建議

- 建議參考 `tests/unit/test_intention_brick_standalone.py` 及 `tests/e2e/test_intention_grpc.py`，涵蓋本地與 gRPC、正常與異常情境。
- 可用 pytest/pytest-asyncio 撰寫 async 測試。

## 錯誤處理

- 使用 ErrorDetail 回報業務錯誤，並善用 error.code/message/detail。
- handler 未註冊時，呼叫對應 run_xxx 會拋出 NotImplementedError。
- handler 拋出異常時，gRPC 端會自動包裝為 error.code=13 (INTERNAL)。

## 常見問題

### Q1: 可以註冊 streaming handler 嗎？
A: 不行，IntentionBrick 僅允許 unary/get_service_info，註冊其他 handler 會警告並拋出 NotImplementedError。

### Q2: 如何切換本地與 gRPC？
A: 只需用 `toGrpcClient()` 創建遠端 client，API 完全一致，無需修改業務邏輯。

### Q3: handler 必須是 async 嗎？
A: 是，所有 handler 必須為 async function，否則會在註冊或執行時出錯。

## 總結

IntentionBrick 提供簡潔、統一的意圖判斷服務元件，支援本地與 gRPC 無縫切換，API 設計直覺、易於測試。  
**限制：** 僅支援 unary/get_service_info，所有 handler 必須為 async function。  
建議參考本指南與測試案例，實現穩定、可維護的意圖判斷服務。