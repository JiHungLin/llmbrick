from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from google.protobuf.json_format import MessageToDict

from llmbrick.protocols.grpc.rectify import rectify_pb2
from llmbrick.protocols.models.bricks.common_types import ErrorDetail


@dataclass
class RectifyRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: rectify_pb2.RectifyRequest) -> "RectifyRequest":
        return cls(
            text=model.text,
            client_id=model.client_id,
            session_id=model.session_id,
            request_id=model.request_id,
            source_language=model.source_language,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RectifyRequest":
        return cls(
            text=data.get("text", ""),
            client_id=data.get("client_id", ""),
            session_id=data.get("session_id", ""),
            request_id=data.get("request_id", ""),
            source_language=data.get("source_language", ""),
        )


@dataclass
class RectifyResponse:
    corrected_text: str = ""
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: rectify_pb2.RectifyResponse) -> "RectifyResponse":
        error = (
            ErrorDetail.from_dict(MessageToDict(model.error, preserving_proto_field_name=True)) if model.error else None
        )
        return cls(corrected_text=model.corrected_text, error=error)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RectifyResponse":
        error_data = data.get("error")
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(corrected_text=data.get("corrected_text", ""), error=error)
