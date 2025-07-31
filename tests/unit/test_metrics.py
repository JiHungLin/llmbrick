import logging

import pytest

from llmbrick.utils.metrics import measure_memory, measure_peak_memory, measure_time

# 設定 logging 輸出到 console
logging.basicConfig(level=logging.INFO)


def test_measure_time_sync(caplog):
    @measure_time
    def foo(x):
        return x * 2

    with caplog.at_level(logging.INFO):
        result = foo(3)
    assert result == 6
    assert any("execution time" in r.message for r in caplog.records)


def test_measure_memory_sync(caplog):
    @measure_memory
    def foo(x):
        a = [0] * 10000  # noqa: F841 占用一點記憶體
        return x + 1

    with caplog.at_level(logging.INFO):
        result = foo(5)
    assert result == 6
    assert any("memory usage diff" in r.message for r in caplog.records)


def test_measure_peak_memory_sync(caplog):
    @measure_peak_memory
    def foo(x):
        a = [0] * 10000  # noqa: F841 占用一點記憶體
        return x - 1

    with caplog.at_level(logging.INFO):
        result = foo(7)
    assert result == 6
    assert any("peak memory usage" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_measure_time_async(caplog):
    @measure_time
    async def foo(x):
        return x * 3

    with caplog.at_level(logging.INFO):
        result = await foo(4)
    assert result == 12
    assert any("execution time" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_measure_memory_async(caplog):
    @measure_memory
    async def foo(x):
        a = [0] * 10000  # noqa: F841 占用一點記憶體
        return x + 2

    with caplog.at_level(logging.INFO):
        result = await foo(8)
    assert result == 10
    assert any("memory usage diff" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_measure_peak_memory_async(caplog):
    @measure_peak_memory
    async def foo(x):
        a = [0] * 10000  # noqa: F841 占用一點記憶體
        return x - 2

    with caplog.at_level(logging.INFO):
        result = await foo(9)
    assert result == 7
    assert any("peak memory usage" in r.message for r in caplog.records)
