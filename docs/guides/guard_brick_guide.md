# GuardBrick 使用指南

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

GuardBrick 是 LLMBrick 框架中專為意圖檢查（如安全過濾、攻擊偵測）設計的組件。  
它提供統一的異步介面，支援本地與 gRPC 調用的無縫切換，API 完全一致。  
僅支援兩種 handler：**Unary**（單次請求-回應）與 **GetServiceInfo**（服務資訊查詢），不支援 streaming。

## 架構設計

### 設計模式

1. **裝飾器模式**：使用 `@unary_handler`, `@get_service_info_handler` 註冊處理函數
2. **適配器模式**：`GuardGrpcWrapper` 提供 gRPC 與本地調用的適配
3. **工廠模式**：`toGrpcClient()` 動態創建 gRPC 客戶端
4. **策略模式**：支援本地/遠端多種調用策略

### 核心組件

```
GuardBrick (核心類)
├── BaseBrick (基礎類)
├── GuardGrpcWrapper (gRPC 包裝器)
├── GuardRequest/GuardResponse (數據模型)
└── 處理器裝飾器 (@unary_handler, @get_service_info_handler)
```

## 快速開始

### 基本安裝

```python
from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse, GuardResult
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
```

### 最簡單的 GuardBrick 實現

```python
class SimpleGuard(GuardBrick):
    @unary_handler
    async def check(self, request: GuardRequest) -> GuardResponse:
        is_attack = "attack" in (request.text or "").lower()
        result = GuardResult(
            is_attack=is_attack,
            confidence=0.99 if is_attack else 0.1,
            detail="Detected attack" if is_attack else "Safe"
        )
        return GuardResponse(
            results=[result],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleGuard",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

## 單機版使用

### 1. 創建與使用 GuardBrick

```python
import asyncio
from llmbrick.protocols.models.bricks.guard_types import GuardRequest

async def main():
    brick = SimpleGuard(verbose=False)
    request = GuardRequest(text="This is an attack!")
    response = await brick.run_unary(request)
    print(f"Is attack: {response.results[0].is_attack}")  # True

asyncio.run(main())
```

### 2. 服務資訊查詢

```python
info = await brick.run_get_service_info()
print(info.service_name, info.version)
```

## gRPC 版使用

### 1. 服務端設置

```python
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

async def start_grpc_server():
    brick = SimpleGuard(verbose=True)
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

asyncio.run(start_grpc_server())
```

### 2. 客戶端使用

```python
async def use_grpc_client():
    client_brick = SimpleGuard.toGrpcClient(
        remote_address="127.0.0.1:50051",
        verbose=False
    )
    try:
        request = GuardRequest(text="attack detected")
        response = await client_brick.run_unary(request)
        print(f"gRPC result: {response.results[0].is_attack}")  # True

asyncio.run(use_grpc_client())
```

### 3. 無縫切換示例

```python
# 本地
local_brick = SimpleGuard(verbose=False)
# 遠端
remote_brick = SimpleGuard.toGrpcClient("127.0.0.1:50051", verbose=False)

async def check(brick, text):
    req = GuardRequest(text=text)
    return await brick.run_unary(req)

result1 = await check(local_brick, "attack")
result2 = await check(remote_brick, "attack")
```

## 最佳實踐

### 1. 僅支援 async handler

所有 handler 必須為 async function，否則會拋出錯誤。
常見錯誤：
- 忘記加 async，導致 handler 註冊失敗或執行時型別錯誤
- 未 await 非同步操作，導致 coroutine 未執行
- handler 內部呼叫同步阻塞操作，建議全程 async

**範例：正確 async handler**
```python
@unary_handler
async def check(self, request: GuardRequest) -> GuardResponse:
    # ... 非同步邏輯 ...
    return GuardResponse(...)
```

### 2. 錯誤處理建議

- 回傳 ErrorDetail，明確標註錯誤碼與訊息
- 建議捕捉異常並轉為 ErrorDetail 回應，避免未捕捉異常導致 gRPC 斷線
- 可自訂錯誤碼（如 400, 500），並於 detail 補充說明

**範例：健壯的錯誤處理**
```python
@unary_handler
async def robust_handler(self, request: GuardRequest) -> GuardResponse:
    try:
        # 業務邏輯
        ...
        return GuardResponse(
            results=[GuardResult(is_attack=False, confidence=1.0, detail="ok")],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
    except ValueError as e:
        return GuardResponse(
            results=[],
            error=ErrorDetail(code=400, message="Invalid input", detail=str(e))
        )
    except Exception as e:
        return GuardResponse(
            results=[],
            error=ErrorDetail(code=500, message="Internal error", detail=str(e))
        )
```

### 3. API 一致性

- 本地與 gRPC 客戶端 API 完全一致，開發時可先用本地模式測試，再無縫切換到遠端
- 測試時建議同時覆蓋本地與 gRPC 兩種情境

### 4. 測試建議

- 建議參考 `tests/unit/test_guard_brick_standalone.py` 及 `tests/e2e/test_guard_grpc.py` 撰寫單元與端到端測試
- 覆蓋正常、攻擊、錯誤、異常情境
- 可用 pytest.mark.asyncio 進行 async 測試
- 建議測試 handler 註冊、異常拋出、gRPC 連線失敗等情境

### 5. 常見陷阱與解法

- **未註冊 handler**：呼叫未註冊的 handler 會拋出 NotImplementedError，請確認有正確加上裝飾器
- **誤用 streaming handler**：GuardBrick 僅支援 unary/get_service_info，註冊 streaming handler 會直接報錯
- **gRPC 連線問題**：gRPC server 未啟動或 port 錯誤會導致連線失敗，請確認 server 狀態
- **型別錯誤**：handler 回傳型別需正確（GuardResponse），否則 wrapper 會報錯

**建議：**
- 開發時先用本地模式驗證邏輯，再切換 gRPC 測試
- handler 內部盡量捕捉所有異常，避免未處理異常導致服務中斷
- 測試覆蓋所有分支，包含異常與錯誤情境

## 錯誤處理

### 常見錯誤類型

- handler 非 async function
- 調用未註冊的 handler
- streaming handler 會直接拋出 NotImplementedError
- gRPC 連線失敗或伺服器未啟動

### 錯誤處理範例

```python
@unary_handler
async def robust_handler(self, request: GuardRequest) -> GuardResponse:
    try:
        # 業務邏輯
        ...
        return GuardResponse(
            results=[GuardResult(is_attack=False, confidence=1.0, detail="ok")],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
    except Exception as e:
        return GuardResponse(
            results=[],
            error=ErrorDetail(code=500, message="Internal error", detail=str(e))
        )
```

## 常見問題

### Q1: 可以註冊 streaming handler 嗎？
A: GuardBrick 僅支援 unary 與 get_service_info，註冊 streaming handler 會直接拋出 NotImplementedError。

### Q2: 如何切換本地與 gRPC？
A: 只需用 `toGrpcClient()` 創建 client 實例，API 完全一致，無需更改業務邏輯。

### Q3: handler 必須是 async 嗎？
A: 是，所有 handler 必須為 async function，否則會報錯。

### Q4: 如何測試 GuardBrick？
A: 參考 `tests/unit/test_guard_brick_standalone.py` 及 `tests/e2e/test_guard_grpc.py`，可用 pytest 撰寫單元與端到端測試。

---

## 總結

GuardBrick 提供簡潔、直覺的意圖檢查服務，支援本地與 gRPC 無縫切換，API 一致，易於擴展與測試。  
建議開發者遵循 async handler、明確錯誤處理與完整測試的最佳實踐，以確保服務穩定可靠。