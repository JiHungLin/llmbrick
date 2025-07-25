from dataclasses import dataclass, field
from typing import List, Optional

from .common_types import ErrorDetail

@dataclass
class IntentionRequest:
    text: str = ""

@dataclass
class IntentionResult:
    intent_category: str = ""
    confidence: float
    is_attack: bool = False
    action: str = ""

@dataclass
class IntentionResponse:
    results: List[IntentionResult] = field(default_factory=list)
    error: Optional[ErrorDetail] = None

