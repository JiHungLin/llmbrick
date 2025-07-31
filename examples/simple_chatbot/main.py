import asyncio
from typing import Any, AsyncGenerator, Dict

# 範例 async flow handler
from llmbrick.servers.sse.server import SSEServer

server = SSEServer()


@server.handler
async def simple_flow(request_body: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
    # 模擬訊息處理與回應
    yield {
        "id": "1",
        "type": "text",
        "text": "Hello, this is a streaming response.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(0.5)
    yield {"id": "1", "type": "done", "progress": "DONE"}


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
