from dataclasses import dataclass
from typing import Optional

from .common_types import ErrorDetail

@dataclass
class TextRequest:
    text: str = ""
    language: str = ""

@dataclass
class TextResponse:
    corrected_text: str = ""
    error: Optional[ErrorDetail] = None

