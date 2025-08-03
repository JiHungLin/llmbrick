from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from google.protobuf.json_format import MessageToDict

from llmbrick.protocols.grpc.guard import guard_pb2
from llmbrick.protocols.models.bricks.common_types import ErrorDetail


@dataclass
class GuardRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_pb2_model(cls, model: guard_pb2.GuardRequest) -> "GuardRequest":
        return cls(
            text=model.text,
            client_id=model.client_id,
            session_id=model.session_id,
            request_id=model.request_id,
            source_language=model.source_language,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardRequest":
        return cls(
            text=data.get("text", ""),
            client_id=data.get("client_id", ""),
            session_id=data.get("session_id", ""),
            request_id=data.get("request_id", ""),
            source_language=data.get("source_language", ""),
        )


@dataclass
class GuardResult:
    is_attack: bool = False
    confidence: float = 0.0
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: guard_pb2.GuardResult) -> "GuardResult":
        return cls(
            is_attack=model.is_attack, confidence=model.confidence, detail=model.detail
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardResult":
        return cls(
            is_attack=data.get("is_attack", False),
            confidence=data.get("confidence", 0.0),
            detail=data.get("detail", ""),
        )


@dataclass
class GuardResponse:
    results: List[GuardResult] = field(default_factory=list)
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: guard_pb2.GuardResponse) -> "GuardResponse":
        results = [GuardResult.from_pb2_model(result) for result in model.results]
        error = (
            ErrorDetail.from_dict(MessageToDict(model.error, preserving_proto_field_name=True)) if model.error else None
        )
        return cls(results=results, error=error)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardResponse":
        results_data = data.get("results", [])
        results = [GuardResult.from_dict(result) for result in results_data]
        error_data = data.get("error")
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(results=results, error=error)
