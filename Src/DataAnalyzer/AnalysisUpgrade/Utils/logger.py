"""
日志工具
"""

import logging
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    
    参数:
        name (str): 日志记录器名称
        level (int): 日志级别
        
    返回:
        logging.Logger: 日志记录器实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果记录器已经有处理器，则直接返回
    if logger.handlers:
        return logger
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(console_handler)
    
    return logger