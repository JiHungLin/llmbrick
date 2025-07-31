from enum import Enum, unique
from typing import Any, Optional


@unique
class ErrorCode(Enum):
    # 通用錯誤
    UNKNOWN_ERROR = 1000
    CONFIG_ERROR = 1100
    MODEL_ERROR = 1200
    EXTERNAL_SERVICE_ERROR = 1300
    VALIDATION_ERROR = 1400
    # 可依需求擴充更多錯誤代碼


class LLMBrickException(Exception):
    """
    框架基礎異常類別，所有自訂異常皆應繼承此類。
    """

    def __init__(
        self,
        code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        message: Optional[str] = None,
        detail: Optional[Any] = None,
    ):
        self.code = code
        self.message = message or code.name
        self.detail = detail
        super().__init__(f"[{self.code.value}] {self.message}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_code": self.code.value,
            "error_name": self.code.name,
            "message": self.message,
            "detail": self.detail,
        }


class ConfigException(LLMBrickException):
    def __init__(self, message: Optional[str] = None, detail: Optional[Any] = None):
        super().__init__(ErrorCode.CONFIG_ERROR, message, detail)


class ModelException(LLMBrickException):
    def __init__(self, message: Optional[str] = None, detail: Optional[Any] = None):
        super().__init__(ErrorCode.MODEL_ERROR, message, detail)


class ExternalServiceException(LLMBrickException):
    def __init__(self, message: Optional[str] = None, detail: Optional[Any] = None):
        super().__init__(ErrorCode.EXTERNAL_SERVICE_ERROR, message, detail)


class ValidationException(LLMBrickException):
    def __init__(self, message: Optional[str] = None, detail: Optional[Any] = None):
        super().__init__(ErrorCode.VALIDATION_ERROR, message, detail)
