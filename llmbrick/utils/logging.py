"""
llmbrick.utils.logging
----------------------
Pretty-Loguru 封裝，提供全域 logger、decorator 與動態配置功能。
需先安裝 pretty-loguru: pip install pretty-loguru
"""

import functools
import inspect

from pretty_loguru import create_logger, get_logger as _get_logger, \
    ConfigTemplates, \
    LoggerConfig, \
    EnhancedLogger

config = LoggerConfig(
    level="INFO",
    rotation="1 day",
    retention="7 days"
)

# 預設全域 logger
logger = create_logger("llmbrick", config=config)

def get_logger(name: str = "llmbrick"):
    """
    取得指定名稱的 logger，預設為 llmbrick。
    """
    return _get_logger(name)

def configure_logger(
    name: str = None,
    level: str = None,
    log_path: str = None,
    rotation: str = None,
    retention: str = None,
    compression: str = None,
):
    """
    重新配置 logger，會回傳新的 logger 實體。
    """
    global config
    if name is None:
        config.update(name="llmbrick")
    if level is not None:
        config.update(level=level)
    if log_path is not None:
        config.update(log_path=log_path)
    if rotation is not None:
        config.update(rotation=rotation)
    if retention is not None:
        config.update(retention=retention)
    if compression is not None:
        config.update(compression=compression)


def apply_template(name: str = "llmbrick", template: str = "production"):
    """
    使用 ConfigTemplates 內建模板建立 logger。
    template: "development" | "production" | "testing" | "debug" | "performance" | "minimal"
    """
    templates = {
        "development": ConfigTemplates.development,
        "production": ConfigTemplates.production,
        "testing": ConfigTemplates.testing,
        "debug": ConfigTemplates.debug,
        "performance": ConfigTemplates.performance,
        "minimal": ConfigTemplates.minimal,
        "daily": ConfigTemplates.daily,
        "hourly": ConfigTemplates.hourly,
        "minute": ConfigTemplates.minute,
        "weekly": ConfigTemplates.weekly,
        "monthly": ConfigTemplates.monthly,
    }
    if template not in templates:
        raise ValueError(f"未知的模板名稱: {template}")
    config = templates[template]()
    global logger
    logger = config.apply_to(name)
    return logger

def log_function(
    _func=None,
    *,
    logger_instance=None,
    log_input=True,
    log_output=True,
    log_exception=True,
    level="info",
    service_name=None
):
    """
    Decorator: 自動 log 函式的輸入、輸出、例外。
    支援 async/sync 函式。
    service_name: 於 log 訊息前加上 [service_name] 標籤
    """
    def decorator_log_function(func):
        is_async = inspect.iscoroutinefunction(func)
        log: EnhancedLogger = logger_instance or logger
        prefix = f"[{service_name}] " if service_name else ""
        log_method = getattr(log, str(level).lower(), None)
        if not callable(log_method):
            log_method = log.info
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if log_input:
                log_method(f"{prefix}[{func.__name__}] input: args={args}, kwargs={kwargs}")
            try:
                result = await func(*args, **kwargs)
                if log_output:
                    log_method(f"{prefix}[{func.__name__}] output: {result}")
                return result
            except Exception as e:
                if log_exception:
                    log.error(f"{prefix}[{func.__name__}] exception: {e}", exc_info=True)
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if log_input:
                log_method(f"{prefix}[{func.__name__}] input: args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                if log_output:
                    log_method(f"{prefix}[{func.__name__}] output: {result}")
                return result
            except Exception as e:
                if log_exception:
                    log.error(f"{prefix}[{func.__name__}] exception: {e}", exc_info=True)
                raise

        return async_wrapper if is_async else sync_wrapper

    if _func is None:
        return decorator_log_function
    else:
        return decorator_log_function(_func)

# =========================
# Decorator 使用範例
# =========================

# 同步函式範例
# from llmbrick.utils.logging import log_function
#
# @log_function(service_name="user-service")
# def add(x, y):
#     return x + y
#
# add(1, 2)
#
# 非同步函式範例
# @log_function(service_name="async-service", level="debug")
# async def async_add(x, y):
#     return x + y
#
# import asyncio
# asyncio.run(async_add(3, 4))