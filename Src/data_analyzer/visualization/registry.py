# data_visualization/registry.py
from typing import Dict, Callable, Any, Optional

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
            return func
        return decorator
    
    def get_plot_function(self, task_type: str, model_name: str) -> Optional[Callable]:
        """获取绘图函数"""
        return self._registry.get((task_type.lower(), model_name.lower()))
    
    def register_plots(self, plots: Dict[tuple, Callable]) -> None:
        """批量注册绘图函数"""
        for (task_type, model_name), func in plots.items():
            key = (task_type.lower(), model_name.lower())
            self._registry[key] = func

# 创建全局注册表实例
plot_registry = PlotRegistry()