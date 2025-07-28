from dataclasses import dataclass, field
from typing import List, Optional
from .common_types import ErrorDetail

@dataclass
class GuardRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

@dataclass
class GuardResult:
    is_attack: bool = False
    confidence: float
    detail: str = ""

@dataclass
class GuardResponse:
    results: List[GuardResult] = field(default_factory=list)
    error: Optional[ErrorDetail] = None

