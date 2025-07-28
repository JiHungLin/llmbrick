from dataclasses import dataclass
from typing import Optional
from .common_types import ErrorDetail

@dataclass
class RectifyRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

@dataclass
class RectifyResponse:
    corrected_text: str = ""
    error: Optional[ErrorDetail] = None

