<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 根據我的研究，我發現perplexity跟GPT的對話網頁，基本上都是透過一個問題的POST API建立SSE的請求，你可以提供這個細節嗎? Header需要什麼、Body或QueryParam需要什麼，我想要設計一個通用的SSE API，並且是遵照這幾個大廠的API格式

要設計一個通用、類似Perplexity、OpenAI GPT等主流SSE API對話格式，下面是依據實際API規範整理的「標準Headers」、「Body結構」與「Query/參數」，特別針對SSE（Server-Sent Events）串流需求進行說明：

## 1. HTTP Headers（標準做法）

- `Content-Type: application/json`  // 指定請求的內容格式
- `Authorization: Bearer <Your_Token>`  // 權杖認證（必要）
- `Accept: text/event-stream`  // 回傳為SSE需設定這個（部分實作意即接收SSE）


## 2. POST Body（JSON格式，對話內容）

以下是常見的body範本，無論是OpenAI、Perplexity還是OpenRouter等廠商API都相當接近：

```json
{
  "model": "gpt-4o" 或 "sonar",
  "messages": [
    {"role": "system", "content": "Be precise and concise."},
    {"role": "user", "content": "你的問題內容"}
  ],
  "stream": true
}
```

> 說明：
> - `model`：指定模型名稱（如gpt-4o、gpt-3.5-turbo、sonar等）
> - `messages`：訊息陣列（依GPT對話格式，需指定role與content）
> - `stream`：設為`true`啟用串流SSE回應（必要）

部分API還支援以下可選參數：

- `temperature`：回應多樣性
- `max_tokens`：生成最大token數
- `tools`和`tool_choice`：如支援function call功能


## 3. Query Parameters

一般情境下 Query String 不強制設置，但Google Bard等特殊情境下會用`stream=true`或SSE相關參數於查詢列，標準做法為全放在Body。

## 4. 範例CURL請求（SSE串流）

Perplexity API 範例：[^1_1]

```bash
curl --request POST \
  --url https://api.perplexity.ai/chat/completions \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --header 'Accept: text/event-stream' \
  --data '{
        "model": "sonar",
        "messages": [
          {"role": "system", "content": "Be precise and concise."},
          {"role": "user", "content": "How many stars are there in our galaxy?"}
        ],
        "stream": true
      }'
```

OpenAI SSE流格式：[^1_2]

```json
{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "問題"}],
  "stream": true
}
```


## 5. Response SSE格式（回應）

每個chunk資料會用類似

```
data: {"id":"...","object":"chat.completion.chunk", ...}
```

分段推送，直至最後出現

```
data: [DONE]
```


## 6. Google Bard/Gemini 特色（進階）

- header需加多組cookie，如__Secure-1PSID與User-Agent（官方不開放API，但社群有繞過案例）[^1_3]。
- body參數會混合form-urlencoded及複雜多欄位。


## 結論

你可以依上述規範實作接口，基本原則如下[^1_4][^1_1][^1_5][^1_2]：

1. **POST** 請求至 `/chat/completions` (或/chat接口)。
2. **Headers**：至少含認證（Bearer Token）、Content-Type與SSE內容（Accept: text/event-stream）。
3. **Body**：以`model`、`messages`、`stream`為主，支援對話串流。
4. **SSE回應**：分段送出JSON物件、最後以`data: [DONE]`結束。

這套格式，目前已成對話AI串流API的「行業標準」。

<div style="text-align: center">⁂</div>

[^1_1]: https://docs.perplexity.ai/api-reference/chat-completions-post

[^1_2]: https://gist.github.com/simonw/209b46563b520d1681a128c11dd117bc

[^1_3]: https://gist.github.com/vitouXY/f302b033a6b16c42b4b23694e6c8d5af

[^1_4]: https://doc.302.ai/api-205343637

[^1_5]: https://vercel.com/docs/ai-gateway/openai-compat

[^1_6]: https://apifox.com/apidoc/docs-site/4012774/147522040e0

[^1_7]: https://gist.github.com/rbiswasfc/f38ea50e1fa12058645e6077101d55bb

[^1_8]: https://ithelp.ithome.com.tw/m/articles/10330323

[^1_9]: https://customgpt.ai/get-messages-for-a-conversation-using-rag-api/

[^1_10]: https://betterprogramming.pub/openai-sse-sever-side-events-streaming-api-733b8ec32897

[^1_11]: https://apifox.com/apidoc/docs-site/4012774/api-147522043

[^1_12]: https://platform.openai.com/docs/api-reference/introduction

[^1_13]: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference

[^1_14]: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/

[^1_15]: https://platform.openai.com/docs/api-reference/models/list

[^1_16]: https://www.w3schools.com/html/html5_serversentevents.asp

[^1_17]: https://doc.302.ai/api-212459640

[^1_18]: https://platform.openai.com/docs/guides/streaming-responses

[^1_19]: https://developers.google.com/adsense/management/reference/rest/v2/HttpBody

[^1_20]: https://rdrr.io/cran/gptstudio/man/request_base_perplexity.html


---

# 那麼可以提供我Response的格式嗎？

GPT的像是以下：
event: delta
data: {"v": "\u4e00\u500b\u524d\u7aef"}

perplexity像以下：
event: message
data: {"backend_uuid": "12a620ff-064c-4a49-8e34-c71e3871bdca", "context_uuid": "404824e3-cdab-4b26-9daa-b359011cae77", "uuid": "140b8cec-5f5c-4c15-b781-8e119a89bf73", "frontend_context_uuid": "ff5ac302-a1de-4f4a-9a46-672895b2bf01", "display_model": "turbo", "mode": "CONCISE", "search_focus": "internet", "source": "default", "attachments": [], "thread_url_slug": "gen-ju-wo-de-yan-jiu-wo-fa-xia-EqYg_wZMSkmONMceOHG9yg", "expect_search_results": "false", "gpt4": false, "text_completed": false, "blocks": [{"intended_usage": "pro_search_steps", "plan_block": {"progress": "IN_PROGRESS", "goals": [], "steps": [{"uuid": "", "step_type": "INITIAL_QUERY", "initial_query_content": {"query": "\u90a3\u9ebc\u53ef\u4ee5\u63d0\u4f9b\u6211Response\u7684\u683c\u5f0f\u55ce\uff1f"}, "assets": []}], "final": false}}], "message_mode": "STREAMING", "reconnectable": false, "image_completions": [], "cursor": "06884b90-bef6-7cca-8000-63eb86916fa8", "status": "PENDING", "final_sse_message": false}

根據你的需求，我整理主流SSE對話AI API（以GPT與Perplexity為例）在Server-Sent Events (SSE)的Response格式細節，並提出完整解釋與設計建議，方便你設計通用且實用的SSE Response格式。

## 1. SSE 概念回顧

SSE是一種HTTP 1.1單向串流技術，服務端會以持續的資料“事件”（event）形式推送訊息給客戶端，不需客戶端頻繁重複請求。

SSE標準格式每個事件包含：

```
event: <事件名稱>      （可省略，預設是message）
data: <事件資料>       （單行或多行）
id: <事件id>           （可選，用於斷點續傳）
retry: <時間(ms)>      （可選，重新連線等待時間）
\n                     （事件分隔必須空行）
```


## 2. 主流AI SSE Response格式範例與解析

### 2.1 OpenAI-風格（GPT）

- **event名稱**：`delta` （有些版本是省略event，預設`message`）
- **data內容**：JSON格式，封裝本次新增的文本片段等資訊
- **常見data示例**：

```text
event: delta
data: {"v": "\u4e00\u500b\u524d\u7aef"}  

event: delta
data: {"v": "\u7bc4\u4f8b"}  

event: delta
data: [DONE]
```

- **說明**：
    - `"v"`一般是本次輸出文字（UTF-8轉義的Unicode字元）
    - 透過多個小`delta`事件拼接成完整文字
    - 當完成時送出`data: [DONE]`表示結束流


### 2.2 Perplexity-風格

- **event名稱**：`message`
- **data內容**：包含多個狀態、識別符號與回傳聊天資料的複雜JSON物件
- **示例（簡化版）**：

```text
event: message
data: {
  "backend_uuid": "...",
  "context_uuid": "...",
  "uuid": "...",
  "frontend_context_uuid": "...",
  "display_model": "turbo",
  "mode": "CONCISE",
  "text_completed": false,
  "blocks": [
    {
      "intended_usage": "pro_search_steps",
      "plan_block": {
        "progress": "IN_PROGRESS",
        "goals": [],
        "steps": [
          {
            "step_type": "INITIAL_QUERY",
            "initial_query_content": {"query": "那麼可以提供我Response的格式嗎？"},
            "assets": []
          }
        ],
        "final": false
      }
    }
  ],
  "message_mode": "STREAMING",
  "reconnectable": false,
  "cursor": "06884b90-bef6-7cca-8000-63eb86916fa8",
  "status": "PENDING",
  "final_sse_message": false
}
```

- **說明**：
    - 回傳結構複雜，包含上下文識別（UUID）、模型狀態、segment狀態、文字是否完成以及多種額外輔助訊息（搜索計畫、附件等）
    - 方便客戶端依多維度做處理（UI呈現、錯誤追蹤、斷點續流）


## 3. 建議設計一個通用SSE AI Response格式

結合上述兩者優點，設計**既簡單又可擴展**的SSE回應事件：

```text
event: message  # 也可用 delta 等語意明確名稱

data: {
  "id": "<chunk_id>",          # 唯一識別碼，每塊資料可單獨追蹤
  "type": "text" | "meta" | "done",  # 表示資料類型
  "model": "<model_name>",     # 回應的模型
  "text": "<文本內容>",        # 本次串流新文本
  "progress": "IN_PROGRESS" | "DONE",    # 進度狀態
  "context": {                 # 可擴充的狀態/上下文資訊
    "conversation_id": "...",
    "cursor": "..."
  },
  "metadata": {                # 額外輔助資訊(如搜尋結果、分塊、工具狀態等)
    ...
  }
}
```

- **當完成時**，送出：

```text
event: message
data: {"type": "done", "id": "...", "progress": "DONE"}
```

- **設計重點**：
    - `event`名稱明確，允許擴展（如`message`表示輸出文字，`meta`可傳輔助資料）
    - `data`是JSON字串，客戶端解析簡單，且可包含多個欄位方便狀態管理
    - 包含唯一訊息ID方便重連與去重
    - 支援多階段回應狀態與非同步資訊同步


## 4. 範例

```text
event: message
data: {
  "id": "abc123",
  "type": "text",
  "model": "gpt-4o",
  "text": "這是一段回應文本",
  "progress": "IN_PROGRESS",
  "context": {
    "conversation_id": "conv-xyz",
    "cursor": "cursor-001"
  },
  "metadata": {
    "search_results": [],
    "attachments": []
  }
}
```

最終完成訊息：

```text
event: message
data: {
  "id": "abc123",
  "type": "done",
  "progress": "DONE"
}
```


## 5. 開發者使用考量

- 以JSON封裝資料，輕鬆用標準工具(`JSON.parse`)解析
- 明確`event`機制讓UI可根據`event`類型顯示不同視圖（文字流、狀態更新、錯誤等）
- 統一`id`與`progress`，可管理斷線續連（檢查是否漏接）
- 預留`metadata`欄位方便後續加入任意擴展功能（如工具呼叫結果、參考資料）
- 介面簡單、結構清晰，初學者容易上手也方便維護

若你想，我可以提供一個用**FastAPI**或**Flask**實作的基礎SSE範例，方便你快速帶入這種Response格式並串流。

如你需要，我也可協助設計完整API包括認證、中介軟體等機制，確保符合實務開發需求。

