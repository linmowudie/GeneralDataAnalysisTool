"""
Src/DataAnalyzer/VisualizationModule/registry.py
可视化注册表模块

该模块提供一个注册表系统，用于管理和注册各种图表类型的绘制函数，
支持根据不同任务类型和模型名称获取相应的可视化函数。
"""

# visualization/registry.py
from typing import Dict, Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PlotRegistry:
    """绘图函数注册表"""
    
    def __init__(self):
        self._registry = {}
    
    def register(self, task_type: str, model_name: str) -> Callable:
        """注册装饰器"""
        def decorator(func: Callable) -> Callable:
            key = (task_type.lower(), model_name.lower())
            if key in self._registry:
                raise ValueError(f"Plot for {model_name} ({task_type}) already registered")
            self._registry[key] = func
            logger.debug(f"Registered plot function for {model_name} ({task_type})")
            return func
        return decorator
    
    def get_plot_function(self, task_type: str, model_name: str) -> Optional[Callable]:
        """获取绘图函数"""
        logger.debug(f"Attempting to get plot function for {model_name} ({task_type})")
        logger.debug(f"Registry contents: {list(self._registry.keys())}")
        result = self._registry.get((task_type.lower(), model_name.lower()))
        if result:
            logger.debug(f"Found plot function for {model_name} ({task_type})")
        else:
            logger.debug(f"No plot function found for {model_name} ({task_type})")
        return result
    
    def register_plots(self, plots: Dict[tuple, Callable]) -> None:
        """批量注册绘图函数"""
        for (task_type, model_name), func in plots.items():
            key = (task_type.lower(), model_name.lower())
            self._registry[key] = func

# 创建全局注册表实例
plot_registry = PlotRegistry()