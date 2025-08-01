from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from google.protobuf.json_format import MessageToDict

from llmbrick.protocols.grpc.translate import translate_pb2
from llmbrick.protocols.models.bricks.common_types import ErrorDetail


@dataclass
class TranslateRequest:
    text: str = ""
    model_id: str = ""
    target_language: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(
        cls, model: translate_pb2.TranslateRequest
    ) -> "TranslateRequest":
        return cls(
            text=model.text,
            model_id=model.model_id,
            target_language=model.target_language,
            client_id=model.client_id,
            session_id=model.session_id,
            request_id=model.request_id,
            source_language=model.source_language,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranslateRequest":
        return cls(
            text=data.get("text", ""),
            model_id=data.get("model_id", ""),
            target_language=data.get("target_language", ""),
            client_id=data.get("client_id", ""),
            session_id=data.get("session_id", ""),
            request_id=data.get("request_id", ""),
            source_language=data.get("source_language", ""),
        )


@dataclass
class TranslateResponse:
    text: str = ""
    tokens: List[str] = field(default_factory=list)
    language_code: str = ""
    is_final: bool = False
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(
        cls, model: translate_pb2.TranslateResponse
    ) -> "TranslateResponse":
        error = (
            ErrorDetail.from_dict(MessageToDict(model.error, preserving_proto_field_name=True)) if model.error else None
        )
        return cls(
            text=model.text,
            tokens=model.tokens,
            language_code=model.language_code,
            is_final=model.is_final,
            error=error,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranslateResponse":
        error_data = data.get("error")
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(
            text=data.get("text", ""),
            tokens=data.get("tokens", []),
            language_code=data.get("language_code", ""),
            is_final=data.get("is_final", False),
            error=error,
        )
