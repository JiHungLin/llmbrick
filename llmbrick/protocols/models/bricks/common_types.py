from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from google.protobuf.json_format import MessageToDict

from llmbrick.protocols.grpc.common import common_pb2


@dataclass
class ErrorDetail:
    code: int
    message: str
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: common_pb2.ErrorDetail) -> "ErrorDetail":
        return cls(
            code=model.code,
            message=model.message,
            detail=model.detail,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorDetail":
        return cls(
            code=data.get("code", 0),
            message=data.get("message", ""),
            detail=data.get("detail", ""),
        )


@dataclass
class ModelInfo:
    model_id: str
    version: str
    supported_languages: List[str] = field(default_factory=list)
    support_streaming: bool = False
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        return cls(
            model_id=data.get("model_id", ""),
            version=data.get("version", ""),
            supported_languages=data.get("supported_languages", []),
            support_streaming=data.get("support_streaming", False),
            description=data.get("description", ""),
        )


@dataclass
class CommonRequest:
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: common_pb2.CommonRequest) -> "CommonRequest":
        data = MessageToDict(model.data, preserving_proto_field_name=True)
        return cls(data=data)


@dataclass
class CommonResponse:
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_pb2_model(cls, model: common_pb2.CommonResponse) -> "CommonResponse":
        data = MessageToDict(model.data, preserving_proto_field_name=True)
        error = (
            ErrorDetail.from_dict(MessageToDict(model.error, preserving_proto_field_name=True)) if model.error else None
        )
        return cls(data=data, error=error)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommonResponse":
        error_data = data.get("error")
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(data=data.get("data", {}), error=error)


@dataclass
class ServiceInfoRequest:
    pass

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServiceInfoRequest":
        return cls()


@dataclass
class ServiceInfoResponse:
    service_name: str = ""
    version: str = ""
    models: List[ModelInfo] = field(default_factory=list)
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServiceInfoResponse":
        models_data = data.get("models", [])
        models = [ModelInfo.from_dict(model) for model in models_data]
        error_data = data.get("error")
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(
            service_name=data.get("service_name", ""),
            version=data.get("version", ""),
            models=models,
            error=error,
        )
