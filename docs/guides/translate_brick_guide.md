# TranslateBrick 使用指南

## 目錄
- [概述](#概述)
- [架構設計](#架構設計)
- [快速開始](#快速開始)
- [單機版使用](#單機版使用)
- [gRPC版使用](#grpc版使用)
- [無縫切換示例](#無縫切換示例)
- [最佳實踐](#最佳實踐)
- [常見問題](#常見問題)
- [測試建議](#測試建議)

## 概述

TranslateBrick 是 LLMBrick 框架中專為翻譯/轉換場景設計的元件，提供統一的異步處理介面，支援本地調用與遠端 gRPC 調用的無縫切換。  
**僅支援三種處理模式**：
- Unary（單次請求-回應）
- Output Streaming（單次請求-流式回應）
- GetServiceInfo（查詢服務資訊）

## 架構設計

### 設計模式

1. **裝飾器模式**：使用 `@unary_handler`, `@output_streaming_handler`, `@get_service_info_handler` 註冊處理函數
2. **適配器模式**：`TranslateGrpcWrapper` 提供 gRPC 與本地調用的適配
3. **工廠模式**：`toGrpcClient()` 動態創建 gRPC 客戶端
4. **策略模式**：支援本地/遠端多種調用策略

### 核心組件

```
TranslateBrick (核心類)
├── BaseBrick (基礎類)
├── TranslateGrpcWrapper (gRPC 包裝器)
├── TranslateRequest/TranslateResponse (數據模型)
└── 處理器裝飾器 (@unary_handler, @output_streaming_handler, @get_service_info_handler)
```

### 支援模式

| gRPC 方法         | Brick Handler         | 支援 |
|-------------------|----------------------|------|
| GetServiceInfo    | get_service_info     | ✔    |
| Unary             | unary                | ✔    |
| OutputStreaming   | output_streaming     | ✔    |
| InputStreaming    | input_streaming      | ✖    |
| BidiStreaming     | bidi_streaming       | ✖    |

## 快速開始

### 基本安裝

```python
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.translate_types import (
    TranslateRequest, TranslateResponse
)
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
```

### 最簡單的 TranslateBrick 實現

```python
class SimpleTranslator(TranslateBrick):
    @unary_handler
    async def echo_translate(self, request: TranslateRequest) -> TranslateResponse:
        return TranslateResponse(
            text=f"{request.text} (to {request.target_language})",
            tokens=[1, 2, 3],
            language_code=request.target_language,
            is_final=True,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

    @output_streaming_handler
    async def stream_translate(self, request: TranslateRequest):
        for i, word in enumerate(request.text.split()):
            yield TranslateResponse(
                text=f"{word} (t{i})",
                tokens=[i],
                language_code=request.target_language,
                is_final=(i == len(request.text.split()) - 1),
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
            )

    @get_service_info_handler
    async def service_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleTranslator",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )
```

## 單機版使用

```python
import asyncio

async def main():
    brick = SimpleTranslator(verbose=False)
    request = TranslateRequest(
        text="Hello world",
        model_id="simple-translator",
        target_language="zh",
        client_id="test",
        session_id="s1",
        request_id="r1",
        source_language="en",
    )
    response = await brick.run_unary(request)
    print(response.text)  # Hello world (to zh)

    # Output streaming
    async for resp in brick.run_output_streaming(request):
        print(resp.text)

    # Get service info
    info = await brick.run_get_service_info()
    print(info.service_name)

asyncio.run(main())
```

## gRPC版使用

### 1. 服務端設置

```python
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

async def start_grpc_server():
    brick = SimpleTranslator(verbose=True)
    server = GrpcServer(port=50071)
    server.register_service(brick)
    await server.start()

asyncio.run(start_grpc_server())
```

### 2. 客戶端使用

```python
async def use_grpc_client():
    client_brick = SimpleTranslator.toGrpcClient(
        remote_address="127.0.0.1:50071",
        verbose=False
    )
    request = TranslateRequest(
        text="Hello world",
        model_id="simple-translator",
        target_language="zh",
        client_id="test",
        session_id="s1",
        request_id="r1",
        source_language="en",
    )
    response = await client_brick.run_unary(request)
    print(response.text)

asyncio.run(use_grpc_client())
```

## 無縫切換示例

```python
# 本地
local_brick = SimpleTranslator(verbose=False)
# 遠端
remote_brick = SimpleTranslator.toGrpcClient("127.0.0.1:50071", verbose=False)

async def process(brick, text):
    req = TranslateRequest(
        text=text,
        model_id="simple-translator",
        target_language="zh",
        client_id="test",
        session_id="s1",
        request_id="r1",
        source_language="en",
    )
    return await brick.run_unary(req)

result1 = await process(local_brick, "Hello")
result2 = await process(remote_brick, "Hello")
```
> API 完全一致，僅建構方式不同。

## 最佳實踐

### 1. 僅實作支援的 handler

TranslateBrick 只允許 `unary`、`output_streaming`、`get_service_info`，其他 handler 會丟出 NotImplementedError。

### 2. 全部 handler 必須 async

所有 handler 必須使用 async def 定義，才能正確運作於 asyncio 與 gRPC 環境。

### 3. 錯誤處理

建議回傳 `error=ErrorDetail(...)`，並於 gRPC wrapper 層自動轉換為 protobuf error 欄位。

### 4. 性能優化

- 利用 async/await 實現高併發
- 輸出流式回應時可逐步 yield，減少延遲

### 5. 測試覆蓋

- 單機與 gRPC 皆應測試
- 驗證不支援 handler 會丟出 NotImplementedError

## 常見問題

### Q1: 可以實作 input_streaming 或 bidi_streaming 嗎？
A: TranslateBrick 僅允許 unary/output_streaming/get_service_info，其他 handler 會丟出 NotImplementedError。

### Q2: 如何自訂錯誤訊息？
A: 回傳 TranslateResponse 時，填入 error 欄位即可，gRPC wrapper 會自動轉換。

### Q3: 如何切換本地與 gRPC？
A: 只需改變建構方式（new or toGrpcClient），API 完全一致。

## 測試建議

- 參考 `tests/unit/test_translate_brick_standalone.py`、`tests/e2e/test_translate_grpc.py`
- 覆蓋：
  - run_unary、run_output_streaming、run_get_service_info
  - 不支援 handler 的異常
  - 錯誤回傳情境
- 建議使用 pytest + pytest-asyncio

---

TranslateBrick 提供直覺、統一、可擴展的翻譯服務開發體驗，適合本地與分散式部署，並易於測試與維護。