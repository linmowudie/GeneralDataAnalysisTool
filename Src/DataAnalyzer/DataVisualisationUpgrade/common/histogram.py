"""
通用直方图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class HistogramStrategy(VisualizationStrategy):
    """
    直方图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态直方图
        """
        charts = {}
        charts.update(self.generate_histogram())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式直方图
        """
        charts = {}
        charts.update(self.generate_interactive_histogram())
        return charts

    def validate_params(self) -> None:
        """
        验证直方图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"直方图缺少必要参数: {param}")

    def generate_histogram(self) -> Dict[str, Figure]:
        """
        生成静态直方图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            ax.hist(y, bins=30)
            ax.set_xlabel('值')
        else:
            # 如果没有y值，使用X的第一列
            if len(X.shape) > 1:
                data = X[:, 0]
            else:
                data = X
            ax.hist(data, bins=30)
            ax.set_xlabel('值')
        
        ax.set_ylabel('频率')
        ax.set_title('直方图')
        
        return {"histogram": fig}

    def generate_interactive_histogram(self) -> Dict[str, go.Figure]:
        """
        生成交互式直方图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        if y is not None:
            data = y
        else:
            # 如果没有y值，使用X的第一列
            if len(X.shape) > 1:
                data = X[:, 0]
            else:
                data = X
        
        fig = go.Figure(data=[
            go.Histogram(x=data)
        ])
        
        fig.update_layout(
            title="直方图",
            xaxis_title="值",
            yaxis_title="频率"
        )
        
        return {"histogram": fig}