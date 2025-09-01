import functools
import inspect
import time
from llmbrick.utils.logging import logger


def measure_time(func):
    """
    Decorator: Measure function execution time and log it.
    Supports both sync and async functions.
    """
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start
                logger.info(
                    f"[metrics] {func.__module__}.{func.__name__} execution " +
                    f"time: {elapsed:.6f} seconds"
                )

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start
                logger.info(
                    f"[metrics] {func.__module__}.{func.__name__} execution " +
                    f"time: {elapsed:.6f} seconds"
                )

        return sync_wrapper


def measure_memory(func):
    """
    Decorator: Measure function memory usage (RSS diff in MB) and log it.
    Requires 'psutil' package. Supports both sync and async functions.
    """
    import psutil

    process = psutil.Process()
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            mem_before = process.memory_info().rss
            result = await func(*args, **kwargs)
            mem_after = process.memory_info().rss
            mem_diff_mb = (mem_after - mem_before) / (1024 * 1024)
            logger.info(
                f"[metrics] {func.__module__}.{func.__name__} memory " +
                f"usage diff: {mem_diff_mb:.6f} MB"
            )
            return result

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            mem_before = process.memory_info().rss
            result = func(*args, **kwargs)
            mem_after = process.memory_info().rss
            mem_diff_mb = (mem_after - mem_before) / (1024 * 1024)
            logger.info(
                f"[metrics] {func.__module__}.{func.__name__} memory " +
                f"usage diff: {mem_diff_mb:.6f} MB"
            )
            return result

        return sync_wrapper


def measure_peak_memory(func):
    """
    Decorator: Measure peak memory usage (in MB) during \n
    function execution using tracemalloc.
    Supports both sync and async functions.
    """
    import tracemalloc

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracemalloc.start()
            try:
                result = await func(*args, **kwargs)
                current, peak = tracemalloc.get_traced_memory()
                peak_mb = peak / (1024 * 1024)
                logger.info(
                    f"[metrics] {func.__module__}.{func.__name__} peak " +
                    f"memory usage: {peak_mb:.6f} MB (tracemalloc)"
                )
                return result
            finally:
                tracemalloc.stop()

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracemalloc.start()
            try:
                result = func(*args, **kwargs)
                current, peak = tracemalloc.get_traced_memory()
                peak_mb = peak / (1024 * 1024)
                logger.info(
                    f"[metrics] {func.__module__}.{func.__name__} peak " +
                    f"memory usage: {peak_mb:.6f} MB (tracemalloc)"
                )
                return result
            finally:
                tracemalloc.stop()

        return sync_wrapper


# Future: add call count, exception count, etc.
