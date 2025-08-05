# RectifyBrick 使用指南

## 目錄
- [概述](#概述)
- [架構設計](#架構設計)
- [快速開始](#快速開始)
- [單機版使用](#單機版使用)
- [gRPC版使用](#grpc版使用)
- [最佳實踐](#最佳實踐)
- [錯誤處理](#錯誤處理)
- [常見問題](#常見問題)

## 概述

RectifyBrick 是 LLMBrick 框架中專為「文本校正」設計的元件，提供統一的異步處理介面，支援本地調用和遠程 gRPC 調用的無縫切換。  
目前僅支援兩種處理模式：
- **Unary**: 單次請求-回應
- **GetServiceInfo**: 查詢服務資訊

## 架構設計

### 設計模式

1. **裝飾器模式**: 使用 `@unary_handler`, `@get_service_info_handler` 註冊處理函數
2. **適配器模式**: `RectifyGrpcWrapper` 提供 gRPC 和本地調用之間的適配
3. **工廠模式**: `toGrpcClient()` 動態創建 gRPC 客戶端
4. **策略模式**: 支援本地/遠程多種調用策略

### 核心組件

```
RectifyBrick (核心類)
├── BaseBrick (基礎類)
├── RectifyGrpcWrapper (gRPC 包裝器)
├── RectifyRequest/RectifyResponse (數據模型)
└── 處理器裝飾器 (@unary_handler, @get_service_info_handler)
```

## 快速開始

### 基本安裝

```python
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
```

### 最簡單的 Brick 實現

```python
class SimpleRectifyBrick(RectifyBrick):
    @unary_handler
    async def rectify_handler(self, request: RectifyRequest) -> RectifyResponse:
        return RectifyResponse(
            corrected_text=request.text.upper(),
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleRectifyBrick",
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
    brick = SimpleRectifyBrick(verbose=False)
    request = RectifyRequest(text="hello", client_id="cli", session_id="s1", request_id="r1", source_language="en")
    response = await brick.run_unary(request)
    print(f"Corrected: {response.corrected_text}")  # 輸出: Corrected: HELLO

asyncio.run(main())
```

### 2. 服務資訊查詢

```python
info = await brick.run_get_service_info()
print(info.service_name, info.version)
```

## gRPC版使用

### 1. 服務端設置

```python
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

async def start_grpc_server():
    brick = SimpleRectifyBrick(verbose=True)
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

asyncio.run(start_grpc_server())
```

### 2. 客戶端使用

```python
async def use_grpc_client():
    client_brick = SimpleRectifyBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        verbose=False
    )
    try:
        request = RectifyRequest(text="abc", client_id="cli", session_id="s1", request_id="r1", source_language="en")
        response = await client_brick.run_unary(request)
        print(f"gRPC result: {response.corrected_text}")  # CBA

asyncio.run(use_grpc_client())
```

### 3. 無縫切換示例

```python
# 本地使用
local_brick = SimpleRectifyBrick(verbose=False)
# 遠程使用
remote_brick = SimpleRectifyBrick.toGrpcClient("127.0.0.1:50051", verbose=False)

async def process(brick, text):
    request = RectifyRequest(text=text, client_id="cli", session_id="s1", request_id="r1", source_language="en")
    return await brick.run_unary(request)

result1 = await process(local_brick, "abc")
result2 = await process(remote_brick, "abc")
```

## 最佳實踐

### 1. 異步函數設計

- 所有 handler 必須為 async function。
- 輸入驗證、錯誤處理建議統一包裝於 ErrorDetail。
- 建議將業務邏輯與 handler 分離，便於測試與維護。

### 2. 錯誤處理策略

- 回傳 ErrorDetail，並設置 code/message。
- 建議對常見錯誤（如參數缺失、型別錯誤）給予明確錯誤碼與訊息。

### 3. 型別安全

- 請確保 RectifyRequest/RectifyResponse 欄位與 proto 定義一致。
- gRPC wrapper 會自動檢查型別，型別錯誤會回傳 error。

## 錯誤處理

- handler 必須回傳 RectifyResponse，否則會被 wrapper 捕捉並回傳錯誤。
- 不支援的 handler（如 streaming）會丟出 NotImplementedError。

## 常見問題

### Q1: 如何擴充支援 streaming handler？
A: 目前 RectifyBrick 僅支援 unary/get_service_info，若需 streaming，需擴充 proto、BaseBrick 與 RectifyBrick 實作。

### Q2: handler 必須是 async function 嗎？
A: 是，所有 handler 必須 async，否則會出現執行錯誤。


## 總結

RectifyBrick 提供簡潔、統一的文本校正服務元件，支援本地與 gRPC 無縫切換，API 一致、async 支援完整、型別安全。  
可考慮未來支援 streaming handler 以提升靈活性。