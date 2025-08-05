# 快速開始

歡迎體驗 **llmbrick**！本指南將以明確步驟，帶你從零開始建立並測試你的第一個 Brick，每個步驟都對應一個獨立檔案，讓新手也能輕鬆上手。

---

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

async def main():
    brick = HelloBrick()
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
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

---

## 6. 更多資源

- 查看 [指南文件](index.md) 以深入了解各種 Brick 類型與進階用法。
- 參考 [tutorials/](tutorials/index.md) 進行實戰教學。