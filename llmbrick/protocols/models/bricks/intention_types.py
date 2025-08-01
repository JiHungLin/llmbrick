from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from google.protobuf.json_format import MessageToDict

from llmbrick.protocols.grpc.intention import intention_pb2
from llmbrick.protocols.models.bricks.common_types import ErrorDetail


@dataclass
class IntentionRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(
        cls, model: intention_pb2.IntentionRequest
    ) -> "IntentionRequest":
        return cls(
            text=model.text,
            client_id=model.client_id,
            session_id=model.session_id,
            request_id=model.request_id,
            source_language=model.source_language,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentionRequest":
        return cls(
            text=data.get("text", ""),
            client_id=data.get("client_id", ""),
            session_id=data.get("session_id", ""),
            request_id=data.get("request_id", ""),
            source_language=data.get("source_language", ""),
        )


@dataclass
class IntentionResult:
    intent_category: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentionResult":
        return cls(
            intent_category=data.get("intent_category", ""),
            confidence=data.get("confidence", 0.0),
        )


@dataclass
class IntentionResponse:
    results: List[IntentionResult] = field(default_factory=list)
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(
        cls, model: intention_pb2.IntentionResponse
    ) -> "IntentionResponse":
        results = [
            IntentionResult.from_dict(MessageToDict(result, preserving_proto_field_name=True)) for result in model.results
        ]
        error = (
            ErrorDetail.from_dict(MessageToDict(model.error, preserving_proto_field_name=True)) if model.error else None
        )
        return cls(results=results, error=error)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentionResponse":
        results_data = data.get("results", [])
        results = [IntentionResult.from_dict(result) for result in results_data]
        error_data = data.get("error")
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(results=results, error=error)
