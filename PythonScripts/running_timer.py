import time
import logging
import functools
import sys
import os
from pathlib import Path
from typing import Any, Callable

def _setup_module_logging(module_name: str, log_dir: str = "Logs", level=logging.DEBUG):
    """
    为特定模块配置独立的日志文件（内部函数）
    :param module_name: 模块名称
    :param log_dir: 日志目录
    :param level: 日志级别
    :return: 配置好的logger
    """
    logs_dir = Path(log_dir)
    logs_dir.mkdir(exist_ok=True)

    # 为模块创建独立的日志文件
    log_file = f"{module_name}.log"
    log_path = logs_dir / log_file

    # 创建独立的logger
    logger = logging.getLogger(module_name)
    logger.setLevel(level)

    # 避免重复添加handler
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# 为running_timer模块创建独立的日志记录器
logger = _setup_module_logging("running_timer")

def run_timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    装饰器：用于测量函数执行时间并记录日志
    
    Args:
        func: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            logger.info(f"{func.__name__} 执行耗时: {elapsed_time:.4f} 秒")
    return wrapper