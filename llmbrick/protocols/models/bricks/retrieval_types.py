from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .common_types import ErrorDetail

@dataclass
class RetrievalRequest:
    query: str = ""
    max_results: int = 0
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

@dataclass
class Document:
    doc_id: str = ""
    title: str = ""
    snippet: str = ""
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalResponse:
    documents: List[Document] = field(default_factory=list)
    error: Optional[ErrorDetail] = None