# LLMBrick

一個模組化的 LLM 應用開發框架，支援多種通信協議和可插拔的組件架構。

## 特色

- 🧱 **模組化設計**: 基於 Brick 組件的可插拔架構
- 🔄 **多協議支援**: SSE、WebSocket、WebRTC、gRPC
- 🤖 **多 LLM 支援**: OpenAI、Anthropic、本地模型
- 🎤 **語音處理**: ASR 語音識別整合
- 📚 **RAG 支援**: 內建檢索增強生成
- 🔧 **易於擴展**: 插件系統和自定義組件

## 快速開始

### 安裝

```bash
pip install llmbrick
```

### 基本使用

```python
from llmbrick import Pipeline, OpenAILLM
from llmbrick.servers.sse import SSEServer

# 建立 Pipeline
pipeline = Pipeline()
pipeline.add_brick(OpenAILLM(api_key="your-api-key"))

# 啟動 SSE 服務
server = SSEServer(pipeline)
server.run(host="0.0.0.0", port=8000)
```

## 範例

#### 運作單元 Brick (使用內建Brick，Decorator直接替換自己的func)

```python
from llmbrick.core.brick import BaseBrick
import nest_asyncio

class LLMBrick(BaseBrick[str, str]):
    pass


llm = LLMBrick()

@llm.unary()
async def input(prompt: str) -> str:
    return f"user input: {prompt}"

result = await llm.run_unary("What is your name?") #直接調用就本機運算
```

#### 運作單元 Brick (繼承Brick，客製自己需要的Brick)

```python
from llmbrick.core.brick import BaseBrick, unary_handler
import nest_asyncio


class MyNewBrick(BaseBrick[str, str]):
    def __init__(self, some_param: str, **kwargs):
        super().__init__(**kwargs)
        self.some_param = some_param
    
    @unary_handler
    async def process(self, input_data: str) -> str:
        return f"Processed: {input_data} with param {self.some_param}"
    
nest_asyncio.apply()

brick = MyNewBrick(some_param="example")

result = await brick.run_unary("What is your name? ") #直接調用就本機運算
```

#### Brick轉換為異步 gRPC Server

```python
import asyncio
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.bricks.llm.base_llm import LLMBrick

async def main():
    # 建立 LLM Brick
    brick = LLMBrick(default_prompt="你是一個有用的助手")
    
    # 建立異步 gRPC 伺服器
    server = GrpcServer(port=50051)
    server.register_service(brick)
    
    # 啟動異步伺服器
    await server.start()

# 運行伺服器
asyncio.run(main())
```

#### Brick轉換為異步 gRPC Client

```python
import asyncio
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest

async def main():
    # 建立異步 gRPC 客戶端
    brick = LLMBrick.toGrpcClient(remote_address="127.0.0.1:50051")
    
    # 單次請求 - 跟本機調用的寫法一樣
    request = LLMRequest(prompt="What is your name?")
    result = await brick.run_unary(request)
    print(result)
    
    # 流式請求
    async for chunk in brick.run_output_streaming(request):
        print(chunk)
    
    # 清理資源
    await brick._grpc_channel.close()

# 運行客戶端
asyncio.run(main())
```

#### 建立SSE接口

```python
from llmbrick.servers.sse.server import SSEServer
import asyncio

server = SSEServer() 
# 會自動建立SSE的Router

fast_app = server.fastapi_app # 這等同FastAPI的app
# 等價 app = FastAPI()

@server.handler # 使用Decorator自訂需要的邏輯，這邊就是整合所有LLM Brick的區塊
async def simple_flow(request_body):
    # 模擬訊息處理與回應
    yield {"id": "1", "type": "text", "text": "Hello, this is a streaming response.", "progress": "IN_PROGRESS"}
    await asyncio.sleep(0.5)
    yield {"id": "1", "type": "done", "progress": "DONE"}

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
```

#### 建立SSE接口，搭配Brick

```python
from llmbrick.servers.sse.server import SSEServer
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.bricks.intention.base_intention import IntentionBrick
import asyncio

server = SSEServer() 
# 會自動建立SSE的Router

fast_app = server.fastapi_app # 這等同FastAPI的app
# 等價 app = FastAPI()

intention_brick = IntentionBrick()
llm_brick = LLMBrick.toGrpcClient(remote_address="192.168.1.100:50051")

@server.handler #使用Decorator自訂需要的邏輯，這邊就是整合所有LLM Brick的區塊
async def simple_flow(request_body):
    # 模擬訊息處理與回應
    text = request_body.text;
    
    intention_list = await intention_brick.run_unary(text)
    
    ... # 自訂細節

    input_data = {
        "intention_list": intention_list,
        "model_id": request_body.modelId,
        "max_tokens": request_body.maxTokens,
        "context": [...]
    }
    try:
        for i in llm_brick.run_output_stream(input_data):
            output = {"event": "message", "data": i.text}
            yield output
    except:
        yield {"event": "done"}
    
    yield {"event": "done"}
        

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
```

## 文檔

- [快速開始](docs/quickstart.md)
- [API 參考](docs/api_reference/)
- [教學範例](docs/tutorials/)

## 授權

MIT License