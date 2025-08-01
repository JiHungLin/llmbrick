# 快速開始

歡迎體驗 **llmbrick**！本頁將以最精簡的步驟，帶你從安裝到執行第一個 Brick。

---

## 1. 安裝 llmbrick

```bash
pip install llmbrick
```

---

## 2. 建立你的第一個 Brick

以下以 CommonBrick 為例，實作一個最簡單的服務：

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
            error=ErrorDetail(code=0, message="Success")
        )
```

---

## 3. 執行與測試

直接在本地執行：

```python
import asyncio

async def main():
    brick = HelloBrick()
    req = CommonRequest(data={"name": "Alice"})
    resp = await brick.run_unary(req)
    print(resp.data["message"])  # 輸出: Hello, Alice!

asyncio.run(main())
```

---

## 4. （進階）啟動 gRPC 服務

快速啟動 gRPC server：

```python
from llmbrick.servers.grpc.server import GrpcServer

async def start_grpc_server():
    brick = HelloBrick()
    server = GrpcServer(port=50051)
    server.register_service(brick)
    await server.start()

# asyncio.run(start_grpc_server())
```

---

## 5. （進階）gRPC Client 呼叫

```python
client_brick = HelloBrick.toGrpcClient("127.0.0.1:50051")
resp = await client_brick.run_unary(CommonRequest(data={"name": "Bob"}))
print(resp.data["message"])
await client_brick._grpc_channel.close()
```

---

## 6. 更多範例

- 查看 [指南文件](index.md) 以深入了解各種 Brick 類型與進階用法。
- 參考 [tutorials/](tutorials/index.md) 進行實戰教學。