"""
通用图表可视化基础策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class CommonChartStrategy(VisualizationStrategy):
    """
    通用图表可视化策略基类
    """

    def validate_params(self) -> None:
        """
        验证通用图表参数
        """
        # 通用图表参数验证可以根据具体图表类型进行
        pass

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        
        Returns:
            包含图表名称和Figure对象的字典
        """
        # 通用图表基类不实现具体图表生成
        return {}

    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式图表
        
        Returns:
            包含图表名称和plotly Figure对象的字典
        """
        # 通用图表基类不实现具体图表生成
        return {}