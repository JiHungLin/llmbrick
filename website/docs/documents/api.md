---
sidebar_position: 0
---
# APIs

## 1. API 總覽

LLMBrick 提供高效、型態安全的 AI 應用 API，支援多種協定（SSE、gRPC），適合對話生成、串流回應、分散式服務等多元場景。設計理念強調：

- **協定彈性**：同一套 Brick 可同時支援 SSE 與 gRPC。
- **型別明確**：所有請求/回應皆有嚴謹型別定義，便於前後端協作。
- **串流友善**：支援多次回應、即時推播，適合 LLM 應用。

### 支援協定

- **SSE（Server-Sent Events）**：主力協定，適合即時串流回應。
- **gRPC**：高效能、跨語言 RPC，適合分散式部署。

### API 使用情境

- 串流聊天機器人
- 多輪對話、即時回饋
- 跨語言、跨平台 AI 服務串接

---

## 2. 主要 API 類型

- **SSE API**：HTTP POST 請求，回應為 SSE 串流事件。
- **gRPC API**：多種 Brick 皆有對應 gRPC 服務，支援 Unary/Streaming。

---

## 3. 端點與方法說明

### 3.1 SSE API

#### 端點

- `POST /chat/completions`  
  - 請求：`ConversationSSERequest` (JSON)
  - 回應：`ConversationSSEResponse` (SSE 串流)

#### 請求範例

:::tip 必須設定 Accept Header
SSE API **請求時，HTTP headers 必須包含**：

```http
Accept: text/event-stream
```

否則將無法正確取得串流回應，且會回傳 406 Not Acceptable 錯誤。
請參考下方 JavaScript 範例與[錯誤處理](#錯誤處理與回報)章節。
:::

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather like today?"}
  ],
  "stream": true,
  "clientId": "client123",
  "sessionId": "1234567890",
  "temperature": 0.7,
  "maxTokens": 100
}
```

#### 回應範例

```json
{
  "id": "1",
  "type": "text",
  "model": "gpt-4o",
  "text": "Hello, this is a streaming response.",
  "progress": "IN_PROGRESS",
  "context": {
    "conversationId": "1234567890",
    "cursor": "abcdefg12345"
  },
  "metadata": {
    "searchResults": {"results": ["result1", "result2"]},
    "attachments": [
      {"type": "image", "url": "http://example.com/image.jpg"}
    ]
  }
}
```

#### Python Handler 範例

```python
from llmbrick.servers.sse.server import SSEServer
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse

server = SSEServer()

@server.handler
async def chat_handler(request_data):
    user_message = request_data["messages"][-1]["content"]
    yield ConversationSSEResponse(
        id="response-1",
        type="text",
        text=f"You said: {user_message}",
        progress="DONE"
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
```

#### JavaScript 客戶端串流範例

```javascript
fetch('/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    model: 'gpt-4o',
    messages: [{ role: 'user', content: 'Hello!' }],
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

:::warning
**注意：SSE 串流 API 必須設定 `Accept: text/event-stream` header！**
若未正確設定，伺服器將回傳 406 Not Acceptable 錯誤，無法取得串流資料。
:::

---

### 3.2 gRPC API

- 每個 Brick（如 LLM、Guard、Compose 等）皆有對應 gRPC 服務，支援 Unary/Streaming。
- 端點、方法、型別詳見 [Bricks 文件](../category/bricks/) 與 [proto 定義](https://github.com/JiHungLin/llmbrick/tree/main/llmbrick/protocols/grpc)。

#### gRPC 通用設計說明

LLMBrick 的 gRPC API 採用高度通用、型態安全的設計，方便擴充與跨語言串接。
主要特色如下：

- **四種呼叫型態**（對應 gRPC 標準與 Python decorator）：
  | 呼叫型態         | gRPC 方法                | Python decorator                | 用途說明                  |
  |------------------|-------------------------|---------------------------------|---------------------------|
  | Unary            | `Unary`                 | `@unary_handler`                | 一般請求/回應             |
  | Server Streaming | `OutputStreaming`       | `@output_streaming_handler`     | 伺服器多次回應（如串流）   |
  | Client Streaming | `InputStreaming`        | `@input_streaming_handler`      | 客戶端多次送資料           |
  | Bidi Streaming   | `BidiStreaming`         | `@bidi_streaming_handler`       | 雙向串流                   |

- **通用訊息格式**（見 [`common.proto`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/common/common.proto)）：
  - `CommonRequest`/`CommonResponse` 以 `google.protobuf.Struct` 傳遞彈性資料結構。
  - `ErrorDetail` 統一錯誤回報格式，便於前後端自動處理。
  - `ServiceInfoRequest`/`ServiceInfoResponse` 支援服務發現與模型資訊查詢。

- **服務介面範例**（proto 定義）：
  ```proto
  service CommonService {
    rpc GetServiceInfo(ServiceInfoRequest) returns (ServiceInfoResponse);
    rpc Unary (CommonRequest) returns (CommonResponse) {}
    rpc OutputStreaming (CommonRequest) returns (stream CommonResponse) {}
    rpc InputStreaming (stream CommonRequest) returns (CommonResponse) {}
    rpc BidiStreaming (stream CommonRequest) returns (stream CommonResponse) {}
  }
  ```

- **Python Handler 實作方式**（以 `llmbrick/core/brick.py` 為例）：

  - **Class-level Decorator（常見寫法）**
    ```python
    from llmbrick.core.brick import BaseBrick, unary_handler, output_streaming_handler

    class MyBrick(BaseBrick):
        @unary_handler
        async def my_unary(self, request):
            # 處理單次請求
            return {"result": "ok"}

        @output_streaming_handler
        async def my_stream(self, request):
            for i in range(3):
                yield {"chunk": i}
    ```

  - **物件導向 Decorator（直接註冊函式）**
    也可直接用 Brick 物件的 decorator 方法（如 `.unary()`、`.output_streaming()`）註冊 handler，常用於 script/demo 或不需自訂 class 的情境：

    ```python
    from llmbrick.bricks.common import CommonBrick

    common_brick = CommonBrick()

    @common_brick.unary()
    async def my_unary(request):
        return {"result": "ok"}

    @common_brick.output_streaming()
    async def my_stream(request):
        for i in range(3):
            yield {"chunk": i}

    # 之後可將 common_brick 物件註冊到 server 或直接用於測試
    ```
    這種寫法適合快速註冊 handler，無需自訂 class，與 class-level decorator 寫法等價，依專案需求選擇。

- **擴充與自訂**：
  - 可依需求自訂 handler，並用 decorator 標註型態。
  - 支援自動註冊與型別檢查，避免 handler 實作錯誤。
  - 服務資訊查詢（`GetServiceInfo`）可回報模型支援、版本、串流能力等。

- **常見用途**：
  - 跨語言/平台串接（Python、Go、Node.js 等皆可用 gRPC client）。
  - 高效能、型態安全的分散式 AI 服務。
  - 支援多種串流場景（如 LLM 回應、資料同步等）。

> 進階設計與實作細節，請參考 [llmbrick/core/brick.py](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py) 及 [proto 定義](https://github.com/JiHungLin/llmbrick/tree/main/llmbrick/protocols/grpc)。

---

## 4. 型別定義與資料結構

### 4.1 ConversationSSERequest（主型態）

| 欄位           | 型別         | 必填 | 說明 |
|----------------|--------------|------|------|
| model          | str          | ✔    | 指定模型名稱 (如 'gpt-4o') |
| messages       | List[Message]| ✔    | 訊息陣列，詳見下方 Message |
| stream         | bool         | ✔    | 是否啟用串流，必須為 True |
| clientId       | str          |      | 客戶端識別碼 (選填) |
| sessionId      | str          | ✔    | 對話 session id |
| temperature    | float        |      | 回應多樣性 (選填) |
| maxTokens      | int          |      | 生成最大 token 數 (選填) |
| tools          | List[Any]    |      | 工具列表 (選填) |
| toolChoice     | Any          |      | 工具選擇 (選填) |
| sourceLanguage | str          |      | 源語言 (選填) |

**範例：**
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather like today?"}
  ],
  "stream": true,
  "clientId": "client123",
  "sessionId": "1234567890",
  "temperature": 0.7,
  "maxTokens": 100
}
```

---

### 4.2 ConversationSSEResponse（主型態）

| 欄位      | 型別                | 必填 | 說明 |
|-----------|---------------------|------|------|
| id        | str                 | ✔    | 唯一識別碼 |
| type      | str                 | ✔    | 資料類型，如 'text', 'meta', 'done' |
| model     | str                 |      | 回應的模型名稱 (選填) |
| text      | str                 |      | 本次串流新文本 (選填) |
| progress  | str                 | ✔    | 進度狀態，如 'IN_PROGRESS', 'DONE' |
| context   | SSEContext          |      | 上下文資訊 (選填，詳見下方 SSEContext) |
| metadata  | SSEResponseMetadata |      | 輔助資訊 (選填，詳見下方 SSEResponseMetadata) |

**範例：**
```json
{
  "id": "1",
  "type": "text",
  "model": "gpt-4o",
  "text": "Hello, this is a streaming response.",
  "progress": "IN_PROGRESS",
  "context": {
    "conversationId": "1234567890",
    "cursor": "abcdefg12345"
  },
  "metadata": {
    "searchResults": {"results": ["result1", "result2"]},
    "attachments": [
      {"type": "image", "url": "http://example.com/image.jpg"}
    ]
  }
}
```

---

### 4.3 子型態說明

#### Message

| 欄位      | 型別   | 必填 | 說明 |
|-----------|--------|------|------|
| role      | str    | ✔    | 訊息角色，如 'system', 'user', 'assistant' |
| content   | str    | ✔    | 訊息內容 |

**範例：**
```json
{"role": "user", "content": "What is the weather like today?"}
```

#### SSEContext

| 欄位           | 型別   | 必填 | 說明 |
|----------------|--------|------|------|
| conversationId | str    |      | 對話ID (選填) |
| cursor         | str    |      | 游標 (選填) |

**範例：**
```json
{"conversationId": "1234567890", "cursor": "abcdefg12345"}
```

#### SSEResponseMetadata

| 欄位         | 型別   | 必填 | 說明 |
|--------------|--------|------|------|
| searchResults| Any    |      | 搜尋結果 (選填) |
| attachments  | Any    |      | 附件 (選填) |

**範例：**
```json
{
  "searchResults": {"results": ["result1", "result2"]},
  "attachments": [
    {"type": "image", "url": "http://example.com/image.jpg"}
  ]
}
```

---

### 4.4 欄位命名與 JSON 格式

- 支援 Python snake_case 及 JSON camelCase（如 `session_id` 對應 `sessionId`）。
- 請依實際 API 文件與程式碼同步。

---

## 5. 錯誤處理與回報

### HTTP 標準狀態碼

| 名稱         | 代碼 |
| ------------ | ---- |
| SUCCESS      | 200  |
| BAD_REQUEST  | 400  |
| UNAUTHORIZED | 401  |
| NOT_FOUND    | 404  |
| INTERNAL_ERROR | 500 |

### 框架特定錯誤碼

| 名稱                | 代碼  | 說明         |
|---------------------|-------|--------------|
| VALIDATION_ERROR    | 2000  | 驗證錯誤     |
| PARAMETER_MISSING   | 2002  | 參數缺失     |
| MODEL_ERROR         | 4000  | 模型錯誤     |
| MODEL_NOT_FOUND     | 4001  | 模型未找到   |
| EXTERNAL_SERVICE_ERROR | 5000 | 外部服務錯誤 |
| RESOURCE_NOT_FOUND  | 6001  | 資源未找到   |

> 完整錯誤碼請參考 [llmbrick/core/error_codes.py (GitHub)](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/error_codes.py)。

---

### 常見錯誤情境

- **406 Not Acceptable**：請求 header 缺少 `Accept: text/event-stream`
- **422 Unprocessable Entity**：請求格式不符 `ConversationSSERequest`，或缺少 `sessionId`
- **業務驗證失敗**：模型名稱不在允許清單、訊息結構錯誤
- **Handler 異常**：回傳型別錯誤、未正確 yield `ConversationSSEResponse`
- **模型錯誤**：模型名稱錯誤、模型服務異常
- **外部服務錯誤**：串接外部 API 失敗
- **資源未找到**：請求資源不存在

### 錯誤格式與處理建議

- 回應型別 `type: "error"`，`text` 為錯誤訊息，`metadata.attachments` 可帶錯誤細節。
- 建議前端根據 `type` 與 `progress` 判斷是否為錯誤事件。
- 錯誤碼可於 `metadata.attachments` 內帶出，便於前端自動化處理。

#### 錯誤回應範例

```json
{
  "id": "validation-error",
  "type": "error",
  "text": "驗證錯誤: sessionId 缺失",
  "progress": "DONE",
  "metadata": {
    "attachments": [
      { "type": "error", "code": "validation_error", "message": "sessionId 缺失" }
    ]
  }
}
```

#### 其他錯誤回應範例

```json
{
  "id": "model-error",
  "type": "error",
  "text": "模型服務異常",
  "progress": "DONE",
  "metadata": {
    "attachments": [
      { "type": "error", "code": "model_error", "message": "模型服務異常" }
    ]
  }
}
```

```json
{
  "id": "external-service-error",
  "type": "error",
  "text": "外部 API 連線失敗",
  "progress": "DONE",
  "metadata": {
    "attachments": [
      { "type": "error", "code": "external_service_error", "message": "外部 API 連線失敗" }
    ]
  }
}
```

### Troubleshooting 指南

- 檢查 header、請求格式、必填欄位
- 檢查模型名稱、sessionId 是否正確
- 檢查外部服務連線狀態
- 啟用 `debug_mode=True` 取得詳細錯誤
- 參考 [SSE Server Guide](./servers/sse_server_guide.md) 常見問題

---

## 6. FAQ 與進階應用

### 常見問題

- **Q: 如何支援多次串流回應？**  
  A: 在 handler 內多次 `yield ConversationSSEResponse(...)`，每次即為一個 SSE event。

- **Q: 如何自訂回應格式？**  
  A: 請依照 `ConversationSSEResponse` 結構填入所需欄位，支援 id/type/text/progress 等。

- **Q: 如何整合至正式服務？**  
  A: 可將 SSEServer 整合至主應用程式，或以 Docker 部署，並依需求擴充 handler 邏輯。

### 進階串接技巧

- 支援自訂中間件（middleware），可攔截/處理所有請求。
- 可結合多種 Brick，實現複雜對話流程。
- gRPC 與 SSE 可無縫切換，便於測試與部署。

---

## 7. 參考資源

- [SSE Server Guide](./servers/sse_server_guide.md)
- [Bricks 文件](../category/bricks/)
- [gRPC proto 定義](https://github.com/JiHungLin/llmbrick/tree/main/llmbrick/protocols/grpc)
- [SSE 規範（MDN）](https://developer.mozilla.org/zh-TW/docs/Web/API/Server-sent_events)

---

