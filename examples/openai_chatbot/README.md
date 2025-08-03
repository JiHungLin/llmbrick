# LLMBrick Examples

This directory contains example implementations and use cases for LLMBrick.

## OpenAI GPT Brick with SSE Server

[`openai_chatbot.py`](openai_chatbot.py) - 完整的 OpenAI GPT Brick 整合範例：
- SSE 服務器整合
- 串流輸出顯示
- 即時累積回應
- 自動系統語言偵測
- 深色/淺色主題支援
- 完整錯誤處理

### 使用方式

1. 設定 API 金鑰：
```bash
export OPENAI_API_KEY=your_api_key_here
```

2. 執行範例：
```bash
python examples/openai_chatbot/openai_chatbot.py
```

3. 開啟測試頁面：
```
http://127.0.0.1:8000/
```

### 功能特色

1. 即時串流回應
   - 左側面板：完整事件串流
   - 右側面板：累積文字回應
   - 自動捲動和格式化

2. 系統整合
   - 自動偵測系統語言
   - 支援多種 OpenAI 模型
   - 完整的錯誤處理

3. 開發者體驗
   - 即時串流顯示
   - 深色/淺色主題
   - API 文檔和範例
   - 完整的錯誤資訊

### 相關文件

- [OpenAI GPT Brick 使用指南](../docs/guides/openai_llm_brick_guide.md)
- [SSE Server 使用指南](../docs/guides/sse_server_guide.md)