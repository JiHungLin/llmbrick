from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .common_types import ErrorDetail

@dataclass
class Document:
    doc_id: str = ""
    title: str = ""
    snippet: str = ""
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComposeRequest:
    input_documents: List[Document] = field(default_factory=list)
    target_format: str = ""
    target_language: str = ""

@dataclass
class ComposeResponse:
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[ErrorDetail] = None

