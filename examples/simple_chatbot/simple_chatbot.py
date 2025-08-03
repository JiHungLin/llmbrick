import asyncio
from typing import Any, AsyncGenerator, Dict

# 範例 async flow handler
from llmbrick.servers.sse.server import SSEServer
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse

server = SSEServer( enable_test_page=True)


@server.handler
async def simple_flow(
    request_body: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    # 模擬訊息處理與回應
    yield ConversationSSEResponse(
        id="1",
        type="text",
        text="Hello, this is a streaming response.",
        progress="IN_PROGRESS",
    )
    await asyncio.sleep(0.5)
    yield ConversationSSEResponse(
        id="1",
        type="text",
        text="Here is the next part of the response.",
        progress="IN_PROGRESS",
    )
    await asyncio.sleep(0.5)
    yield ConversationSSEResponse(
        id="1",
        type="text",
        text="And here is another chunk.",
        progress="IN_PROGRESS",
    )
    await asyncio.sleep(0.5)
    yield ConversationSSEResponse(
        id="1",
        type="text",
        text="This is yet another message in the stream.",
        progress="IN_PROGRESS",
    )
    await asyncio.sleep(0.5)
    yield ConversationSSEResponse(
        id="1",
        type="text",
        text="Streaming will finish soon.",
        progress="IN_PROGRESS",
    )
    await asyncio.sleep(0.5)
    yield ConversationSSEResponse(
        id="1",
        type="done",
        progress="DONE",
    )


if __name__ == "__main__":
    server.run(host="127.0.0.1", port=8000)
