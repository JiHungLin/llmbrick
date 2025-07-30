from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from llmbrick.protocols.models.bricks.common_types import ErrorDetail

@dataclass
class RetrievalRequest:
    query: str = ""
    max_results: int = 0
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetrievalRequest':
        return cls(
            query=data.get('query', ''),
            max_results=data.get('max_results', 0),
            client_id=data.get('client_id', ''),
            session_id=data.get('session_id', ''),
            request_id=data.get('request_id', ''),
            source_language=data.get('source_language', '')
        )

@dataclass
class Document:
    doc_id: str = ""
    title: str = ""
    snippet: str = ""
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        return cls(
            doc_id=data.get('doc_id', ''),
            title=data.get('title', ''),
            snippet=data.get('snippet', ''),
            score=data.get('score', 0.0),
            metadata=data.get('metadata', {})
        )

@dataclass
class RetrievalResponse:
    documents: List[Document] = field(default_factory=list)
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetrievalResponse':
        docs_data = data.get('documents', [])
        documents = [Document.from_dict(doc) for doc in docs_data]
        error_data = data.get('error')
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(
            documents=documents,
            error=error
        )