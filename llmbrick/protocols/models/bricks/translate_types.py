from dataclasses import dataclass, field
from typing import List, Optional
from .common_types import ErrorDetail

@dataclass
class TranslateRequest:
    text: str = ""
    model_id: str = ""
    target_language: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

@dataclass
class TranslateResponse:
    text: str = ""
    tokens: List[str] = field(default_factory=list)
    language_code: str = ""
    is_final: bool = False
    error: Optional[ErrorDetail] = None

