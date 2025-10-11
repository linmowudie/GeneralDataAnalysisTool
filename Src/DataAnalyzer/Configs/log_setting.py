"""
Src/DataAnalyzer/log_setting.py
日志配置模块

该模块提供日志系统配置功能，统一管理应用的日志格式、
输出路径和日志级别等设置。
"""

import logging
from pathlib import Path
from typing import Optional
import sys

# 定义不同组件的日志文件名
LOG_FILES = {
    'backend': 'backend.log',
    'api': 'api.log',
    'frontend': 'frontend.log',
    'app': 'app.log'  # 默认/综合日志
}

def setup_logging(component: str = 'app', log_dir: str = "Logs", level=logging.INFO):
    """
    配置日志系统
    :param component: 组件名称 (backend, api, frontend, app)
    :param log_dir: 日志目录
    :param level: 日志级别
    """
    logs_dir = Path(log_dir)
    logs_dir.mkdir(exist_ok=True)

    log_file = LOG_FILES.get(component, LOG_FILES['app'])
    log_path = logs_dir / log_file

    # 避免重复添加 handler
    logger = logging.getLogger()
    if not logger.hasHandlers():
        logging.basicConfig(
            filename=log_path,
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            encoding='utf-8'  # 防止中文乱码
        )
        # 过滤第三方库的详细日志
        _filter_third_party_logs(level)

    return logging.getLogger(__name__)

def _filter_third_party_logs(base_level):
    """
    过滤第三方库的日志，避免记录过多无用信息
    """
    # 将一些第三方库的日志级别调高，只记录警告及以上级别
    third_party_loggers = [
        'watchfiles', 'asyncio', 'python_multipart', 'MARKDOWN'
    ]
    
    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

def setup_module_logging(module_name: str, log_dir: str = "Logs", level=logging.INFO, component: str = 'app'):
    """
    为特定模块配置独立的日志文件
    :param module_name: 模块名称
    :param log_dir: 日志目录
    :param level: 日志级别
    :param component: 组件名称 (backend, api, frontend, app)
    :return: 配置好的logger
    """
    logs_dir = Path(log_dir)
    logs_dir.mkdir(exist_ok=True)

    # 为模块创建独立的日志文件
    log_file = f"{module_name}.log"
    if component != 'app':
        log_file = f"{component}_{module_name}.log"
    
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
        # 过滤第三方库日志
        _filter_third_party_logs(level)

    return logger

def get_component_logger(component: str, name: Optional[str] = None):
    """
    获取特定组件的logger
    :param component: 组件名称 (backend, api, frontend)
    :param name: logger名称
    :return: 配置好的logger
    """
    logs_dir = Path("Logs")
    logs_dir.mkdir(exist_ok=True)
    
    log_file = LOG_FILES.get(component, LOG_FILES['app'])
    log_path = logs_dir / log_file
    
    logger_name = name if name else component
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加handler
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # 过滤第三方库日志
        _filter_third_party_logs(logging.INFO)
    
    return logger