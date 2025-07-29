from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from .common_types import ErrorDetail

@dataclass
class GuardRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GuardRequest':
        return cls(
            text=data.get('text', ''),
            client_id=data.get('client_id', ''),
            session_id=data.get('session_id', ''),
            request_id=data.get('request_id', ''),
            source_language=data.get('source_language', '')
        )

@dataclass
class GuardResult:
    is_attack: bool = False
    confidence: float = 0.0
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GuardResult':
        return cls(
            is_attack=data.get('is_attack', False),
            confidence=data.get('confidence', 0.0),
            detail=data.get('detail', '')
        )

@dataclass
class GuardResponse:
    results: List[GuardResult] = field(default_factory=list)
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GuardResponse':
        results_data = data.get('results', [])
        results = [GuardResult.from_dict(result) for result in results_data]
        error_data = data.get('error')
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(
            results=results,
            error=error
        )

