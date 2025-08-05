# SSE Server 使用指南

## 概述

LLMBrick SSE Server 是一個基於 FastAPI 的 Server-Sent Events (SSE) 服務器，專為大型語言模型對話應用設計。它提供了完整的型態安全、錯誤處理和開發者友善的配置選項。

## 特色功能

- ✅ **完整的型態安全保障** - 嚴格的輸入輸出驗證
- ✅ **業務邏輯驗證** - 可配置的模型清單、訊息長度限制等
- ✅ **結構化錯誤處理** - 詳細的錯誤訊息和異常處理
- ✅ **開發者友善** - 可配置的除錯模式和日誌記錄
- ✅ **向後相容** - 支援現有的初始化方式
- ✅ **易於測試** - 提供測試工具和範例幫助開發者驗證應用

## 快速開始

### 基本使用

```python
from llmbrick.servers.sse.server import SSEServer
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse

# 創建 SSE Server
server = SSEServer()

# 定義處理函數
@server.handler
async def my_handler(request_data):
    # 處理邏輯
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

# 啟動服務器
server.run(host="0.0.0.0", port=8000)
```

### 使用配置類別

```python
from llmbrick.servers.sse.server import SSEServer
from llmbrick.servers.sse.config import SSEServerConfig

# 創建配置
config = SSEServerConfig(
    host="127.0.0.1",
    port=9000,
    debug_mode=True,
    allowed_models=["gpt-4o", "claude-3"],
    max_message_length=5000,
    enable_request_logging=True
)

# 使用配置創建服務器
server = SSEServer(config=config)

@server.handler
async def advanced_handler(request_data):
    # 配置會自動驗證請求
    # 業務邏輯處理...
    pass

server.run()
```

## API 參考

### SSEServerConfig

配置類別提供了豐富的自定義選項：

```python
class SSEServerConfig:
    # 基本配置
    host: str = "0.0.0.0"
    port: int = 8000
    prefix: str = ""
    chat_completions_path: str = "/chat/completions"
    
    # 驗證配置
    allowed_models: List[str] = ["gpt-4o", "gpt-3.5-turbo", "sonar"]
    max_message_length: int = 10000
    max_messages_count: int = 100
    
    # 開發者體驗配置
    debug_mode: bool = False
    enable_request_logging: bool = True
    enable_validation_details: bool = True
    
    # 效能配置
    request_timeout: int = 30
    max_concurrent_connections: int = 100
```

### 請求格式

SSE Server 接受符合 `ConversationSSERequest` 格式的請求：

```json
{
    "model": "gpt-4o",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    "stream": true,
    "sessionId": "session-123",
    "temperature": 0.7,
    "maxTokens": 1000
}
```

### 回應格式

服務器回傳符合 `ConversationSSEResponse` 格式的 SSE 事件：

```json
{
    "id": "msg-1",
    "type": "text",
    "model": "gpt-4o", 
    "text": "Hello! How can I help you?",
    "progress": "IN_PROGRESS",
    "context": {
        "conversationId": "conv-123",
        "cursor": "cursor-abc"
    },
    "metadata": {
        "searchResults": null,
        "attachments": null
    }
}
```

## 驗證機制

### 輸入驗證

1. **HTTP Header 驗證** - 必須包含 `Accept: text/event-stream`
2. **JSON 格式驗證** - 確保請求體為有效的 JSON
3. **Schema 驗證** - 使用 Pydantic 驗證請求符合 `ConversationSSERequest` 格式
4. **業務邏輯驗證** - 檢查模型名稱、訊息結構、長度限制等

### 輸出驗證

1. **型態檢查** - 確保 handler 回傳 `ConversationSSEResponse` 物件
2. **必要欄位檢查** - 驗證 `id`、`type`、`progress` 等必要欄位
3. **進度狀態檢查** - 確保 `progress` 為有效值 (`IN_PROGRESS` 或 `DONE`)

## 錯誤處理

### HTTP 錯誤碼

- `400` - 請求格式錯誤（無效 JSON、空請求等）
- `406` - 缺少 `Accept: text/event-stream` header
- `422` - 請求 schema 驗證失敗
- `404` - Handler 未設定

### SSE 錯誤事件

```
event: error
data: {"error": "Business validation failed", "details": "Unsupported model: invalid-model"}
```

### 自定義異常

```python
from llmbrick.core.exceptions import ValidationException

@server.handler 
async def my_handler(request_data):
    if some_condition:
        raise ValidationException("Custom validation error")
    # ...
```

## 開發者使用模式

### 1. 基本聊天機器人

```python
server = SSEServer()

@server.handler
async def chat_handler(request_data):
    # 簡單的回聲機器人
    user_message = request_data["messages"][-1]["content"]
    
    yield ConversationSSEResponse(
        id="response-1",
        type="text",
        text=f"You said: {user_message}",
        progress="DONE"
    )
```

### 2. 流式回應

```python
@server.handler
async def streaming_handler(request_data):
    response_text = "This is a long response that will be streamed..."
    
    for i, char in enumerate(response_text):
        progress = "DONE" if i == len(response_text) - 1 else "IN_PROGRESS"
        
        yield ConversationSSEResponse(
            id=f"chunk-{i}",
            type="text",
            text=char,
            progress=progress
        )
```

### 3. 整合外部 LLM

```python
import openai

@server.handler
async def openai_handler(request_data):
    # 轉換為 OpenAI 格式
    openai_messages = [
        {"role": msg["role"], "content": msg["content"]} 
        for msg in request_data["messages"]
    ]
    
    # 調用 OpenAI API
    response = await openai.ChatCompletion.acreate(
        model=request_data["model"],
        messages=openai_messages,
        stream=True
    )
    
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield ConversationSSEResponse(
                id=chunk.id,
                type="text",
                text=chunk.choices[0].delta.content,
                progress="IN_PROGRESS"
            )
    
    # 結束標記
    yield ConversationSSEResponse(
        id="final", 
        type="done",
        progress="DONE"
    )
```

## 內建測試頁面

SSEServer 提供了一個開發者友善的測試頁面，可透過 `enable_test_page` 參數啟用：

```python
server = SSEServer(enable_test_page=True)
```

測試頁面功能：

1. **完整的請求配置**
   - 支援所有 ConversationSSERequest 欄位
   - 動態訊息管理（新增/刪除/重排序）
   - 內建欄位說明和類型提示

2. **串流輸出視覺化**
   - 固定高度的輸出區塊，自動捲動到最新訊息
   - 時間戳記標記（HH:MM:SS.mmm）
   - 依訊息類型顯示不同顏色：
     - 一般訊息：預設顏色
     - 錯誤訊息：紅色背景
     - Meta 訊息：藍色背景
     - Done 訊息：綠色背景

3. **使用者體驗優化**
   - 深色/淺色主題切換
   - 支援系統主題偏好
   - 主題設定自動保存
   - 響應式設計，適應不同螢幕大小

4. **開發者工具**
   - API 文件和範例
   - 請求/回應格式說明
   - 欄位描述與規範

![SSE Test Page](sse_server_test.png)

要訪問測試頁面，只需在瀏覽器中開啟伺服器根路徑：
```
http://localhost:8000/
```

## 測試你的應用

### 使用 curl 測試

```bash
# 測試基本 SSE 請求
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "stream": true,
    "sessionId": "test-session-123"
  }'
```

### 測試你的 Handler

```python
import pytest
from fastapi.testclient import TestClient
from llmbrick.servers.sse.server import SSEServer
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse
from llmbrick.core.error_codes import ErrorCodes

def test_my_handler():
    server = SSEServer()
    
    @server.handler
    async def my_handler(request_data):
        yield ConversationSSEResponse(
            id="test-1",
            type="text",
            text="Test response",
            progress="DONE"
        )
    
    client = TestClient(server.fastapi_app)
    
    response = client.post(
        "/chat/completions",
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "test"}],
            "stream": True,
            "sessionId": "test-session"
        },
        headers={"accept": "text/event-stream"}
    )
    
    assert response.status_code == ErrorCodes.SUCCESS
    assert "Test response" in response.content.decode()
```

### JavaScript 客戶端測試

```javascript
// 測試 SSE 連接
const eventSource = new EventSource('/chat/completions');

// 發送 POST 請求（需要使用 fetch + EventSource 組合）
fetch('/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    model: 'gpt-4o',
    messages: [
      { role: 'user', content: 'Hello!' }
    ],
    stream: true,
    sessionId: 'test-session-123'
  })
}).then(response => {
  const reader = response.body.getReader();
  
  function readStream() {
    return reader.read().then(({ done, value }) => {
      if (done) return;
      
      const chunk = new TextDecoder().decode(value);
      console.log('Received:', chunk);
      
      return readStream();
    });
  }
  
  return readStream();
});
```

## 故障排除

### 常見問題

1. **406 錯誤**
   - 確保請求 header 包含 `Accept: text/event-stream`

2. **422 錯誤** 
   - 檢查請求格式是否符合 `ConversationSSERequest` schema
   - 確保 `sessionId` 必要欄位存在

3. **業務驗證失敗**
   - 檢查模型名稱是否在 `allowed_models` 清單中
   - 確認訊息結構符合要求（最後一則為 user 訊息等）

4. **Handler 異常**
   - 啟用 `debug_mode=True` 獲取詳細錯誤訊息
   - 檢查 handler 是否正確回傳 `ConversationSSEResponse` 物件

### 除錯模式

```python
config = SSEServerConfig(
    debug_mode=True,
    enable_request_logging=True,
    enable_validation_details=True
)
```

啟用除錯模式後，你將獲得：
- 詳細的錯誤訊息
- 完整的請求日誌
- 異常堆疊追蹤
- 更多驗證詳情

## 最佳實踐

1. **使用配置類別** - 便於管理和維護
2. **適當的錯誤處理** - 在 handler 中捕獲並處理異常
3. **型態安全** - 始終回傳正確的 `ConversationSSEResponse` 物件
4. **日誌記錄** - 啟用請求日誌以便監控和除錯
5. **測試覆蓋** - 為你的 handler 編寫測試確保功能正常

## 進階功能

### 自定義驗證器

你可以建立自定義驗證器來實現特殊的業務邏輯驗證：

```python
from llmbrick.servers.sse.server import SSEServer
from llmbrick.servers.sse.validators import ConversationSSERequestValidator
from llmbrick.core.exceptions import ValidationException

class CustomValidator(ConversationSSERequestValidator):
    @staticmethod
    def validate(request, allowed_models=None, max_message_length=10000, max_messages_count=100):
        # 先執行基本驗證
        super(CustomValidator, CustomValidator).validate(
            request, allowed_models, max_message_length, max_messages_count
        )
        
        # 自定義驗證邏輯
        if request.temperature and request.temperature > 2.0:
            raise ValidationException("Temperature too high")
        
        # 檢查特定的模型限制
        if request.model == "gpt-4o" and len(request.messages) > 50:
            raise ValidationException("GPT-4o model limited to 50 messages")
        
        # 檢查特殊關鍵字
        for msg in request.messages:
            if "banned_word" in msg.content.lower():
                raise ValidationException("Content contains banned words")

# 使用自定義驗證器
custom_validator = CustomValidator()
server = SSEServer(custom_validator=custom_validator)

@server.handler
async def my_handler(request_data):
    # 到這裡的請求都已經通過自定義驗證
    yield ConversationSSEResponse(
        id="response-1",
        type="text",
        text="Validated request processed",
        progress="DONE"
    )

server.run()
```

### 更簡單的驗證器擴展

如果你只需要添加一些簡單的驗證規則，可以這樣做：

```python
from llmbrick.servers.sse.validators import ConversationSSERequestValidator
from llmbrick.core.exceptions import ValidationException

class MyValidator(ConversationSSERequestValidator):
    @staticmethod
    def validate(request, allowed_models=None, max_message_length=10000, max_messages_count=100):
        # 執行預設驗證
        ConversationSSERequestValidator.validate(
            request, allowed_models, max_message_length, max_messages_count
        )
        
        # 添加你的驗證邏輯
        if hasattr(request, 'client_id') and request.client_id:
            if not request.client_id.startswith('app_'):
                raise ValidationException("Client ID must start with 'app_'")

# 使用方式
server = SSEServer(custom_validator=MyValidator())
```

### 中間件支援

```python
from fastapi import Request

server = SSEServer()

@server.app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # 自定義中間件邏輯
    response = await call_next(request)
    return response
```

這份指南涵蓋了 SSE Server 的主要功能和使用方式。如有其他問題，請參考範例代碼或提交 Issue。