"""
Src/DataAnalyzer/DataVisualisationUpgrade/base_visualization.py
新版数据可视化模块基类文件

定义可视化策略的基类和通用接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.graph_objects as go


class VisualizationStrategy(ABC):
    """
    可视化策略抽象基类
    """

    def __init__(self, params: Dict[str, Any]):
        """
        初始化可视化策略
        
        Args:
            params: 可视化参数字典
        """
        self.params = params

    @abstractmethod
    def validate_params(self) -> None:
        """
        验证参数
        """
        pass

    @abstractmethod
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        
        Returns:
            包含图表名称和Figure对象的字典
        """
        pass

    @abstractmethod
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式图表
        
        Returns:
            包含图表名称和plotly Figure对象的字典
        """
        pass

    def apply_styles(self) -> None:
        """
        应用样式设置
        """
        # 设置matplotlib样式
        plot_style = self.params.get("plot_style")
        if plot_style:
            plt.style.use(plot_style)
            
        # 设置字体
        font_style = self.params.get("font_style")
        if font_style:
            plt.rcParams.update({"font.family": font_style})