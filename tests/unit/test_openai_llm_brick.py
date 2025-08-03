"""
OpenAI GPT Brick 單元測試

測試 OpenAI GPT 整合的 LLMBrick 實作，包含：
- 初始化參數驗證
- API 呼叫模擬
- 各種 handler 行為測試
- 錯誤處理測試
"""

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, Context
from llmbrick.protocols.models.bricks.common_types import ErrorDetail


@pytest.fixture
def mock_api_key(monkeypatch):
    """模擬設置 OpenAI API key 環境變數"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")


@pytest.fixture
def mock_openai_client():
    """模擬 OpenAI API 客戶端"""
    with patch("openai.AsyncOpenAI") as mock:
        yield mock


@pytest.mark.asyncio
async def test_init_with_api_key():
    """測試使用 API key 初始化"""
    brick = OpenAIGPTBrick(api_key="test-key")
    assert brick.model_id == "gpt-3.5-turbo"
    assert "gpt-3.5-turbo" in brick.supported_models
    assert "gpt-4" in brick.supported_models


@pytest.mark.asyncio
async def test_init_without_api_key(monkeypatch):
    """測試缺少 API key 時的錯誤處理"""
    # 確保環境中沒有 API key
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    with pytest.raises(ValueError) as exc_info:
        OpenAIGPTBrick()
    assert "OpenAI API key must be provided" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_unary_handler(mock_api_key, mock_openai_client):
#     """測試單次請求處理"""
#     # 模擬 API 回應
#     mock_completion = ChatCompletion(
#         id="test",
#         model="gpt-3.5-turbo",
#         object="chat.completion",
#         created=1234567890,
#         choices=[
#             Choice(
#                 index=0,
#                 message=ChatCompletionMessage(
#                     role="assistant",
#                     content="Test response"
#                 ),
#                 finish_reason="stop"
#             )
#         ]
#     )
    
#     # 設置模擬行為
#     # Create ChatCompletionMessage instance
#     message = ChatCompletionMessage(
#         role="assistant",
#         content="Test response"
#     )
    
#     # Create Choice instance
#     choice = Choice(
#         index=0,
#         message=message,
#         finish_reason="stop"
#     )
    
#     # Create ChatCompletion instance
#     mock_completion = ChatCompletion(
#         id="test",
#         model="gpt-3.5-turbo",
#         object="chat.completion",
#         created=1234567890,
#         choices=[choice]
#     )
    
#     # Set up mock client
#     mock_client = AsyncMock()
#     mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
#     mock_openai_client.return_value = mock_client
    
#     # 創建請求
#     brick = OpenAIGPTBrick()
#     request = LLMRequest(
#         prompt="Test prompt",
#         temperature=0.7,
#         context=[Context(role="user", content="Previous message")]
#     )
    
#     # 執行請求
#     response = await brick.run_unary(request)

#     # 驗證結果
#     assert response.text == "Test response"
#     assert response.is_final is True
#     assert response.error.code == 0
#     assert response.error.message == "Success"
    
#     # 驗證 API 呼叫參數
#     mock_client.chat.completions.create.assert_called_once()
#     call_kwargs = mock_client.chat.completions.create.call_args.kwargs
#     assert call_kwargs["temperature"] == 0.7
#     assert len(call_kwargs["messages"]) == 2
#     assert call_kwargs["messages"][0]["role"] == "user"
#     assert call_kwargs["messages"][0]["content"] == "Previous message"


# @pytest.mark.asyncio
# async def test_output_streaming_handler(mock_api_key, mock_openai_client):
#     """測試串流輸出處理"""
#     # 模擬串流回應
#     # Create streaming chunks with proper structure
#     chunks = []
#     for text in ["Stream ", "test ", "response"]:
#         message = ChatCompletionMessage(
#             role="assistant",
#             content=text
#         )
#         choice = Choice(
#             index=0,
#             delta=message,
#             finish_reason=None
#         )
#         chunk = ChatCompletionChunk(
#             id="test",
#             model="gpt-3.5-turbo",
#             object="chat.completion.chunk",
#             created=1234567890,
#             choices=[choice]
#         )
#         chunks.append(chunk)
    
#     # 設置模擬行為
#     mock_client = AsyncMock()
#     mock_client.chat.completions.create = AsyncMock(return_value=chunks)
#     mock_openai_client.return_value = mock_client
    
#     # 創建請求
#     brick = OpenAIGPTBrick()
#     request = LLMRequest(prompt="Stream test")
    
#     # 執行串流請求並收集結果
#     responses = []
#     async for response in brick.run_output_streaming(request):
#         responses.append(response)
    
#     # 驗證結果
#     assert len(responses) == 4  # 3 chunks + 1 final
#     assert responses[0].text == "Stream "
#     assert responses[1].text == "test "
#     assert responses[2].text == "response"
#     assert responses[3].is_final is True
    
#     # 驗證 API 呼叫
#     mock_client.chat.completions.create.assert_called_once()
#     assert mock_client.chat.completions.create.call_args.kwargs["stream"] is True


@pytest.mark.asyncio
async def test_get_service_info(mock_api_key):
    """測試服務資訊"""
    brick = OpenAIGPTBrick()
    info = await brick.run_get_service_info()
    assert info.service_name == "OpenAI GPT Brick"
    assert info.version == "1.0.0"
    assert len(info.models) == 3
    assert "gpt-3.5-turbo" in [m for m in info.models]
    assert "gpt-4" in [m for m in info.models]
    assert "gpt-4o" in [m for m in info.models]


@pytest.mark.asyncio
async def test_api_error_handling(mock_api_key, mock_openai_client):
    """測試 API 錯誤處理"""
    # 模擬 API 錯誤
    mock_client = AsyncMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai_client.return_value = mock_client
    
    brick = OpenAIGPTBrick()
    request = LLMRequest(prompt="Test error")
    # 測試單次請求錯誤
    response = await brick.run_unary(request)
    assert response.error.code == 1
    assert "error" in response.error.message
    
    # 測試串流請求錯誤
    responses = []
    async for resp in brick.run_output_streaming(request):
        responses.append(resp)
    
    assert len(responses) == 1
    assert responses[0].error.code == 1
    assert "error" in responses[0].error.message