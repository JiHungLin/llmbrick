# LLMBrick 使用指南

## 目錄
- [概述](#概述)
- [架構設計](#架構設計)
- [快速開始](#快速開始)
- [單機版使用](#單機版使用)
- [gRPC 版使用](#grpc-版使用)
- [API 與 Handler 說明](#api-與-handler-說明)
- [最佳實踐](#最佳實踐)
- [錯誤處理](#錯誤處理)
- [性能考慮](#性能考慮)
- [常見問題](#常見問題)
- [總結](#總結)

---

## 概述

LLMBrick 是 LLMBrick 框架中專為大型語言模型（LLM）服務設計的核心元件，提供統一的異步處理介面，支援本地調用與遠端 gRPC 調用的無縫切換。
其 API 設計與 CommonBrick 完全一致，讓開發者可專注於業務邏輯，無需關心底層通訊細節。

### 可用的 LLM Brick 實作

- [OpenAI GPT Brick](./openai_llm_brick_guide.md) - 整合 OpenAI GPT-3.5、GPT-4 等模型的 Brick 實作

---

## 架構設計

### 設計模式

1. **裝飾器模式**：使用 `@unary_handler`, `@output_streaming_handler`, `@get_service_info_handler` 註冊處理函數
2. **適配器模式**：`LLMGrpcWrapper` 提供 gRPC 與本地調用之間的適配
3. **工廠模式**：`toGrpcClient()` 動態創建 gRPC 客戶端
4. **策略模式**：支援本地/遠端多種調用策略

### 核心組件

```
LLMBrick (核心類)
├── BaseBrick (基礎類)
├── LLMGrpcWrapper (gRPC 包裝器)
├── LLMRequest/LLMResponse (數據模型)
└── 處理器裝飾器 (@unary_handler, @output_streaming_handler, @get_service_info_handler)
```

---

## 快速開始

### 安裝與引入

```python
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse, Context
from llmbrick.protocols.models.bricks.common_types import ServiceInfoResponse, ErrorDetail
```

---

## 單機版使用

### 1. 創建與使用 LLMBrick

```python
import asyncio
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, Context

class SimpleLLMBrick(LLMBrick):
    def __init__(self, default_prompt="Say hi", **kwargs):
        super().__init__(default_prompt=default_prompt, **kwargs)

    @unary_handler
    async def echo(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text=f"Echo: {request.prompt or self.default_prompt}",
            tokens=["echo"],  # tokens 必須為 List[str]
            is_final=True,
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleLLMBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success"),
        )

async def main():
    brick = SimpleLLMBrick(default_prompt="Hello")
    req = LLMRequest(prompt="Test prompt", context=[])  # context 必須為 List[Context]
    resp = await brick.run_unary(req)
    print(resp.text)  # 輸出: Echo: Test prompt

asyncio.run(main())
```

---

## gRPC 版使用

### 1. 服務端設置

```python
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

class MyLLMBrick(LLMBrick):
    # ... 實作 handler ...

async def start_grpc_server():
    brick = MyLLMBrick(default_prompt="gRPC hi")
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

asyncio.run(start_grpc_server())
```

### 2. 客戶端使用

```python
from llmbrick.protocols.models.bricks.llm_types import LLMRequest

async def use_grpc_client():
    client_brick = MyLLMBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        default_prompt="gRPC hi"
    )
    req = LLMRequest(prompt="gRPC test", context=[])
    resp = await client_brick.run_unary(req)
    print(resp.text)

asyncio.run(use_grpc_client())
```

### 3. 無縫切換示例

```python
# 本地
local_brick = MyLLMBrick(default_prompt="local")
# 遠端
remote_brick = MyLLMBrick.toGrpcClient("127.0.0.1:50051", default_prompt="remote")

async def process(brick, prompt):
    req = LLMRequest(prompt=prompt, context=[])
    return await brick.run_unary(req)

result1 = await process(local_brick, "hi")
result2 = await process(remote_brick, "hi")
```

---

## API 與 Handler 說明

### 支援的 Handler

- `@unary_handler`：單次請求-回應（必須 async）
- `@output_streaming_handler`：單次請求-流式回應（必須 async generator）
- `@get_service_info_handler`：查詢服務資訊（必須 async）

> **注意**：LLMBrick 僅允許上述三種 handler，註冊其他 handler 會 raise NotImplementedError。

### LLMRequest/LLMResponse 型態

- `LLMRequest`
  - `temperature: float`
  - `model_id: str`
  - `prompt: str`
  - `context: List[Context]`  ← 必須為 Context 物件列表
  - `client_id: str`
  - `session_id: str`
  - `request_id: str`
  - `source_language: str`
  - `max_tokens: int`
- `LLMResponse`
  - `text: str`
  - `tokens: List[str]`  ← 必須為字串列表
  - `is_final: bool`
  - `error: Optional[ErrorDetail]`

---

## 最佳實踐

- **所有 handler 必須為 async function**
- 輸入驗證與錯誤處理（回傳 error 欄位）
- 支援多語言與流式回應
- 測試覆蓋 handler 未註冊、型別錯誤、異常情境
- 建議於 handler 內部加上日誌與異常捕捉
- **型態嚴格對齊**：tokens 必須為 List[str]，context 必須為 List[Context]

---

## 錯誤處理

- handler 回傳的 error 欄位應為 ErrorDetail，code=ErrorCodes.SUCCESS 表示成功
- 未註冊 handler 會 raise NotImplementedError
- gRPC 包裝器自動將異常轉為 error 欄位回傳
- 建議使用框架內建 ErrorCodes 工具類

---

## 性能考慮

- 建議所有 handler 為非同步，避免阻塞 event loop
- 可於 output_streaming 實作分批/流式回應
- 如需高併發，建議加上 semaphore 或快取機制

---

## 常見問題

### Q1: handler 必須是 async function 嗎？
A: 是，否則會於 runtime 拋出錯誤。

### Q2: 如何切換本地與 gRPC？
A: 只需分別用建構子或 toGrpcClient 建立實例，API 完全一致。

### Q3: 如何 debug handler 未註冊？
A: 呼叫未註冊的 handler 會拋出 NotImplementedError，請檢查是否有正確加上裝飾器。

### Q4: tokens 或 context 型態錯誤怎麼辦？
A: tokens 必須為 List[str]，context 必須為 List[Context]。常見錯誤如 tokens=0、tokens="abc"、context=None 都會導致型態錯誤，請參考本文件範例。

---

## 總結

LLMBrick 提供統一、直覺、可擴展的 LLM 服務開發框架，支援本地與 gRPC 無縫切換，API 設計友善，易於測試與維護。  
建議開發者參考本指南與測試案例，實踐最佳實踐，打造高效穩定的 LLM 服務。