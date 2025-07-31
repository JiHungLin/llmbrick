import pytest
from llmbrick.utils import logging as logmod

def test_log_function_sync(monkeypatch):
    logs = []
    class DummyLogger:
        def info(self, msg): logs.append(msg)
        def error(self, msg, exc_info=None): logs.append(msg)
    monkeypatch.setattr(logmod, "logger", DummyLogger())

    @logmod.log_function(service_name="svc", level="info")
    def add(x, y): return x + y

    assert add(1, 2) == 3
    assert any("input" in m for m in logs)
    assert any("output" in m for m in logs)

def test_log_function_exception(monkeypatch):
    logs = []
    class DummyLogger:
        def info(self, msg): pass
        def error(self, msg, exc_info=None): logs.append(msg)
    monkeypatch.setattr(logmod, "logger", DummyLogger())

    @logmod.log_function(service_name="svc", level="info")
    def fail(): raise ValueError("fail")
    with pytest.raises(ValueError):
        fail()
    assert any("exception" in m for m in logs)