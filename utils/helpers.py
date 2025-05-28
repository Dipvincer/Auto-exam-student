import logging
from functools import wraps
from typing import Callable, Any
from core.config import Config

def log_execution(logger: logging.Logger = None):
    """
    Декоратор для логирования выполнения функций
    
    :param logger: Логгер для записи (если None, будет использован root logger)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            used_logger = logger or logging.getLogger(func.__module__)
            
            try:
                used_logger.info(f"Начало выполнения {func.__name__}")
                result = func(*args, **kwargs)
                used_logger.info(f"Успешное завершение {func.__name__}")
                return result
            except Exception as e:
                used_logger.error(f"Ошибка в {func.__name__}: {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)
    return logger