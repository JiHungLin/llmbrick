import pytest
from fastapi.testclient import TestClient
from llmbrick.servers.sse.server import SSEServer
from llmbrick.protocols.models.http.conversation import ConversationSSEResponse

@pytest.fixture
def sse_server():
    server = SSEServer()
    @server.handler
    async def handler(data):
        yield ConversationSSEResponse(
            id="test-1",
            type="text",
            text="Hello World",
            progress="IN_PROGRESS"
        )
        yield ConversationSSEResponse(
            id="test-2",
            type="done",
            progress="DONE"
        )
    return server

@pytest.fixture
def valid_request():
    return {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ],
        "stream": True,
        "sessionId": "test-session-123"
    }

def test_fastapi_app_property(sse_server):
    app = sse_server.fastapi_app
    assert app

def test_post_chat_completions_accept_header(sse_server, valid_request):
    client = TestClient(sse_server.fastapi_app)
    # 缺少 accept header，應回 406
    resp = client.post("/chat/completions", json=valid_request)
    assert resp.status_code == 406
    # 有 accept header
    resp = client.post(
        "/chat/completions",
        json=valid_request,
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
    assert resp.status_code == 422  # FastAPI returns 422 for request validation errors
    assert resp.json().get("detail") is not None  # FastAPI provides validation details

def test_invalid_json_body(sse_server):
    client = TestClient(sse_server.fastapi_app)
    resp = client.post(
        "/chat/completions",
        data="invalid json",
        headers={"accept": "text/event-stream", "content-type": "application/json"},
    )
    assert resp.status_code == 422  # FastAPI returns 422 for JSON parse errors
    assert resp.json().get("detail") is not None  # FastAPI provides error details

def test_invalid_request_schema(sse_server):
    client = TestClient(sse_server.fastapi_app)
    invalid_request = {"invalid": "data"}
    resp = client.post(
        "/chat/completions",
        json=invalid_request,
        headers={"accept": "text/event-stream"},
    )
    assert resp.status_code == 422
    detail = resp.json().get("detail", [])
    assert any("field required" in str(err).lower() for err in detail)  # FastAPI validation error format

def test_unsupported_model(sse_server):
    client = TestClient(sse_server.fastapi_app)
    invalid_model_request = {
        "model": "unsupported-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
        "sessionId": "test-session-123"
    }
    resp = client.post(
        "/chat/completions",
        json=invalid_model_request,
        headers={"accept": "text/event-stream"},
    )
    assert resp.status_code == 200
    # 檢查串流回應中包含業務驗證錯誤
    content = resp.content.decode()
    assert "Business validation failed" in content

def test_invalid_messages_structure(sse_server):
    client = TestClient(sse_server.fastapi_app)
    # 測試多個system message
    invalid_messages_request = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "First system"},
            {"role": "system", "content": "Second system"},
            {"role": "user", "content": "Hello"}
        ],
        "stream": True,
        "sessionId": "test-session-123"
    }
    resp = client.post(
        "/chat/completions",
        json=invalid_messages_request,
        headers={"accept": "text/event-stream"},
    )
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "Only one system message allowed" in content

def test_valid_request_flow(sse_server, valid_request):
    client = TestClient(sse_server.fastapi_app)
    resp = client.post(
        "/chat/completions",
        json=valid_request,
        headers={"accept": "text/event-stream"},
    )
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "Hello World" in content
    assert "IN_PROGRESS" in content
    assert "DONE" in content
def test_custom_validator():
    from llmbrick.servers.sse.validators import ConversationSSERequestValidator
    from llmbrick.core.exceptions import ValidationException
    
    class CustomValidator(ConversationSSERequestValidator):
        @staticmethod
        def validate(request, allowed_models=None, max_message_length=10000, max_messages_count=100):
            # 執行預設驗證
            ConversationSSERequestValidator.validate(
                request, allowed_models, max_message_length, max_messages_count
            )
            # 自定義驗證：禁止temperature > 1.5
            if hasattr(request, 'temperature') and request.temperature and request.temperature > 1.5:
                raise ValidationException("Temperature too high")
    
    server = SSEServer(custom_validator=CustomValidator())
    
    @server.handler
    async def handler(data):
        yield ConversationSSEResponse(
            id="test-1",
            type="text",
            text="Custom validation passed",
            progress="DONE"
        )
    
    client = TestClient(server.fastapi_app)
    
    # 測試通過自定義驗證的請求
    valid_request = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
        "sessionId": "test-session",
        "temperature": 1.0
    }
    
    resp = client.post(
        "/chat/completions",
        json=valid_request,
        headers={"accept": "text/event-stream"},
    )
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "Custom validation passed" in content
    
    # 測試被自定義驗證器拒絕的請求
    invalid_request = {
        "model": "gpt-4o", 
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
        "sessionId": "test-session",
        "temperature": 2.0  # 超過自定義限制
    }
    
    resp = client.post(
        "/chat/completions",
        json=invalid_request,
        headers={"accept": "text/event-stream"},
    )
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "Temperature too high" in content