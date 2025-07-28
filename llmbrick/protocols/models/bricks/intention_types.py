from dataclasses import dataclass, field
from typing import List, Optional
from .common_types import ErrorDetail

@dataclass
class IntentionRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

@dataclass
class IntentionResult:
    intent_category: str = ""
    confidence: float

@dataclass
class IntentionResponse:
    results: List[IntentionResult] = field(default_factory=list)
    error: Optional[ErrorDetail] = None

