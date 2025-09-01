---
sidebar_position: 0
sidebar_label: SSE Server 快速上手
---

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/simple_sse_server)

# 建立與啟動 SSE Server

本教學將帶你快速上手 LLMBrick 的 SSE (Server-Sent Events) Server，並說明如何自訂請求處理邏輯。你將學會如何設定伺服器、撰寫 handler、啟動服務，以及如何進行本地測試。適合初學者與進階開發者。

---

## 1. 前置準備

- 已安裝 Python 3.8 以上版本
- 已安裝 `llmbrick` 套件
- 建議使用虛擬環境管理依賴

```bash
pip install llmbrick
```

---

## 2. SSE Server 範例程式碼

以下為一個最小可執行的 SSE Server 範例，檔案路徑：`examples/simple_sse_server/server.py`。

```python
from llmbrick.servers.sse.server import SSEServer
from llmbrick.servers.sse.config import SSEServerConfig
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse

# 進階設定
config = SSEServerConfig(
    host="127.0.0.1",
    port=9000,
    debug_mode=True,
    allowed_models=["gpt-4o", "claude-3"],
    max_message_length=5000,
    enable_request_logging=True
)

# 啟用測試網頁
server = SSEServer(config=config, enable_test_page=True)

# 註冊 handler 處理請求
@server.handler
async def my_handler(request_data):
    # 回傳訊息（可多次 yield 以支援串流）
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

# 啟動服務
server.run()
```

---

## 3. 程式碼說明

- **SSEServerConfig**：用於設定伺服器參數（如 host、port、允許的模型、訊息長度限制等）。
- **SSEServer**：建立 SSE 伺服器實例，`enable_test_page=True` 會自動啟用內建測試網頁，方便本地測試。
- **@server.handler**：註冊一個 async handler 處理所有進入的請求。可多次 `yield` 回應以支援串流。
- **ConversationSSEResponse**：標準化 SSE 回應格式，支援 id、type、text、progress 等欄位。
- **server.run()**：啟動伺服器，開始監聽請求。

---

## 4. 啟動 SSE Server

於終端機執行：

```bash
python examples/simple_sse_server/server.py
```

預設會啟動在 `http://127.0.0.1:9000`。

---

## 5. 測試與驗證

1. **瀏覽器測試**  
   啟動後，於瀏覽器開啟 [http://127.0.0.1:9000/](http://127.0.0.1:9000/)  
   可直接發送測試請求，觀察 SSE 串流回應。

   ![SSE Server 測試網頁畫面](/img/sse_server_test.png)

---

## 6. 進階設定與最佳實踐

- **安全性**：建議設定 `allowed_models` 限制可用模型，避免未授權存取。
- **日誌管理**：`enable_request_logging=True` 可協助除錯與追蹤請求。
- **效能調校**：可依需求調整 `max_message_length`，避免過大訊息造成資源耗盡。

---

## 7. 常見問題

- **Q: 如何支援多次串流回應？**  
  A: 在 handler 內多次 `yield ConversationSSEResponse(...)`，每次即為一個 SSE event。

- **Q: 如何自訂回應格式？**  
  A: 請依照 `ConversationSSEResponse` 結構填入所需欄位，支援 id/type/text/progress 等。

- **Q: 如何整合至正式服務？**  
  A: 可將 SSEServer 整合至主應用程式，或以 Docker 部署，並依需求擴充 handler 邏輯。

---

## 8. 參考資源

- [SSE 協定說明（MDN）](https://developer.mozilla.org/zh-TW/docs/Web/API/Server-sent_events)
- [完整範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/simple_sse_server)

---

本教學涵蓋了 SSE Server 的基本設定、啟動與測試流程，協助你快速上手 LLMBrick 的串流服務開發。如需進階應用，請參考其他相關教學文件。
