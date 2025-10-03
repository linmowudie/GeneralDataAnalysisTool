"""
Src/DataAnalyzer/log_setting.py
日志配置模块

该模块提供日志系统配置功能，统一管理应用的日志格式、
输出路径和日志级别等设置。
"""

import logging
from pathlib import Path

def setup_logging(log_dir: str = "Logs", log_file: str = "app.log", level=logging.DEBUG):
    """
    配置日志系统
    :param log_dir: 日志目录
    :param log_file: 日志文件名
    :param level: 日志级别
    """
    logs_dir = Path(log_dir)
    logs_dir.mkdir(exist_ok=True)

    log_path = logs_dir / log_file

    # 避免重复添加 handler
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            filename=log_path,
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            encoding='utf-8'  # 防止中文乱码
        )

    # 返回一个命名的 logger（推荐使用模块名）
    return logging.getLogger(__name__)

def setup_module_logging(module_name: str, log_dir: str = "Logs", level=logging.DEBUG):
    """
    为特定模块配置独立的日志文件
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