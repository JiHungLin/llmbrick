```
llmbrick/
├── README.md
├── LICENSE                          # 開源授權檔案
├── MANIFEST.in                      # 包含額外檔案的清單
├── requirements.txt                 # 開發依賴
├── requirements-dev.txt             # 開發專用依賴
├── setup.py                         # 傳統安裝腳本
├── pyproject.toml                   # 現代Python專案配置
├── .env.example
├── .gitignore
├── .github/                         # GitHub Actions
│   └── workflows/
│       ├── test.yml                 # CI測試
│       └── publish.yml              # 自動發布到PyPI
├── docker-compose.yml
├── Dockerfile
├── client_examples/                 # 客戶端範例 (供開發者參考)
│   ├── __init__.py
│   ├── javascript/                  # JavaScript客戶端範例
│   │   ├── sse_client.js            # SSE客戶端實作
│   │   ├── websocket_client.js      # WebSocket客戶端
│   │   └── webrtc_client.js         # WebRTC客戶端
│   │
│   ├── python/                      # Python客戶端範例
│   │   ├── sse_client.py
│   │   ├── websocket_client.py
│   │   └── grpc_client.py           # gRPC客戶端
│   │
│   └── html/                        # HTML測試頁面
│       ├── sse_test.html
│       ├── websocket_test.html
│       └── webrtc_test.html
│
├── llmbrick/                        # 核心框架代碼
│   ├── __init__.py
│   ├── version.py
│   │
│   ├── core/                        # 核心基礎設施
│   │   ├── __init__.py
│   │   ├── brick.py                 # Brick基類定義
│   │   ├── pipeline.py              # Pipeline管理
│   │   ├── event_bus.py             # 事件匯流排
│   │   ├── grpc_service.py          # gRPC服務基類
│   │   ├── exceptions.py            # 異常定義
│   │   └── config.py                # 配置管理
│   │
│   ├── bricks/                      # 內建Brick組件
│   │   ├── __init__.py
│   │   ├── base/                    # 基礎組件
│   │   │   ├── __init__.py
│   │   │   ├── rectify.py           # 文字修正
│   │   │   ├── guard.py             # 意圖判斷/防護
│   │   │   └── retrieval.py         # RAG檢索
│   │   │
│   │   ├── llm/                     # LLM組件
│   │   │   ├── __init__.py
│   │   │   ├── base_llm.py          # LLM基類
│   │   │   ├── openai_llm.py        # OpenAI實作
│   │   │   ├── anthropic_llm.py     # Anthropic實作
│   │   │   └── local_llm.py         # 本地模型實作
│   │   │
│   │   ├── asr/                     # 語音識別
│   │   │   ├── __init__.py
│   │   │   ├── base_asr.py
│   │   │   └── google_asr.py
│   │   │
│   │   └── compose/                 # 內容組合/翻譯
│   │       ├── __init__.py
│   │       ├── translator.py
│   │       └── formatter.py
│   │
│   ├── protocols/                   # 通信協議
│   │   ├── __init__.py
│   │   ├── grpc/                    # gRPC相關
│   │   │   ├── __init__.py
│   │   │   ├── brick_service.proto  # protobuf定義
│   │   │   ├── brick_service_pb2.py # 生成的Python代碼
│   │   │   └── brick_service_pb2_grpc.py
│   │   │
│   │   └── models/                  # 資料模型
│   │       ├── __init__.py
│   │       ├── request.py
│   │       ├── response.py
│   │       └── event.py
│   │
│   ├── servers/                     # 對外服務介面
│   │   ├── __init__.py
│   │   ├── sse/                     # SSE服務 (一問一答)
│   │   │   ├── __init__.py
│   │   │   ├── server.py            # SSE伺服器實作
│   │   │   └── handlers.py          # 請求處理器
│   │   │
│   │   ├── websocket/               # WebSocket服務
│   │   │   ├── __init__.py
│   │   │   ├── server.py            # WebSocket伺服器
│   │   │   └── handlers.py          # 訊息處理器
│   │   │
│   │   ├── webrtc/                  # WebRTC服務 (通話式對答)
│   │   │   ├── __init__.py
│   │   │   ├── server.py            # WebRTC伺服器
│   │   │   ├── signaling.py         # 信令處理
│   │   │   └── handlers.py          # 音訊處理器
│   │   │
│   │   └── base/                    # 服務基類
│   │       ├── __init__.py
│   │       ├── server_base.py       # 伺服器基類
│   │       └── middleware.py        # 中介軟體
│   │
│   ├── utils/                       # 工具函數
│   │   ├── __init__.py
│   │   ├── logging.py               # 日誌工具
│   │   ├── metrics.py               # 性能監控
│   │   ├── decorators.py            # 裝飾器
│   │   └── helpers.py               # 幫助函數
│   │
│
├── examples/                        # 範例代碼
│   ├── __init__.py
│   ├── simple_chatbot/              # 簡單聊天機器人
│   │   ├── main.py
│   │   ├── config.yaml
│   │   └── requirements.txt
│   │
│   ├── rag_system/                  # RAG系統範例
│   │   ├── main.py
│   │   ├── documents/
│   │   └── config.yaml
│   │
│   └── voice_assistant/             # 語音助手範例
│       ├── main.py
│       ├── static/
│       └── templates/
│
├── tests/                           # 測試代碼
│   ├── __init__.py
│   ├── conftest.py                  # pytest配置
│   ├── unit/                        # 單元測試
│   │   ├── test_brick.py
│   │   ├── test_pipeline.py
│   │   └── test_event_bus.py
│   │
│   ├── integration/                 # 整合測試
│   │   ├── test_sse_api.py
│   │   └── test_grpc_service.py
│   │
│   └── e2e/                         # 端到端測試
│       └── test_complete_flow.py
│
├── docs/                            # 文檔
│   ├── index.md
│   ├── quickstart.md
│   ├── api_reference/
│   ├── tutorials/
│   └── deployment/
│
├── scripts/                         # 腳本工具
│   ├── generate_proto.py            # 生成protobuf
│   ├── start_dev.py                 # 開發環境啟動
│   └── deploy.py                    # 部署腳本
│
└── config/                          # 配置檔案
    ├── development.yaml
    ├── production.yaml
    └── docker.yaml
```