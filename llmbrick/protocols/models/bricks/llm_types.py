from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from google.protobuf.json_format import MessageToDict

from llmbrick.protocols.grpc.llm import llm_pb2
from llmbrick.protocols.models.bricks.common_types import ErrorDetail


@dataclass
class Context:
    role: str = ""
    content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Context":
        return cls(role=data.get("role", ""), content=data.get("content", ""))


@dataclass
class LLMRequest:
    temperature: float = 0.7
    model_id: str = ""
    prompt: str = ""
    context: List[Context] = field(default_factory=list)
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""
    max_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: llm_pb2.LLMRequest) -> "LLMRequest":
        context_data = [MessageToDict(ctx, preserving_proto_field_name=True) for ctx in model.context]
        context = [Context.from_dict(ctx) for ctx in context_data]
        return cls(
            temperature=model.temperature,
            model_id=model.model_id,
            prompt=model.prompt,
            context=context,
            client_id=model.client_id,
            session_id=model.session_id,
            request_id=model.request_id,
            source_language=model.source_language,
            max_tokens=model.max_tokens,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMRequest":
        context_data = data.get("context", [])
        context = [Context.from_dict(ctx) for ctx in context_data]
        return cls(
            temperature=data.get("temperature", 0.7),
            model_id=data.get("model_id", ""),
            prompt=data.get("prompt", ""),
            context=context,
            client_id=data.get("client_id", ""),
            session_id=data.get("session_id", ""),
            request_id=data.get("request_id", ""),
            source_language=data.get("source_language", ""),
            max_tokens=data.get("max_tokens", 0),
        )


@dataclass
class LLMResponse:
    text: str = ""
    tokens: List[str] = field(default_factory=list)
    is_final: bool = False
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: llm_pb2.LLMResponse) -> "LLMResponse":
        error = (
            ErrorDetail.from_dict(MessageToDict(model.error, preserving_proto_field_name=True)) if model.error else None
        )
        return cls(
            text=model.text,
            tokens=list(model.tokens),
            is_final=model.is_final,
            error=error,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMResponse":
        error_data = data.get("error")
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(
            text=data.get("text", ""),
            tokens=data.get("tokens", []),
            is_final=data.get("is_final", False),
            error=error,
        )
