# gRPC Server

本指南詳細說明 [`llmbrick/servers/grpc/server.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/servers/grpc/server.py) 中的 gRPC Server 實作，適合初學者與團隊成員快速上手與深入理解。

---

## 目標與用途

- **目標**：提供一個簡化、易於擴展且支援優雅關閉（graceful shutdown）的 gRPC 伺服器框架。
- **解決問題**：讓開發者能夠輕鬆註冊自訂服務（Brick），並確保伺服器在接收到終止訊號時能正確釋放資源與關閉。

---

## 專案結構與模組說明

```plaintext
llmbrick/
└── servers/
    └── grpc/
        ├── server.py      # gRPC Server 主體
        └── wrappers/
            └── ...        # 各類服務註冊包裝器
```

- [`server.py`](../../../llmbrick/servers/grpc/server.py): 定義 `GrpcServer` 類別，負責伺服器的啟動、註冊服務、優雅關閉等。
- `wrappers/`: 提供各種 Brick 服務的註冊函式，讓不同類型的服務能被動態掛載到 gRPC Server。

---

## 安裝與執行指南

### 安裝步驟

請先安裝 llmbrick 套件，所有必要依賴會自動安裝：

```bash
pip install llmbrick
```

### 啟動 gRPC Server 範例

```python
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.servers.grpc.server import GrpcServer
from my_brick import MyBrick  # 假設你已經實作好一個 Brick

server = GrpcServer(port=50051)
server.register_service(MyBrick())
server.run()
```

---

## 逐步範例

### 1. 建立自訂 Brick

```python
from llmbrick.bricks.common.common import CommonBrick

class MyBrick(CommonBrick):
    # 實作你的 gRPC 服務
    ...
```

### 2. 註冊並啟動 Server

```python
from llmbrick.servers.grpc.server import GrpcServer

server = GrpcServer(port=60000)
server.register_service(MyBrick())
server.run()
```

### 3. 優雅關閉

- 伺服器會自動監聽 SIGINT/SIGTERM 訊號（如 Ctrl+C），收到後會呼叫 `stop()` 進行優雅關閉。

---

## 核心 API / 類別 / 函式解析

### [`GrpcServer`](http://github.com/JiHungLin/llmbrick/blob/main/llmbrick/servers/grpc/server.py#L19)

#### 初始化

```python
GrpcServer(port: int = 50051)
```
- **port**: 監聽的 gRPC 端口，預設 50051。

#### 註冊服務

```python
register_service(brick: BaseBrick) -> None
```
- **brick**: 需繼承自 `BaseBrick` 的服務實例。
- **用途**: 將自訂服務加入待註冊清單，於啟動時一併掛載。

#### 啟動伺服器（異步）

```python
await start() -> None
```
- 建立 gRPC 伺服器、註冊所有服務、綁定端口並啟動。
- 會阻塞直到伺服器終止。

#### 停止伺服器（異步）

```python
await stop() -> None
```
- 優雅關閉伺服器，預設有 3 秒緩衝期讓現有請求完成。

#### 運行主入口

```python
run() -> None
```
- 包含訊號處理（SIGINT/SIGTERM），自動呼叫 `stop()`。
- 適合直接用於主程式入口。

---

## 常見錯誤與排除

- **端口被佔用**：啟動時若端口已被佔用，會拋出錯誤。請確認端口未被其他程式使用。
- **未註冊服務**：若未呼叫 `register_service()`，伺服器啟動後不會有任何服務可用。
- **Windows 訊號處理**：Windows 平台訊號處理有限，建議用 Ctrl+C 終止，`finally` 區塊會確保資源釋放。
- **異步錯誤未捕獲**：如有異步例外未處理，會記錄於 logger 並嘗試優雅關閉。

---

## 最佳實踐與進階技巧

- **一次註冊多個 Brick**：可多次呼叫 `register_service()`，於啟動時一併掛載。
- **自訂 logger**：可替換 `llmbrick.utils.logging.logger` 以整合自家日誌系統。
- **資源釋放**：確保 Brick 內部有正確的資源釋放邏輯（如關閉資料庫連線）。
- **單元測試**：可針對 `start()`、`stop()` 進行異步測試，模擬訊號觸發。

---

## FAQ / 進階問答

**Q1: 如何同時註冊多個服務？**  
A: 多次呼叫 `register_service()`，每個 Brick 會在啟動時自動掛載。

**Q2: 如何自訂關閉時的行為？**  
A: 可覆寫 Brick 的 `close()` 或相關釋放方法，`GrpcServer` 會呼叫 `stop()` 進行優雅關閉。

**Q3: 可以用於生產環境嗎？**  
A: 本 Server 著重於簡化與教學，生產環境建議加強安全性、監控與日誌。

**Q4: 如何整合自訂的訊號處理？**  
A: 可參考 `run()` 內部的 `_run_with_signals()`，於 Unix 平台可自訂訊號處理邏輯。

---

## 參考資源

- [gRPC 官方文件](https://grpc.io/docs/)
- [llmbrick 專案](https://github.com/JiHungLin/llmbrick)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

如有更多問題，歡迎參考原始碼或提出 Issue！