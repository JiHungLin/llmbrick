from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    """
    單則對話訊息，符合 OpenAI/Perplexity SSE API 格式
    One message in the conversation, compatible with mainstream SSE API.
    """

    role: str = Field(
        ...,
        description="訊息角色，如 'system', 'user', 'assistant' (Message role: 'system', 'user', 'assistant', etc.)",
    )
    content: str = Field(..., description="訊息內容 (Message content)")

    model_config = ConfigDict(
        extra="forbid",  # 禁止額外欄位
        populate_by_name=True,  # 允許使用欄位名稱進行填充
        json_schema_extra={
            "example": {"role": "user", "content": "What is the weather like today?"}
        },
    )


class ConversationSSERequest(BaseModel):
    """
    SSE 專用對話請求模型，適用於 FastAPI，參考主流 LLM API 並增加 session_id 欄位
    SSE conversation request model for FastAPI, based on mainstream LLM API with additional session_id field.
    """

    model: str = Field(
        ..., description="指定模型名稱 (Model name, e.g. 'gpt-4o', 'sonar')"
    )
    messages: List[Message] = Field(..., description="訊息陣列 (List of messages)")
    stream: bool = Field(
        True, description="是否啟用串流 (Enable SSE streaming, must be True)"
    )
    client_id: Optional[str] = Field(
        None, alias="clientId", description="客戶端識別碼 (Client ID, optional)"
    )
    session_id: str = Field(
        ...,
        alias="sessionId",
        description="對話 session id，標記本次對話所屬 (Session id for conversation tracking)",
    )
    temperature: Optional[float] = Field(
        None, description="回應多樣性 (Response diversity)"
    )
    max_tokens: Optional[int] = Field(
        None,
        alias="maxTokens",
        description="生成最大 token 數 (Max tokens to generate)",
    )
    tools: Optional[List[Any]] = Field(
        None, description="工具列表 (Tools, for function calling, optional)"
    )
    tool_choice: Optional[Any] = Field(
        None, alias="toolChoice", description="工具選擇 (Tool choice, optional)"
    )
    source_language: Optional[str] = Field(
        None, alias="sourceLanguage", description="源語言 (Source language, optional)"
    )

    model_config = ConfigDict(
        extra="forbid",  # 禁止額外欄位
        populate_by_name=True,  # 允許使用欄位名稱進行填充
        json_schema_extra={
            "example": {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is the weather like today?"},
                ],
                "stream": True,
                "clientId": "client123",
                "sessionId": "1234567890",
                "temperature": 0.7,
                "maxTokens": 100,
            }
        },
    )


class SSEContext(BaseModel):
    """
    SSE Response context，包含對話識別資訊
    Context for SSE response, includes conversation/session info.
    """

    conversation_id: Optional[str] = Field(
        None, alias="conversationId", description="對話ID (Conversation ID)"
    )
    cursor: Optional[str] = Field(None, description="游標 (Cursor for streaming)")

    model_config = ConfigDict(
        extra="forbid",  # 禁止額外欄位
        populate_by_name=True,  # 允許使用欄位名稱進行填充
        json_schema_extra={
            "example": {"conversationId": "1234567890", "cursor": "abcdefg12345"}
        },
    )


class SSEResponseMetadata(BaseModel):
    """
    SSE Response metadata，擴充用
    Metadata for SSE response, for extensibility.
    """

    search_results: Optional[Any] = Field(
        None, alias="searchResults", description="搜尋結果 (Search results, optional)"
    )
    attachments: Optional[Any] = Field(None, description="附件 (Attachments, optional)")
    # 可依需求擴充更多欄位

    model_config = ConfigDict(
        extra="forbid",  # 禁止額外欄位
        populate_by_name=True,  # 允許使用欄位名稱進行填充
        json_schema_extra={
            "example": {
                "searchResults": {"results": ["result1", "result2"]},
                "attachments": [
                    {"type": "image", "url": "http://example.com/image.jpg"}
                ],
            }
        },
    )


class ConversationResponseProgressEnum(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    ERROR = "ERROR"

class ConversationSSEResponse(BaseModel):
    """
    SSE 專用對話回應模型，對應主流 LLM SSE Response 格式
    SSE conversation response model, compatible with mainstream LLM SSE response format.
    """

    id: str = Field(..., description="唯一識別碼 (Unique chunk/message ID)")
    type: str = Field(
        ...,
        description="資料類型，如 'text', 'meta', 'done' (Type: 'text', 'meta', 'done')",
    )
    model: Optional[str] = Field(
        None, description="回應的模型名稱 (Model name, optional)"
    )
    text: Optional[str] = Field(
        None, description="本次串流新文本 (Streamed text chunk, optional)"
    )
    progress: ConversationResponseProgressEnum = Field(
        ...,
        description="進度狀態，如 'IN_PROGRESS', 'DONE' (Progress: 'IN_PROGRESS', 'DONE')",
    )
    context: Optional[SSEContext] = Field(
        None, description="上下文資訊 (Context info, optional)"
    )
    metadata: Optional[SSEResponseMetadata] = Field(
        None, description="輔助資訊 (Metadata, optional)"
    )

    model_config = ConfigDict(
        extra="forbid",  # 禁止額外欄位
        populate_by_name=True,  # 允許使用欄位名稱進行填充
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": "1",
                "type": "text",
                "model": "gpt-4o",
                "text": "Hello, this is a streaming response.",
                "progress": "IN_PROGRESS",
                "context": {"conversationId": "1234567890", "cursor": "abcdefg12345"},
                "metadata": {
                    "searchResults": {"results": ["result1", "result2"]},
                    "attachments": [
                        {"type": "image", "url": "http://example.com/image.jpg"}
                    ],
                },
            }
        },
    )
