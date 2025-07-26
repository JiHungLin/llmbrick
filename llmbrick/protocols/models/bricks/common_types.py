from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class ErrorDetail:
    code: int
    message: str
    detail: Optional[str] = None

@dataclass
class ModelInfo:
    model_id: str
    version: str
    supported_languages: List[str] = field(default_factory=list)
    support_streaming: bool = False
    description: str = ""
@dataclass
class CommonRequest:
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CommonResponse:
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[ErrorDetail] = None

@dataclass
class ServiceInfoRequest:
    pass

@dataclass
class ServiceInfoResponse:
    service_name: str = ""
    version: str = ""
    models: List[ModelInfo] = field(default_factory=list)
    error: Optional[ErrorDetail] = None