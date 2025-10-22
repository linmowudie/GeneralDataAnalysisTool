"""
通用面积图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class AreaPlotStrategy(VisualizationStrategy):
    """
    面积图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态面积图
        """
        charts = {}
        charts.update(self.generate_area_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式面积图
        """
        charts = {}
        charts.update(self.generate_interactive_area_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证面积图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"面积图缺少必要参数: {param}")

    def generate_area_plot(self) -> Dict[str, Figure]:
        """
        生成静态面积图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            x_data = np.arange(len(y))
            ax.fill_between(x_data, y, alpha=0.7)
            ax.set_ylabel('值')
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                y_data = X[:, 0]
            else:
                y_data = X
            x_data = np.arange(len(y_data))
            ax.fill_between(x_data, y_data, alpha=0.7)
            ax.set_ylabel('值')
        
        ax.set_xlabel('索引')
        ax.set_title('面积图')
        
        return {"area_plot": fig}

    def generate_interactive_area_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式面积图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        if y is not None:
            x_data = list(range(len(y)))
            y_data = y
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                y_data = X[:, 0]
            else:
                y_data = X
            x_data = list(range(len(y_data)))
        
        fig = go.Figure()
        
        # 添加面积图
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            fill='tozeroy',
            name='数据'
        ))
        
        fig.update_layout(
            title="面积图",
            xaxis_title="索引",
            yaxis_title="值"
        )
        
        return {"area_plot": fig}