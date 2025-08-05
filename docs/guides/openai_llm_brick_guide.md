# OpenAI GPT Brick 使用指南

## 目錄
- [概述](#概述)
- [安裝與配置](#安裝與配置)
- [快速開始](#快速開始)
- [API 說明](#api-說明)
- [最佳實踐](#最佳實踐)
- [錯誤處理](#錯誤處理)
- [常見問題](#常見問題)

---

## 概述

OpenAI GPT Brick 是基於 LLMBrick 框架實現的 OpenAI GPT 整合元件，支援 GPT-3.5、GPT-4 等模型，並提供單次請求與串流輸出功能。其設計遵循 LLMBrick 的統一接口，支援本地與 gRPC 遠端調用。

---

## 安裝與配置

### 環境變數設置

```bash
# .env file
OPENAI_API_KEY=your_api_key_here
```

### 依賴安裝

```bash
pip install openai  # OpenAI Python client
```

---

## 快速開始

### 基本使用範例

```python
import asyncio
from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, Context

async def main():
    # 創建 OpenAI GPT Brick 實例
    brick = OpenAIGPTBrick(
        default_prompt="",
        model_id="gpt-3.5-turbo"  # 可選: gpt-4
    )
    
    # 準備請求
    request = LLMRequest(
        prompt="Tell me a joke",
        temperature=0.7,
        max_tokens=100,
        context=[]  # 可選: 添加對話上下文
    )
    
    # 執行請求
    response = await brick.run_unary(request)
    print(response.text)

asyncio.run(main())
```

### 串流輸出範例

```python
async def stream_example():
    brick = OpenAIGPTBrick(model_id="gpt-3.5-turbo")
    request = LLMRequest(prompt="Write a story")
    
    async for chunk in brick.run_output_streaming(request):
        if not chunk.is_final:
            print(chunk.text, end="", flush=True)

asyncio.run(stream_example())
```

### SSE Server 整合範例

更完整的整合範例，包含 SSE 服務器和測試頁面：

```python
from llmbrick.servers.sse.server import SSEServer
from llmbrick.servers.sse.config import SSEServerConfig
from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.protocols.models.http.conversation import ConversationSSERequest, ConversationSSEResponse

# 創建 SSE 服務器
config = SSEServerConfig(
    host="127.0.0.1",
    port=8000,
    debug_mode=True,
    allowed_models=["gpt-4o", "gpt-3.5-turbo"],
    enable_test_page=True  # 啟用測試頁面
)

server = SSEServer(config=config)
llm = OpenAIGPTBrick(model_id="gpt-4o")

# 處理聊天請求
@server.handler
async def handle_chat(request: ConversationSSERequest):
    # 首先發送開始事件
    yield ConversationSSEResponse(
        id="start",
        type="start",
        progress="IN_PROGRESS"
    )
    
    # 準備 LLM 請求並串流回應
    llm_request = LLMRequest(
        model_id=request.model,
        prompt=request.messages[-1].content,
        context=[Context(role=msg.role, content=msg.content)
                for msg in request.messages[:-1]]
    )
    
    try:
        async for chunk in llm.run_output_streaming(llm_request):
            if chunk.text:
                yield ConversationSSEResponse(
                    id=f"chunk-{time.time()}",
                    type="text",
                    text=chunk.text,
                    progress="IN_PROGRESS"
                )
    except Exception as e:
        yield ConversationSSEResponse(
            id="error",
            type="error",
            text=str(e),
            progress="DONE"
        )
    
    # 發送完成事件
    yield ConversationSSEResponse(
        id="done",
        type="done",
        progress="DONE"
    )

# 啟動服務器
server.run()
```

完整的實作範例可以在 [`openai_chatbot/openai_chatbot.py`](https://github.com/JiHungLin/llmbrick/tree/main/examples/openai_chatbot/openai_chatbot.py) 中找到，包含：
- SSE 服務器整合
- 自動語言偵測
- 串流與累積回應顯示
- 錯誤處理
- 測試頁面

訪問 http://127.0.0.1:8000/ 可以使用內建的測試頁面：
- 支援串流輸出顯示
- 即時累積回應
- 自動偵測系統語言
- 深色/淺色主題
```

---

## API 說明

### 建構子參數

- `default_prompt (str)`: 預設提示詞
- `model_id (str)`: OpenAI 模型 ID，支援 "gpt-3.5-turbo"、"gpt-4" 和 "gpt-4o"
- `api_key (Optional[str])`: OpenAI API 金鑰，若未提供則從環境變數讀取

### 支援的模型

- `gpt-3.5-turbo`: 預設模型，適合一般對話與任務
- `gpt-4`: 進階模型，適合複雜任務與推理
- `gpt-4o`: 進階模型的最新優化版本

### 請求參數說明

使用 `LLMRequest` 類型，重要欄位包括：
- `prompt (str)`: 主要提示詞
- `context (List[Context])`: 對話歷史上下文
- `temperature (float)`: 生成隨機性，預設 0.7
- `max_tokens (int)`: 最大生成長度

---

## 最佳實踐

1. **API 金鑰管理**
   - 使用環境變數管理 API 金鑰
   - 避免在程式碼中硬編碼金鑰

2. **錯誤處理**
   - 妥善處理 API 限流與錯誤
   - 使用 try-except 捕捉可能的異常

3. **資源管理**
   - 及時關閉不需要的連接
   - 使用串流模式處理長回應

4. **性能優化**
   - 適當設置 max_tokens 避免過度生成
   - 根據需求選擇適當的模型

---

## 錯誤處理

常見錯誤碼與處理方式：
- `ValueError`: API 金鑰未設置
- `ErrorDetail(code=1)`: API 調用失敗
- `ErrorDetail(code=ErrorCodes.SUCCESS)`: 成功

---

## 常見問題

### Q1: 如何切換不同的 GPT 模型？
A: 在建構時指定 model_id 參數，或在請求時設置 model_id。

### Q2: API 金鑰未設置怎麼辦？
A: 確認環境變數 OPENAI_API_KEY 已正確設置，或在建構時提供 api_key 參數。

### Q3: 如何處理 API 限流？
A: 實作重試機制，或使用框架的錯誤處理機制。

### Q4: 串流輸出斷開如何處理？
A: 檢查每個響應塊的 error 欄位，實作重連邏輯。