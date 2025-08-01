# LLMBrick

一個強調「模組化設計」、「明確協定定義」、「靈活組裝」與「易於擴展」的 LLM 應用開發框架。
核心理念為：所有功能皆以 Brick 組件為單元，協定明確、組裝彈性，方便擴充與客製化。

## 特色

- 🧱 **模組化設計**：所有功能皆以 Brick 為單元，組件可插拔、可重組，支援多層次組裝。
- 📑 **明確協定定義**：所有 Brick 之間的資料流、型別、錯誤皆有明確協定（protocols/ 目錄），便於跨語言、跨協議整合。
- 🔄 **多協議支援**：SSE、gRPC（WebSocket/WebRTC 計畫中），可依需求切換。
- 🤖 **多 LLM 支援**：OpenAI、Anthropic、本地模型等，輕鬆擴充。
- 📚 **RAG 支援**：檢索增強生成介面（目前僅有協定，尚無完整實例）。
- 🔧 **易於擴展**：插件系統與自定義組件，支援靈活擴充與客製化。

### 設計理念

- **模組化**：每個 Brick 可獨立開發、測試、組裝，降低耦合。
- **協定導向**：所有資料流、型別、錯誤皆有明確協定，便於跨語言、跨協議整合。
- **靈活組裝**：Pipeline、Server、Client 皆可自由組合各種 Brick，支援多種應用場景。
- **易於擴展**：可自訂新 Brick、協定或插件，快速擴充功能。

## 快速開始

### 安裝

```bash
pip install llmbrick
```

### 基本使用

```python
from llmbrick import OpenAILLM
from llmbrick.servers.sse import SSEServer

# 建立 LLM Brick
llm_brick = OpenAILLM(api_key="your-api-key")

# 啟動 SSE 服務
server = SSEServer(llm_brick)
server.run(host="0.0.0.0", port=8000)
```

## 範例

#### 1. CommonBrick 標準用法

```python
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ErrorDetail, ServiceInfoResponse

class SimpleBrick(CommonBrick):
    @unary_handler
    async def process(self, request: CommonRequest) -> CommonResponse:
        return CommonResponse(
            data={"message": f"Hello, {request.data.get('name', 'World')}!"},
            error=ErrorDetail(code=0, message="Success")
        )

    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success")
        )
```

#### 2. LLMBrick 標準用法

```python
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse, Context
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse

class SimpleLLMBrick(LLMBrick):
    @unary_handler
    async def echo(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text=f"Echo: {request.prompt}",
            tokens=["echo"],
            is_final=True,
            error=ErrorDetail(code=0, message="Success"),
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleLLMBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success"),
        )
```

#### 3. ComposeBrick 標準用法

```python
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse

class SimpleCompose(ComposeBrick):
    @unary_handler
    async def process(self, request: ComposeRequest) -> ComposeResponse:
        return ComposeResponse(
            output={"message": f"文件數量: {len(request.input_documents)}"},
            error=ErrorDetail(code=0, message="Success")
        )

    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleCompose",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success")
        )
```

#### 4. GuardBrick 標準用法

```python
from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse, GuardResult
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse

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
            error=ErrorDetail(code=0, message="Success")
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleGuard",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success")
        )
```

#### 5. IntentionBrick 標準用法

```python
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest, IntentionResponse, IntentionResult
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse

class SimpleIntentionBrick(IntentionBrick):
    @unary_handler
    async def process(self, request: IntentionRequest) -> IntentionResponse:
        return IntentionResponse(
            results=[IntentionResult(intent_category="greet", confidence=1.0)],
            error=ErrorDetail(code=0, message="Success")
        )

    @get_service_info_handler
    async def get_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleIntentionBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success")
        )
```

#### 6. RectifyBrick 標準用法

```python
from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest, RectifyResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse

class SimpleRectifyBrick(RectifyBrick):
    @unary_handler
    async def rectify_handler(self, request: RectifyRequest) -> RectifyResponse:
        return RectifyResponse(
            corrected_text=request.text.upper(),
            error=ErrorDetail(code=0, message="Success")
        )

    @get_service_info_handler
    async def service_info_handler(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleRectifyBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success")
        )
```

#### 7. RetrievalBrick 標準用法

```python
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse

class SimpleRetrievalBrick(RetrievalBrick):
    @unary_handler
    async def search(self, request: RetrievalRequest) -> RetrievalResponse:
        return RetrievalResponse(
            documents=[],
            error=ErrorDetail(code=0, message="Success")
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleRetrievalBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success")
        )
```

#### 8. TranslateBrick 標準用法

```python
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.core.brick import unary_handler, output_streaming_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.translate_types import TranslateRequest, TranslateResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse

class SimpleTranslator(TranslateBrick):
    @unary_handler
    async def echo_translate(self, request: TranslateRequest) -> TranslateResponse:
        return TranslateResponse(
            text=f"{request.text} (to {request.target_language})",
            tokens=[1, 2, 3],
            language_code=request.target_language,
            is_final=True,
            error=ErrorDetail(code=0, message="Success"),
        )

    @get_service_info_handler
    async def service_info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleTranslator",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=0, message="Success"),
        )
```

#### 9. gRPC 服務端與客戶端範例

```python
# 服務端
from llmbrick.servers.grpc.server import GrpcServer
import asyncio

async def start_grpc_server():
    from llmbrick.bricks.llm.base_llm import LLMBrick
    brick = LLMBrick(default_prompt="你好")
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

asyncio.run(start_grpc_server())

# 客戶端
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest
import asyncio

async def use_grpc_client():
    client_brick = LLMBrick.toGrpcClient(remote_address="127.0.0.1:50051")
    req = LLMRequest(prompt="Test", context=[])
    resp = await client_brick.run_unary(req)
    print(resp.text)
    await client_brick._grpc_channel.close()

asyncio.run(use_grpc_client())
```

#### 10. SSE Server 標準用法

```python
from llmbrick.servers.sse.server import SSEServer
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse

server = SSEServer()

@server.handler
async def my_handler(request_data):
    # 回傳多個事件
    yield ConversationSSEResponse(
        id="msg-1",
        type="text",
        text="Hello World",
        progress="IN_PROGRESS"
    )
    yield ConversationSSEResponse(
        id="msg-2",
        type="done",
        progress="DONE"
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
```

## 文檔

- [快速開始](docs/quickstart.md)
- [API 參考](docs/api_reference/)
- [教學範例](docs/tutorials/)

## 授權

MIT License
## Metrics Utilities

The `llmbrick.utils.metrics` module provides decorators for monitoring function performance and resource usage. All decorators support both sync and async functions.

### Available Decorators

- **@measure_time**  
  Logs the execution time of the decorated function.

- **@measure_memory**  
  Logs the difference in process memory usage (RSS, MB) before and after the function runs. Requires `psutil`.

- **@measure_peak_memory**  
  Logs the peak memory usage (MB) during function execution using `tracemalloc`.

### Usage Example

```python
from llmbrick.utils.metrics import measure_time, measure_memory, measure_peak_memory

@measure_time
def sync_func(x):
    return x * 2

@measure_memory
async def async_func(x):
    a = [0] * 10000
    return x + 1

@measure_peak_memory
def another_sync_func(x):
    a = [0] * 10000
    return x - 1
```

All decorators will log performance metrics using the standard logging module.  
For async functions, simply decorate as usual.