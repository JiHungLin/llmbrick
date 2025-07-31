# LLMBrick 框架開發工作項目清單

## 🚀 Phase 1: 核心基礎架構 (預估時間: 2-3 週)

### 1.1 專案初始化
- [x] 建立 GitHub 倉庫和基本目錄結構
- [x] 設定 `.gitignore`, `README.md`, `LICENSE`
- [x] 配置 `pyproject.toml` 和 `setup.py`
- [x] 設定開發環境 (虛擬環境、pre-commit hooks)
- [x] 建立基本的 CI/CD Pipeline (GitHub Actions)

### 1.2 核心抽象層實作 (`llmbrick/core/`)
- [x] **BaseBrick 基類** (`brick.py`)
  - [x] 定義抽象介面 (`各模式的process`)
  - [x] 實作基本的錯誤處理機制
  - [x] 加入日誌記錄功能
  - [x] 支援配置注入

### 1.3 異常處理系統 (`exceptions.py`)
- [x] 定義框架專用異常類別
- [x] 實作異常傳播機制
- [x] 建立錯誤代碼體系

### 1.4 基本測試框架
- [x] 設定 pytest 環境
- [ ] 建立測試基類和輔助函數
- [x] 實作 mock Brick
- [x] 撰寫核心組件的單元測試

---

## 🧱 Phase 2: 基礎 Brick 組件 (預估時間: 2-3 週)

### 2.1 文字處理 Brick (`llmbrick/bricks/base/`)
- [x] **RectifyBrick** (`rectify.py`)  <!-- class 骨架已建立，功能尚未實作 -->
- [ ]   基本文字修正功能 <!-- 尚未實作 -->
- [ ]   整合語法檢查工具 (如 language-tool-python) <!-- 尚未實作 -->
- [ ]   支援多語言修正 <!-- 尚未實作 -->
- [ ]   可設定修正程度 <!-- 尚未實作 -->

- [x] **GuardBrick** (`guard.py`) <!-- class 骨架已建立，功能尚未實作 -->
- [ ]   意圖分類功能 <!-- 尚未實作 -->
- [ ]   Prompt 攻擊偵測 <!-- 尚未實作 -->
- [ ]   內容安全過濾 <!-- 尚未實作 -->
- [ ]   可配置的規則引擎 <!-- 尚未實作 -->

### 2.2 LLM 整合 Brick (`llmbrick/bricks/llm/`)
- [x] **BaseLLMBrick** (`base_llm.py`) <!-- class 骨架已建立，部分功能已實作 -->
- [ ]   LLM 抽象介面定義 <!-- 部分完成，細節待補 -->
- [ ]   統一的請求/回應格式 <!-- 部分完成，細節待補 -->
- [ ]   串流回應支援 <!-- 部分完成，細節待補 -->
- [ ]   重試機制和錯誤處理 <!-- 尚未實作 -->

- [ ] **OpenAI 整合** (`openai_llm.py`) <!-- 檔案已建立，內容為空 -->
- [ ]   GPT 模型支援 <!-- 尚未實作 -->
- [ ]   串流和非串流模式 <!-- 尚未實作 -->
- [ ]   參數配置 (temperature, max_tokens 等) <!-- 尚未實作 -->
- [ ]   成本追蹤 <!-- 尚未實作 -->

### 2.3 檢索 Brick (`retrieval.py`)
- [ ] **基礎 RAG 功能**
  - [ ] 向量資料庫整合 (Chroma/Pinecone)
  - [ ] 文件嵌入和檢索
  - [ ] 相似度搜尋
  - [ ] 結果排序和過濾

---

## 🌐 Phase 3: 伺服器介面實作 (預估時間: 2-3 週)

### 3.1 SSE 伺服器 (`llmbrick/servers/sse/`)
- [x] **基礎伺服器** (`server.py`) <!-- 已有完整 FastAPI SSE server 實作 -->
  - [x] FastAPI 整合
  - [x] SSE 串流實作
  - [x] 請求處理和路由
  - [x] 錯誤處理和回復

### 3.2 WebSocket 伺服器 (`llmbrick/servers/websocket/`)
- [ ] WebSocket 伺服器檔案已建立 (`server.py`, `handlers.py`) <!-- 內容為空，僅有骨架 -->
- [ ] WebSocket 連線管理 <!-- 尚未實作 -->
- [ ] 訊息路由和處理 <!-- 尚未實作 -->
- [ ] 連線狀態管理 <!-- 尚未實作 -->
- [ ] 多客戶端支援 <!-- 尚未實作 -->

<!--
### 3.3 服務基類 (`llmbrick/servers/base/`)
- [ ] **BaseServer** (`server_base.py`)
  - [ ] 共用功能抽象
  - [ ] 中介軟體支援
  - [ ] 日誌和監控整合
--> <!-- 檔案不存在，建議註解 -->

---

## 🛠️ Phase 4: gRPC 分散式支援 (預估時間: 2-3 週)

### 4.1 Protocol Buffer 定義 (`llmbrick/protocols/grpc/`)
- [x] **服務定義** (`llm.proto`/`rectify.proto`/`guard.proto` 等) <!-- proto 檔案已建立且內容完整 -->
  - [x] UnaryCall 介面
  - [x] Subscribe/Publish 串流介面
  - [x] BiDiStream 雙向串流
  - [x] GetServiceInfo 服務資訊

- [x] **生成 Python 代碼**
  - [x] 使用 grpcio-tools 生成
  - [x] 自動化生成腳本檔案已建立 (`scripts/generate_proto.py`，內容僅為註解)

---

## 📚 Phase 5: 範例和文檔 (預估時間: 2-3 週)

### 5.1 範例專案 (`examples/`)
- [x] **簡單聊天SSE Server** (`simple_chatbot/`) <!-- main.py 已有基本對話功能與 SSE 介面整合 -->
  - [x] 基本對話功能
  - [x] SSE 介面整合
  - [x] 配置範例

### 5.2 客戶端範例 (`client_examples/`)
- [] **JavaScript 客戶端** <!-- sse_client.js/websocket_client.js/webrtc_client.js 檔案已建立，內容為空 -->
  - [] SSE 客戶端檔案已建立 <!-- 尚未實作 -->
  - [] WebSocket 客戶端檔案已建立 <!-- 尚未實作 -->
  - [] WebRTC 客戶端檔案已建立 <!-- 尚未實作 -->

- [x] **Python 客戶端**
  - [x] gRPC 客戶端 <!-- grpc_client.py 已有完整範例 -->
  - [ ] 同步/非同步版本 <!-- 僅有 async 範例 -->

### 5.3 文檔撰寫 (`docs/`)
- [] **快速開始指南** (`quickstart.md`) <!-- 檔案已建立，內容為空 -->
- [] **API 參考文檔** (`api_reference/`) <!-- 檔案已建立，內容為空 -->
- [] **教學文章** (`tutorials/brick_developer_guide.md`) <!-- 已有完整內容 -->
- [] **部署指南** (`deployment/`) <!-- 檔案已建立，內容為空 -->
<!-- - [ ] **最佳實踐** (`best_practices.md`) --> <!-- 檔案不存在，建議註解 -->

---

## 🧪 Phase 6: 測試和品質保證 (預估時間: 1-2 週)

### 6.1 測試覆蓋率提升
- [ ] 單元測試覆蓋率 > 80%
- [ ] 整合測試完善
- [x] 端到端測試依 Brick 拆分（test_llm_grpc.py、test_common_grpc.py 已建立）
- [ ] 端到端測試場景
- [ ] 性能測試基準

### 6.2 程式碼品質
- [x] 代碼風格統一 (Black, isort)
- [ ] 型別註解完整 (mypy)
- [ ] 文檔字符串規範 (Google style)
- [ ] 安全性檢查 (bandit)

### 6.3 CI/CD 完善
- [x] 自動化測試 pipeline <!-- .github/workflows/python-ci.yml 已有 -->
- [x] 覆蓋率報告 <!-- 可於 pytest 加參數產生，CI 可擴充 -->
- [x] 安全性掃描 <!-- 可於 CI 加入 bandit，現有流程可擴充 -->
- [x] 自動發布流程 <!-- publish.yml 已有 -->

---

## 🚀 Phase 7: 發布準備 (預估時間: 1 週)

### 7.1 包裝和發布
- [x] PyPI 套件配置最佳化 <!-- setup.py 已有 -->
- [x] 版本號管理系統 <!-- setup.py/version.py 已有 -->
<!-- - [ ] CHANGELOG 維護 --> <!-- 檔案不存在，建議註解 -->
- [x] 發布說明準備 <!-- README.md 已有 -->

### 7.2 社群準備
- [x] GitHub README 優化 <!-- README.md 已有 -->
<!-- - [ ] 貢獻指南 (`CONTRIBUTING.md`) --> <!-- 檔案不存在，建議註解 -->
- [ ] 問題模板和 PR 模板 <!-- 可於 .github/ISSUE_TEMPLATE/ 設定，暫未確認 -->
<!-- - [ ] 安全政策 (`SECURITY.md`) --> <!-- 檔案不存在，建議註解 -->

---

## 📊 優先順序建議

### 🔥 高優先級 (MVP 必需)
1. Phase 1: 核心基礎架構
2. Phase 2: 基礎 Brick 組件 (至少 RectifyBrick + OpenAI LLM)
3. Phase 3: SSE 伺服器基礎實作
4. Phase 6: 一個簡單範例

### 🔸 中優先級 (beta 版本)
1. Phase 4: gRPC 分散式支援
2. Phase 5: 開發者體驗優化
3. 更多 Brick 組件

### 🔹 低優先級 (穩定版本)
1. WebRTC 支援
2. 完整文檔系統
3. 高級插件功能

## 🎯 里程碑規劃

- **Week 1-3**: MVP (核心 + 基本 SSE)
- **Week 4-6**: Alpha (加入更多 Brick)
- **Week 7-9**: Beta (gRPC + CLI)
- **Week 10-12**: RC (完整功能)
- **Week 13-14**: Release (文檔 + 發布)

建議您從 Phase 1 開始，先建立穩固的核心基礎，再逐步擴展功能。每個階段完成後建議進行一次程式碼審查和測試。