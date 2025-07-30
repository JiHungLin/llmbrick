from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from llmbrick.protocols.models.bricks.common_types import ErrorDetail

@dataclass
class RectifyRequest:
    text: str = ""
    client_id: str = ""
    session_id: str = ""
    request_id: str = ""
    source_language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RectifyRequest':
        return cls(
            text=data.get('text', ''),
            client_id=data.get('client_id', ''),
            session_id=data.get('session_id', ''),
            request_id=data.get('request_id', ''),
            source_language=data.get('source_language', '')
        )

@dataclass
class RectifyResponse:
    corrected_text: str = ""
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RectifyResponse':
        error_data = data.get('error')
        error = ErrorDetail.from_dict(error_data) if error_data else None
        return cls(
            corrected_text=data.get('corrected_text', ''),
            error=error
        )

