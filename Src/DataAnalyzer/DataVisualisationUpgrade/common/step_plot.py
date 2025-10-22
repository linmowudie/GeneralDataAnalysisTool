"""
通用阶梯图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class StepPlotStrategy(VisualizationStrategy):
    """
    阶梯图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态阶梯图
        """
        charts = {}
        charts.update(self.generate_step_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式阶梯图
        """
        charts = {}
        charts.update(self.generate_interactive_step_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证阶梯图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"阶梯图缺少必要参数: {param}")

    def generate_step_plot(self) -> Dict[str, Figure]:
        """
        生成静态阶梯图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            x_data = np.arange(len(y))
            ax.step(x_data, y, where='mid')
            ax.set_ylabel('值')
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                y_data = X[:, 0]
            else:
                y_data = X
            x_data = np.arange(len(y_data))
            ax.step(x_data, y_data, where='mid')
            ax.set_ylabel('值')
        
        ax.set_xlabel('索引')
        ax.set_title('阶梯图')
        
        return {"step_plot": fig}

    def generate_interactive_step_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式阶梯图
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
        
        # 添加阶梯图
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            line=dict(shape='hv'),  # 阶梯线型
            name='数据'
        ))
        
        fig.update_layout(
            title="阶梯图",
            xaxis_title="索引",
            yaxis_title="值"
        )
        
        return {"step_plot": fig}