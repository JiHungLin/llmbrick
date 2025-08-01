import json
from llmbrick.servers.sse.server import SSEServer
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse


app = SSEServer()

@app.handler
async def handle_message(message):
    print(f"Received message: {message}")

    result = ConversationSSEResponse(
        id="1",
        type="message",
        model="gpt-4",
        text="這是一段假資料。",
        progress="completed",
        context=None,
        metadata=None
    )
    print("Sending response:")
    yield ConversationSSEResponse(
        id="1",
        type="message",
        model="gpt-4",
        text="這是一段假資料。",
        progress="completed",
        context=None,
        metadata=None
    )


if __name__ == "__main__":
    app.run(host="localhost", port=8000)