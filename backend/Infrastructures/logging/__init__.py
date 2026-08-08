"""backend.Infrastructures.logging：日志配置（实现在 log_setting.py，原 Engine/Configs/log_setting 迁入）"""
from .log_setting import setup_logging, setup_module_logging, get_component_logger

__all__ = ["setup_logging", "setup_module_logging", "get_component_logger"]
