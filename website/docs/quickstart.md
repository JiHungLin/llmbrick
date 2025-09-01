# 快速入門

## 快速上手概述

本指南旨在幫助您在最短時間內開始使用 LLMBrick 框架。我們將通過具體步驟，引導您完成環境設置、基本概念理解，以及第一個應用的開發。

### 適用對象
- 初次使用 LLMBrick 的開發者
- 想要快速建立 LLM 應用的工程師
- 需要參考基礎範例的使用者

## 章節使用說明

本快速入門指南分為以下幾個部分：
1. **環境準備**：安裝和配置必要環境
2. **基礎概念**：了解 Brick 和框架基本概念
3. **實作範例**：手把手建立第一個應用
4. **進階主題**：更多功能和最佳實踐

建議按順序閱讀，但您也可以根據需求直接跳到特定章節。

## 快速開始步驟

## 1. 安裝 llmbrick

```bash
pip install llmbrick
```

---

## 2. 建立一個簡單的 Brick

**檔案名稱：`hello_brick.py`**

這個檔案定義了一個最簡單的 Brick，會回傳問候訊息。

```python
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.core.brick import unary_handler
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ErrorDetail
from llmbrick.core.error_codes import ErrorCodes

class HelloBrick(CommonBrick):
    @unary_handler
    async def hello(self, request: CommonRequest) -> CommonResponse:
        name = request.data.get("name", "World")
        return CommonResponse(
            data={"message": f"Hello, {name}!"},
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )
```

---

## 3. 本機調用 Brick

**檔案名稱：`local_test.py`**

這個腳本示範如何在本機直接建立並呼叫你的 Brick。

```python
import asyncio
from hello_brick import HelloBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest

async def main():
    brick = HelloBrick()
    req = CommonRequest(data={"name": "Alice"})
    resp = await brick.run_unary(req)
    print(resp.data["message"])  # 輸出: Hello, Alice!

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. 使用 Brick 搭建 gRPC 伺服器

**檔案名稱：`grpc_server.py`**

這個腳本會啟動一個 gRPC 伺服器，並註冊你的 Brick 為服務。

```python
import asyncio
from hello_brick import HelloBrick
from llmbrick.servers.grpc.server import GrpcServer

brick = HelloBrick()
server = GrpcServer(port=50051)
server.register_service(brick)

if __name__ == "__main__":
    server.run()
```

---

## 5. 建立 gRPC Client 進行測試

**檔案名稱：`grpc_client.py`**

這個腳本會連線到 gRPC 伺服器，並遠端呼叫你的 Brick。

```python
import asyncio
from llmbrick.protocols.models.bricks.common_types import CommonRequest
from hello_brick import HelloBrick

async def main():
    client_brick = HelloBrick.toGrpcClient("127.0.0.1:50051")
    resp = await client_brick.run_unary(CommonRequest(data={"name": "Bob"}))
    print(resp.data["message"])  # 輸出: Hello, Bob!

if __name__ == "__main__":
    asyncio.run(main())
```

## 環境需求

- Python 3.8 或以上版本
- pip（Python 包管理器）
- 虛擬環境（建議使用 venv 或 conda）

## 範例流程解析

### 1. Brick 結構說明
- **CommonBrick**：最基礎的 Brick 類型
- **unary_handler**：處理單一請求的裝飾器
- **Request/Response**：定義輸入輸出格式
- **gRPC 伺服器/Client**：可將 Brick 服務化，並支援跨進程或跨機器呼叫

### 2. 關鍵概念
- **Brick 組件化**：每個功能都是獨立的 Brick
- **協定定義**：明確的資料流和型別
- **非同步處理**：使用 async/await 支援
- **gRPC 通訊**：可將 Brick 以 gRPC 方式對外提供服務，並可用 client 進行遠端呼叫

### 3. 常見使用場景
- 建立聊天機器人
- 串接 OpenAI API
- 實現多語言翻譯
- 自訂 AI 應用邏輯
- 以 gRPC 方式部署與串接多個 Brick 服務

## 常見問題與解決方案

### 1. 安裝問題
- 確認 Python 版本兼容性
- 使用虛擬環境避免衝突
- 更新 pip 到最新版本

### 2. 執行錯誤
- 檢查 async/await 使用正確性
- 確認型別定義完整
- 查看錯誤碼對應說明
- 若 gRPC 連線失敗，請確認 server 已啟動且 port 設定正確

## 下一步

完成基礎設置後，您可以：

1. 🔍 瀏覽[詳細範例](./quickstart/examples)
2. 📚 深入了解[進階文件](./documents)
3. 🛠️ 開發自己的 Brick 組件

## 快速參考

- [API 文件](./documents/api)
- [範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples)