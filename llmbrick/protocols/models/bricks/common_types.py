from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

@dataclass
class ErrorDetail:
    code: int
    message: str
    detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorDetail':
        return cls(
            code=data.get('code', 0),
            message=data.get('message', ''),
            detail=data.get('detail')
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelInfo':
        return cls(
            model_id=data.get('model_id', ''),
            version=data.get('version', ''),
            supported_languages=data.get('supported_languages', []),
            support_streaming=data.get('support_streaming', False),
            description=data.get('description', '')
        )
@dataclass
class CommonRequest:
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CommonResponse:
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommonResponse':
        error_data = data.get('error')
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(
            data=data.get('data', {}),
            error=error
        )

@dataclass
class ServiceInfoRequest:
    pass

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInfoRequest':
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInfoResponse':
        models_data = data.get('models', [])
        models = [ModelInfo.from_dict(model) for model in models_data]
        error_data = data.get('error')
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(
            service_name=data.get('service_name', ''),
            version=data.get('version', ''),
            models=models,
            error=error
        )