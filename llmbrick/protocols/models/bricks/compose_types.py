from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from google.protobuf.json_format import MessageToDict

from llmbrick.protocols.grpc.compose import compose_pb2
from llmbrick.protocols.models.bricks.common_types import ErrorDetail


@dataclass
class Document:
    doc_id: str = ""
    title: str = ""
    snippet: str = ""
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        return cls(
            doc_id=data.get("doc_id", ""),
            title=data.get("title", ""),
            snippet=data.get("snippet", ""),
            score=data.get("score", 0.0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ComposeRequest:
    input_documents: List[Document] = field(default_factory=list)
    target_format: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: compose_pb2.ComposeRequest) -> "ComposeRequest":
        docs_data = [MessageToDict(doc, preserving_proto_field_name=True) for doc in model.input_documents]
        input_documents = [Document.from_dict(doc) for doc in docs_data]
        return cls(
            input_documents=input_documents,
            target_format=model.target_format,
            client_id=model.client_id,
            session_id=model.session_id,
            request_id=model.request_id,
            source_language=model.source_language,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComposeRequest":
        docs_data = data.get("input_documents", [])
        input_documents = [Document.from_dict(doc) for doc in docs_data]
        return cls(
            input_documents=input_documents,
            target_format=data.get("target_format", ""),
            client_id=data.get("client_id", ""),
            session_id=data.get("session_id", ""),
            request_id=data.get("request_id", ""),
            source_language=data.get("source_language", ""),
        )


@dataclass
class ComposeResponse:
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: compose_pb2.ComposeResponse) -> "ComposeResponse":
        output_dict = MessageToDict(model.output, preserving_proto_field_name=True) if model.output else {}
        error = (
            ErrorDetail.from_dict(MessageToDict(model.error, preserving_proto_field_name=True)) if model.error else None
        )
        return cls(output=output_dict, error=error)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComposeResponse":
        error_data = data.get("error")
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(output=data.get("output", {}), error=error)
