"""
通用折线图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class LinePlotStrategy(VisualizationStrategy):
    """
    折线图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态折线图
        """
        charts = {}
        charts.update(self.generate_line_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式折线图
        """
        charts = {}
        charts.update(self.generate_interactive_line_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证折线图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"折线图缺少必要参数: {param}")

    def generate_line_plot(self) -> Dict[str, Figure]:
        """
        生成静态折线图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            ax.plot(X, y)
            ax.set_ylabel('值')
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                ax.plot(X[:, 0])
            else:
                ax.plot(X)
        
        ax.set_xlabel('索引')
        ax.set_title('折线图')
        
        return {"line_plot": fig}

    def generate_interactive_line_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式折线图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        fig = go.Figure()
        
        if y is not None:
            fig.add_trace(go.Scatter(
                x=list(range(len(y))),
                y=y,
                mode='lines+markers',
                name='数据'
            ))
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                y_data = X[:, 0]
            else:
                y_data = X
            fig.add_trace(go.Scatter(
                x=list(range(len(y_data))),
                y=y_data,
                mode='lines+markers',
                name='数据'
            ))
        
        fig.update_layout(
            title="折线图",
            xaxis_title="索引",
            yaxis_title="值"
        )
        
        return {"line_plot": fig}