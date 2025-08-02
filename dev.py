import asyncio
import json
from llmbrick.servers.sse.config import SSEServerConfig
from llmbrick.servers.sse.server import SSEServer
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse

config = SSEServerConfig(debug_mode=True)
app = SSEServer(enable_test_page=True, config=config)

@app.handler
async def handle_message(message):
    print(f"Received message: {message}")

    for i in range(5):
        # Simulate processing time
        await asyncio.sleep(1)
        yield ConversationSSEResponse(
            id=str(i),
            type="message",
            model="gpt-4",
            text=f"這是一段假資料 {i + 1}。",
            progress="IN_PROGRESS" if i < 4 else "DONEasd",
            context=None,
            metadata=None
        )
    


if __name__ == "__main__":
    app.run(host="localhost", port=8000)