from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .common_types import ErrorDetail

@dataclass
class RetrievalRequest:
    query: str = ""
    max_results: int = 0

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

