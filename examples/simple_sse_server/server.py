from llmbrick.servers.sse.server import SSEServer
from llmbrick.servers.sse.config import SSEServerConfig
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse

# 進階設定
config = SSEServerConfig(
    host="127.0.0.1",
    port=9000,
    debug_mode=True,
    allowed_models=["gpt-4o", "claude-3"],
    max_message_length=5000,
    enable_request_logging=True
)

# 啟用測試網頁
server = SSEServer(config=config, enable_test_page=True)

# 註冊 handler 處理請求
@server.handler
async def my_handler(request_data):
    # 回傳訊息（可多次 yield 以支援串流）
    yield ConversationSSEResponse(
        id="msg-1",
        type="text",
        text="Hello World",
        progress="IN_PROGRESS"
    )
    yield ConversationSSEResponse(
        id="msg-2",
        type="done",
        progress="DONE"
    )

# 啟動服務
server.run()