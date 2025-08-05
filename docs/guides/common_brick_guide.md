# CommonBrick 使用指南

## 目錄
- [概述](#概述)
- [架構設計](#架構設計)
- [快速開始](#快速開始)
- [單機版使用](#單機版使用)
- [gRPC版使用](#grpc版使用)
- [最佳實踐](#最佳實踐)
- [錯誤處理](#錯誤處理)
- [性能考慮](#性能考慮)
- [常見問題](#常見問題)

## 概述

CommonBrick 是 LLMBrick 框架中的核心組件，提供統一的異步處理介面，支援本地調用和遠程 gRPC 調用的無縫切換。它實現了四種不同的處理模式：

- **Unary**: 單次請求-回應
- **Output Streaming**: 單次請求-流式回應  
- **Input Streaming**: 流式請求-單次回應
- **Bidirectional Streaming**: 雙向流式處理

## 架構設計

### 設計模式

1. **裝飾器模式**: 使用 `@unary_handler`, `@output_streaming_handler` 等裝飾器註冊處理函數
2. **適配器模式**: `CommonGrpcWrapper` 提供 gRPC 和本地調用之間的適配
3. **工廠模式**: `toGrpcClient()` 動態創建 gRPC 客戶端
4. **策略模式**: 支援多種調用策略（本地/遠程）

### 核心組件

```
CommonBrick (核心類)
├── BaseBrick (基礎類)
├── CommonGrpcWrapper (gRPC 包裝器)
├── CommonRequest/CommonResponse (數據模型)
└── 處理器裝飾器 (@unary_handler, @output_streaming_handler, etc.)
```

## 快速開始

### 基本安裝

```python
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.common_types import (
    CommonRequest, CommonResponse, ErrorDetail, ServiceInfoResponse
)
```

### 最簡單的 Brick 實現

```python
class SimpleBrick(CommonBrick):
    @unary_handler
    async def process(self, request: CommonRequest) -> CommonResponse:
        return CommonResponse(
            data={"message": f"Hello, {request.data.get('name', 'World')}!"},
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
    
    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

## 單機版使用

### 1. 創建和使用 Brick

```python
import asyncio
from llmbrick.protocols.models.bricks.common_types import CommonRequest

async def main():
    # 創建 Brick 實例
    brick = SimpleBrick(verbose=False)
    
    # 發送請求
    request = CommonRequest(data={"name": "Alice"})
    response = await brick.run_unary(request)
    
    print(f"Response: {response.data['message']}")
    # 輸出: Response: Hello, Alice!

# 運行
asyncio.run(main())
```

### 2. 實現所有處理模式

```python
from typing import AsyncIterator
from llmbrick.core.brick import (
    unary_handler, output_streaming_handler, 
    input_streaming_handler, bidi_streaming_handler
)

class FullFeatureBrick(CommonBrick):
    @unary_handler
    async def unary_process(self, request: CommonRequest) -> CommonResponse:
        """單次處理"""
        result = request.data.get("value", 0) * 2
        return CommonResponse(
            data={"result": result},
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
    
    @output_streaming_handler
    async def stream_output(self, request: CommonRequest) -> AsyncIterator[CommonResponse]:
        """流式輸出"""
        count = request.data.get("count", 5)
        for i in range(count):
            await asyncio.sleep(0.1)
            yield CommonResponse(
                data={"index": i, "value": i * i},
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
    
    @input_streaming_handler
    async def stream_input(self, request_stream: AsyncIterator[CommonRequest]) -> CommonResponse:
        """流式輸入處理"""
        total = 0
        count = 0
        async for req in request_stream:
            total += req.data.get("value", 0)
            count += 1
        
        return CommonResponse(
            data={"sum": total, "count": count, "average": total/count if count > 0 else 0},
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
    
    @bidi_streaming_handler
    async def bidi_process(self, request_stream: AsyncIterator[CommonRequest]) -> AsyncIterator[CommonResponse]:
        """雙向流處理"""
        async for req in request_stream:
            value = req.data.get("value", 0)
            yield CommonResponse(
                data={"original": value, "doubled": value * 2},
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
```

### 3. 使用範例

```python
async def demonstrate_all_modes():
    brick = FullFeatureBrick(verbose=False)
    
    # 1. Unary 調用
    response = await brick.run_unary(CommonRequest(data={"value": 10}))
    print(f"Unary result: {response.data['result']}")  # 20
    
    # 2. Output Streaming
    async for response in brick.run_output_streaming(CommonRequest(data={"count": 3})):
        print(f"Stream output: {response.data}")
    
    # 3. Input Streaming
    async def input_generator():
        for i in [1, 2, 3, 4, 5]:
            yield CommonRequest(data={"value": i})
    
    result = await brick.run_input_streaming(input_generator())
    print(f"Input stream result: {result.data}")  # {"sum": 15, "count": 5, "average": 3.0}
    
    # 4. Bidirectional Streaming
    async def bidi_generator():
        for i in [10, 20, 30]:
            yield CommonRequest(data={"value": i})
    
    async for response in brick.run_bidi_streaming(bidi_generator()):
        print(f"Bidi result: {response.data}")
```

## gRPC版使用

### 1. 服務端設置

```python
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

async def start_grpc_server():
    # 創建服務
    brick = FullFeatureBrick(verbose=True)
    
    # 創建 gRPC 服務器
    server = GrpcServer(port=50051)
    server.register_service(brick)
    
    # 啟動服務器
    await server.start()

# 運行服務器
asyncio.run(start_grpc_server())
```

### 2. 客戶端使用

```python
async def use_grpc_client():
    # 創建 gRPC 客戶端
    client_brick = FullFeatureBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        verbose=False
    )
    
    try:
        # 使用與本地相同的 API
        response = await client_brick.run_unary(
            CommonRequest(data={"value": 25})
        )
        print(f"gRPC result: {response.data['result']}")  # 50
        
        # 流式調用也完全相同
        async for response in client_brick.run_output_streaming(
            CommonRequest(data={"count": 3})
        ):
            print(f"gRPC stream: {response.data}")

asyncio.run(use_grpc_client())
```

### 3. 無縫切換示例

切換機制是透過 `toGrpcClient()` 類方法實現的，它會創建一個新的 Brick 實例，該實例的處理器會自動路由到遠程 gRPC 服務：

```python
# 本地使用 - 直接創建實例
local_brick = FullFeatureBrick(verbose=False)

# 遠程使用 - 使用 toGrpcClient 創建 gRPC 客戶端
remote_brick = FullFeatureBrick.toGrpcClient("127.0.0.1:50051", verbose=False)

# API 完全相同，無論本地還是遠程
async def process_data(brick, data):
    request = CommonRequest(data=data)
    return await brick.run_unary(request)

# 使用方式完全相同
result1 = await process_data(local_brick, {"value": 10})
result2 = await process_data(remote_brick, {"value": 10})

```

這種設計讓開發人員可以在不修改業務邏輯代碼的情況下，輕鬆在本地和分散式部署之間切換。所有的 Brick 類型（CommonBrick、LLMBrick、GuardBrick 等）都遵循相同的模式，都有自己的 `toGrpcClient()` 實現。

## 最佳實踐

### 1. 異步函數設計

```python
class BestPracticeBrick(CommonBrick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}
        self.request_count = 0
    
    @unary_handler
    async def optimized_handler(self, request: CommonRequest) -> CommonResponse:
        """最佳實踐的處理器實現"""
        
        # 1. 輸入驗證
        if not request.data:
            return CommonResponse(
                data={},
                error=ErrorDetail(code=400, message="Empty request data")
            )
        
        # 2. 業務邏輯處理
        try:
            # 使用緩存提升性能
            cache_key = str(sorted(request.data.items()))
            if cache_key in self.cache:
                result = self.cache[cache_key]
            else:
                result = await self._process_business_logic(request.data)
                self.cache[cache_key] = result
            
            # 3. 狀態更新
            self.request_count += 1
            
            # 4. 返回結果
            return CommonResponse(
                data={
                    "result": result,
                    "processed_at": asyncio.get_event_loop().time(),
                    "request_id": self.request_count
                },
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
            
        except Exception as e:
            # 5. 錯誤處理
            return CommonResponse(
                data={},
                error=ErrorDetail(
                    code=500, 
                    message="Processing failed", 
                    detail=str(e)
                )
            )
    
    async def _process_business_logic(self, data):
        """分離業務邏輯"""
        await asyncio.sleep(0.01)  # 模擬異步操作
        return sum(data.values()) if all(isinstance(v, (int, float)) for v in data.values()) else 0
```

### 2. 錯誤處理策略

```python
class RobustBrick(CommonBrick):
    @unary_handler
    async def robust_handler(self, request: CommonRequest) -> CommonResponse:
        try:
            # 業務邏輯
            result = await self._risky_operation(request.data)
            
            return CommonResponse(
                data={"result": result},
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
            
        except ValueError as e:
            # 客戶端錯誤
            return CommonResponse(
                data={},
                error=ErrorDetail(code=400, message=f"Invalid input: {e}")
            )
        except TimeoutError:
            # 超時錯誤
            return CommonResponse(
                data={},
                error=ErrorDetail(code=408, message="Request timeout")
            )
        except Exception as e:
            # 服務器錯誤
            return CommonResponse(
                data={},
                error=ErrorDetail(code=500, message="Internal server error", detail=str(e))
            )
    
    async def _risky_operation(self, data):
        # 可能拋出異常的操作
        if not data:
            raise ValueError("Data cannot be empty")
        
        # 模擬可能超時的操作
        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
        return "processed"
```

### 3. 性能優化

```python
class PerformantBrick(CommonBrick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connection_pool = None  # 假設有連接池
        self.semaphore = asyncio.Semaphore(10)  # 限制並發
    
    @unary_handler
    async def high_performance_handler(self, request: CommonRequest) -> CommonResponse:
        # 使用信號量限制並發
        async with self.semaphore:
            # 並行處理多個任務
            tasks = [
                self._task_1(request.data),
                self._task_2(request.data),
                self._task_3(request.data)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 處理結果
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(f"Task {i+1} failed: {result}")
                else:
                    processed_results.append(result)
            
            return CommonResponse(
                data={"results": processed_results},
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
    
    async def _task_1(self, data):
        await asyncio.sleep(0.01)
        return f"Task 1 result: {len(data)}"
    
    async def _task_2(self, data):
        await asyncio.sleep(0.02)
        return f"Task 2 result: {sum(v for v in data.values() if isinstance(v, (int, float)))}"
    
    async def _task_3(self, data):
        await asyncio.sleep(0.01)
        return f"Task 3 result: {list(data.keys())}"
```

## 錯誤處理

### 使用框架提供的ErrorCodes工具類

框架提供了完整的`ErrorCodes`工具類，包含常用的HTTP狀態碼和業務錯誤代碼：

```python
from llmbrick.core.error_codes import ErrorCodes, ErrorCodeUtils
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse

class StandardErrorBrick(CommonBrick):
    @unary_handler
    async def error_demo_handler(self, request: CommonRequest) -> CommonResponse:
        error_type = request.data.get("error_type")
        
        if error_type == "validation":
            # 使用工廠方法創建驗證錯誤
            return CommonResponse(
                data={},
                error=ErrorCodes.validation_error(
                    "數據驗證失敗",
                    "必需字段 'name' 缺失"
                )
            )
        elif error_type == "not_found":
            # 使用特化的工廠方法
            return CommonResponse(
                data={},
                error=ErrorCodes.not_found(
                    "資源未找到",
                    "用戶 ID 123 不存在"
                )
            )
        elif error_type == "model_error":
            # 針對模型錯誤的專用方法
            return CommonResponse(
                data={},
                error=ErrorCodes.model_not_found(
                    "gpt-4",
                    "指定的模型當前不可用"
                )
            )
        elif error_type == "parameter":
            # 參數相關錯誤
            return CommonResponse(
                data={},
                error=ErrorCodes.parameter_missing(
                    "user_id",
                    "請求中必須包含用戶ID"
                )
            )
        else:
            # 成功響應
            return CommonResponse(
                data={"result": "success"},
                error=None
            )
```

### ErrorCodes類別的主要特點

#### 1. 完整的錯誤代碼體系

```python
# HTTP 標準狀態碼
ErrorCodes.SUCCESS = 200
ErrorCodes.BAD_REQUEST = 400
ErrorCodes.UNAUTHORIZED = 401
ErrorCodes.NOT_FOUND = 404
ErrorCodes.INTERNAL_ERROR = 500

# 框架特定業務錯誤代碼
ErrorCodes.VALIDATION_ERROR = 2000        # 驗證錯誤
ErrorCodes.PARAMETER_MISSING = 2002       # 參數缺失
ErrorCodes.MODEL_ERROR = 4000             # 模型錯誤
ErrorCodes.MODEL_NOT_FOUND = 4001         # 模型未找到
ErrorCodes.EXTERNAL_SERVICE_ERROR = 5000  # 外部服務錯誤
ErrorCodes.RESOURCE_NOT_FOUND = 6001      # 資源未找到
```

#### 2. 便利的工廠方法

```python
# 基本工廠方法
error = ErrorCodes.create_error(
    ErrorCodes.BAD_REQUEST,
    "自定義錯誤訊息",
    "詳細錯誤信息"
)

# 常用錯誤的快捷方法
bad_request = ErrorCodes.bad_request("請求格式錯誤")
not_found = ErrorCodes.not_found("資源不存在")
internal_error = ErrorCodes.internal_error("系統錯誤")

# 特化的錯誤方法
model_error = ErrorCodes.model_not_found("gpt-4", "模型服務不可用")
param_error = ErrorCodes.parameter_missing("user_id")
external_error = ErrorCodes.external_service_error("OpenAI API")
```

#### 3. 錯誤分類工具

```python
from llmbrick.core.error_codes import ErrorCodeUtils

# 檢查錯誤類型
is_success = ErrorCodeUtils.is_success(200)          # True
is_client_error = ErrorCodeUtils.is_client_error(400)  # True
is_server_error = ErrorCodeUtils.is_server_error(500)  # True

# 獲取錯誤分類
category = ErrorCodeUtils.get_error_category(2000)  # "驗證錯誤"
category = ErrorCodeUtils.get_error_category(4001)  # "模型錯誤"
```

### 實際使用範例

```python
class PracticalErrorBrick(CommonBrick):
    @unary_handler
    async def comprehensive_handler(self, request: CommonRequest) -> CommonResponse:
        try:
            # 輸入驗證
            if not request.data.get("input"):
                return CommonResponse(
                    data={},
                    error=ErrorCodes.parameter_missing("input", "處理數據不能為空")
                )
            
            # 業務邏輯處理
            result = await self._process_data(request.data)
            
            return CommonResponse(
                data={"result": result},
                error=None
            )
            
        except ValueError as e:
            # 參數錯誤
            return CommonResponse(
                data={},
                error=ErrorCodes.parameter_invalid("input", str(e))
            )
        except TimeoutError:
            # 超時錯誤
            return CommonResponse(
                data={},
                error=ErrorCodes.create_error(
                    ErrorCodes.REQUEST_TIMEOUT,
                    "處理超時",
                    "請求處理時間超過限制"
                )
            )
        except Exception as e:
            # 系統錯誤
            return CommonResponse(
                data={},
                error=ErrorCodes.internal_error("系統處理錯誤", str(e))
            )
    
    async def _process_data(self, data):
        # 模擬業務處理
        if data.get("input") == "invalid":
            raise ValueError("不支援的輸入值")
        return f"處理結果: {data.get('input')}"
```

## 性能考慮

### 1. 並發處理

```python
import asyncio
from asyncio import Semaphore

class ConcurrentBrick(CommonBrick):
    def __init__(self, max_concurrent=100, **kwargs):
        super().__init__(**kwargs)
        self.semaphore = Semaphore(max_concurrent)
    
    @output_streaming_handler
    async def concurrent_stream(self, request: CommonRequest) -> AsyncIterator[CommonResponse]:
        items = request.data.get("items", [])
        
        async def process_item(item):
            async with self.semaphore:
                await asyncio.sleep(0.1)  # 模擬處理時間
                return {"item": item, "processed": True}
        
        # 並發處理所有項目
        tasks = [process_item(item) for item in items]
        
        # 使用 as_completed 來流式返回結果
        for coro in asyncio.as_completed(tasks):
            result = await coro
            yield CommonResponse(
                data=result,
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
```

### 2. 內存管理

```python
class MemoryEfficientBrick(CommonBrick):
    @input_streaming_handler
    async def memory_efficient_handler(self, request_stream: AsyncIterator[CommonRequest]) -> CommonResponse:
        # 使用生成器避免將所有數據加載到內存
        total = 0
        count = 0
        
        # 分批處理以控制內存使用
        batch_size = 100
        batch = []
        
        async for request in request_stream:
            batch.append(request.data.get("value", 0))
            
            if len(batch) >= batch_size:
                # 處理批次
                batch_sum = sum(batch)
                total += batch_sum
                count += len(batch)
                batch.clear()  # 清理內存
        
        # 處理剩餘的數據
        if batch:
            total += sum(batch)
            count += len(batch)
        
        return CommonResponse(
            data={"total": total, "count": count, "average": total/count if count > 0 else 0},
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

## 常見問題

### Q1: 如何處理長時間運行的任務？

```python
class LongRunningBrick(CommonBrick):
    @output_streaming_handler
    async def long_task(self, request: CommonRequest) -> AsyncIterator[CommonResponse]:
        total_steps = request.data.get("steps", 100)
        
        for step in range(total_steps):
            # 執行步驟
            await asyncio.sleep(0.1)
            
            # 定期報告進度
            progress = (step + 1) / total_steps * 100
            yield CommonResponse(
                data={
                    "step": step + 1,
                    "total_steps": total_steps,
                    "progress": f"{progress:.1f}%",
                    "completed": step + 1 == total_steps
                },
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
```

### Q2: 如何實現超時控制？

```python
class TimeoutBrick(CommonBrick):
    @unary_handler
    async def timeout_handler(self, request: CommonRequest) -> CommonResponse:
        timeout = request.data.get("timeout", 5.0)
        
        try:
            # 使用 asyncio.wait_for 實現超時控制
            result = await asyncio.wait_for(
                self._slow_operation(request.data),
                timeout=timeout
            )
            
            return CommonResponse(
                data={"result": result},
                error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
            )
            
        except asyncio.TimeoutError:
            return CommonResponse(
                data={},
                error=ErrorDetail(
                    code=408,
                    message="Request timeout",
                    detail=f"Operation exceeded {timeout} seconds"
                )
            )
    
    async def _slow_operation(self, data):
        # 模擬慢操作
        delay = data.get("delay", 1.0)
        await asyncio.sleep(delay)
        return f"Completed after {delay} seconds"
```

### Q3: 如何實現重試機制？

```python
class RetryBrick(CommonBrick):
    @unary_handler
    async def retry_handler(self, request: CommonRequest) -> CommonResponse:
        max_retries = request.data.get("max_retries", 3)
        
        for attempt in range(max_retries + 1):
            try:
                result = await self._unreliable_operation(request.data)
                return CommonResponse(
                    data={"result": result, "attempts": attempt + 1},
                    error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
                )
                
            except Exception as e:
                if attempt == max_retries:
                    # 最後一次嘗試失敗
                    return CommonResponse(
                        data={},
                        error=ErrorDetail(
                            code=500,
                            message="Operation failed after retries",
                            detail=f"Failed after {max_retries + 1} attempts: {e}"
                        )
                    )
                
                # 等待後重試
                await asyncio.sleep(2 ** attempt)  # 指數退避
    
    async def _unreliable_operation(self, data):
        # 模擬不可靠的操作
        import random
        if random.random() < 0.7:  # 70% 失敗率
            raise Exception("Random failure")
        return "Success!"
```

## 總結

CommonBrick 提供了一個強大且靈活的框架來構建異步服務，其主要優點包括：

1. **統一的 API**: 本地和遠程調用使用相同的介面
2. **豐富的處理模式**: 支援四種不同的處理模式
3. **優雅的錯誤處理**: 內建錯誤處理和報告機制
4. **高性能**: 基於 asyncio 的高性能異步處理
5. **易於測試**: 清晰的介面和豐富的測試工具

通過遵循本指南中的最佳實踐，您可以構建出高效、可靠且易於維護的服務。