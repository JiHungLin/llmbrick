import pytest
from llmbrick.core.exceptions import (
    ErrorCode,
    LLMBrickException,
    ConfigException,
    ModelException,
    ExternalServiceException,
    ValidationException,
)

def test_llmbrick_exception_default():
    exc = LLMBrickException()
    assert exc.code == ErrorCode.UNKNOWN_ERROR
    assert exc.message == "UNKNOWN_ERROR"
    assert exc.detail is None
    d = exc.to_dict()
    assert d["error_code"] == ErrorCode.UNKNOWN_ERROR.value
    assert d["error_name"] == "UNKNOWN_ERROR"
    assert d["message"] == "UNKNOWN_ERROR"
    assert d["detail"] is None

def test_llmbrick_exception_custom():
    exc = LLMBrickException(ErrorCode.MODEL_ERROR, "fail", {"foo": 1})
    assert exc.code == ErrorCode.MODEL_ERROR
    assert exc.message == "fail"
    assert exc.detail == {"foo": 1}
    d = exc.to_dict()
    assert d["error_code"] == ErrorCode.MODEL_ERROR.value
    assert d["error_name"] == "MODEL_ERROR"
    assert d["message"] == "fail"
    assert d["detail"] == {"foo": 1}

@pytest.mark.parametrize("cls,code", [
    (ConfigException, ErrorCode.CONFIG_ERROR),
    (ModelException, ErrorCode.MODEL_ERROR),
    (ExternalServiceException, ErrorCode.EXTERNAL_SERVICE_ERROR),
    (ValidationException, ErrorCode.VALIDATION_ERROR),
])
def test_custom_exceptions(cls, code):
    exc = cls("msg", {"bar": 2})
    assert isinstance(exc, LLMBrickException)
    assert exc.code == code
    assert exc.message == "msg"
    assert exc.detail == {"bar": 2}
    d = exc.to_dict()
    assert d["error_code"] == code.value
    assert d["error_name"] == code.name
    assert d["message"] == "msg"
    assert d["detail"] == {"bar": 2}