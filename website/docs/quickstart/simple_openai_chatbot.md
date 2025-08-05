---
sidebar_position: 9
sidebar_label: OpenAI 聊天機器人
---

# OpenAI 聊天機器人快速入門

[GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/openai_chatbot)

![](/img/openai_chatbot.gif)

---

## 1. 範例簡介

本教學將帶你快速上手如何使用 LLMBrick 框架，結合 OpenAI GPT Brick 與 SSE Server，打造一個即時串流回應的聊天機器人。此範例展示了如何：

- 整合 OpenAI GPT Brick 與 SSE 服務
- 支援即時串流回應與累積顯示
- 自動偵測系統語言
- 深色/淺色主題切換
- 完整錯誤處理與開發者體驗

---

## 2. 執行步驟

### (1) 設定 OpenAI API 金鑰

請先於終端機設定你的 OpenAI API 金鑰：

```bash
export OPENAI_API_KEY=your_api_key_here
```

### (2) 啟動聊天機器人 SSE 服務

於專案根目錄執行：

```bash
python examples/openai_chatbot/openai_chatbot.py
```

### (3) 開啟測試頁面

啟動後，於瀏覽器開啟：

```
http://127.0.0.1:8000/
```

即可看到即時聊天介面，左側為事件串流，右側為累積回應。

---

## 3. 程式架構與重點說明

### (1) SSE Server 與 OpenAI GPT Brick 整合

主程式 [`openai_chatbot.py`](../../../../examples/openai_chatbot/openai_chatbot.py) 以 `SSEServer` 啟動 HTTP 服務，並將 `ChatHandler` 註冊為聊天請求處理器。`ChatHandler` 會將用戶訊息轉換為 LLMRequest，呼叫 OpenAIGPTBrick 進行串流回應。

```python
# 啟動 SSE 服務器
config = SSEServerConfig(
    host="127.0.0.1",
    port=8000,
    debug_mode=True,
    allowed_models=["gpt-4o", "gpt-3.5-turbo"],
    ...
)
server = SSEServer(config=config, enable_test_page=True)
handler = ChatHandler()
server.set_handler(handler.handle_chat)
server.run()
```

### (2) 支援 gRPC 遠端呼叫

如需將 OpenAI GPT Brick 以 gRPC 方式部署，可參考 [`grpc_server.py`](../../../../examples/openai_chatbot/grpc_server.py)：

```python
from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
openai_brick = OpenAIGPTBrick(
    model_id="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)
grpc_server.register_service(openai_brick)
```

### (3) 串流回應與錯誤處理

- 支援 SSE 串流回傳，前端可即時顯示 LLM 回應片段
- 完整的錯誤處理，包含模型驗證、API 錯誤、系統異常等
- 支援多種 OpenAI 模型（如 gpt-4o、gpt-3.5-turbo）

---

## 4. 介面特色

- **即時串流**：左側顯示事件流，右側累積回應
- **主題切換**：自動偵測深色/淺色主題
- **多語系支援**：自動偵測系統語言
- **開發者友善**：詳細錯誤資訊、API 日誌

---

## 5. 常見問題

- **Q: 為什麼沒有回應？**  
  A: 請確認 OpenAI API 金鑰正確，且網路連線正常。

- **Q: 如何切換使用的 OpenAI 模型？**  
  A: 可於啟動參數 `allowed_models` 或前端選單中切換。

- **Q: 如何自訂 SSE Server 參數？**  
  A: 修改 `SSEServerConfig` 相關設定即可。

---

## 6. 相關文件與延伸閱讀

- [OpenAI GPT Brick 使用指南](../../docs/documents/bricks/llm_brick_guide/openai_llm_brick_guide.md)
- [SSE Server 使用指南](../../docs/documents/servers/sse_server_guide.md)
- [CommonBrick 定義教學](common_brick_define.md)

---

本教學涵蓋了 OpenAI 聊天機器人從安裝、啟動到程式架構的完整流程，適合初學者與進階開發者快速上手 LLMBrick 框架的聊天應用開發。