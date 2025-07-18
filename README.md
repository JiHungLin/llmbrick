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

## 文檔

- [快速開始](docs/quickstart.md)
- [API 參考](docs/api_reference/)
- [教學範例](docs/tutorials/)

## 授權

MIT License