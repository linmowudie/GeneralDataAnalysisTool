"""
自定义异常类，便于上层系统捕获和处理
"""

class VisualizationError(Exception):
    """
    可视化模块基础异常类
    """
    pass


class DataValidationError(VisualizationError):
    """
    数据验证异常
    """
    pass


class ModelNotSupportedError(VisualizationError):
    """
    模型不支持异常
    """
    pass


class ChartNotSupportedError(VisualizationError):
    """
    图表类型不支持异常
    """
    pass