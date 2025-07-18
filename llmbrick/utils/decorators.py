import asyncio
from functools import wraps
from typing import Type, Callable
from ..core.brick import BaseBrick

def brick_plugin(brick_class: Type[BaseBrick]):
    """裝飾器，用於註冊Brick插件"""
    def decorator(cls):
        # 註冊邏輯
        cls._brick_class = brick_class
        return cls
    return decorator

def async_retry(max_retries: int = 3, delay: float = 1.0):
    """異步重試裝飾器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(delay)
        return wrapper
    return decorator