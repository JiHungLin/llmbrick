# 範例 async flow handler
import asyncio
from typing import Any, AsyncGenerator, Dict

from llmbrick.servers.sse.server import SSEServer

server = SSEServer()
server.fastapi_app


@server.handler
async def simple_flow(request_body: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
    # 模擬訊息處理與回應
    yield {
        "id": "1",
        "type": "text",
        "text": "Hello, this is a streaming response.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {
        "id": "2",
        "type": "text",
        "text": "Here comes the second message.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {
        "id": "3",
        "type": "text",
        "text": "Streaming data is fun!",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {
        "id": "4",
        "type": "text",
        "text": "Let's keep going.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {
        "id": "5",
        "type": "text",
        "text": "Halfway through the stream.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {"id": "6", "type": "text", "text": "Almost done.", "progress": "IN_PROGRESS"}
    await asyncio.sleep(1)
    yield {
        "id": "7",
        "type": "text",
        "text": "Just a few more messages.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {
        "id": "8",
        "type": "text",
        "text": "This is the eighth message.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {
        "id": "9",
        "type": "text",
        "text": "Ninth message coming through.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {
        "id": "10",
        "type": "text",
        "text": "Final message before done.",
        "progress": "IN_PROGRESS",
    }
    await asyncio.sleep(1)
    yield {"id": "11", "type": "done", "progress": "DONE"}


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
