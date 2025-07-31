import pytest
from fastapi.testclient import TestClient
from llmbrick.servers.sse.server import SSEServer

@pytest.fixture
def sse_server():
    server = SSEServer()
    @server.handler
    async def handler(data):
        yield {"message": "ok"}
    return server

def test_fastapi_app_property(sse_server):
    app = sse_server.fastapi_app
    assert app

def test_post_chat_completions_accept_header(sse_server):
    client = TestClient(sse_server.fastapi_app)
    # 缺少 accept header，應回 406
    resp = client.post("/chat/completions", json={"foo": "bar"})
    assert resp.status_code == 406
    # 有 accept header
    resp = client.post(
        "/chat/completions",
        json={"foo": "bar"},
        headers={"accept": "text/event-stream"},
    )
    # 由於 StreamingResponse，狀態碼應為 200
    assert resp.status_code == 200

def test_post_chat_completions_empty_body(sse_server):
    client = TestClient(sse_server.fastapi_app)
    resp = client.post(
        "/chat/completions",
        data="",
        headers={"accept": "text/event-stream"},
    )
    assert resp.status_code == 400
    assert "Empty request body" in str(resp.json())