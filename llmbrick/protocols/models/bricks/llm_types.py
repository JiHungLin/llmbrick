from dataclasses import dataclass, field
from typing import List, Optional

from .common_types import ErrorDetail

@dataclass
class LLMRequest:
    model_id: str = ""
    prompt: str = ""
    context: List[str] = field(default_factory=list)

@dataclass
class LLMResponse:
    text: str = ""
    tokens: List[str] = field(default_factory=list)
    is_final: bool = False
    error: Optional[ErrorDetail] = None
