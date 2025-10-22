"""
通用气泡图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class BubblePlotStrategy(VisualizationStrategy):
    """
    气泡图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态气泡图
        """
        charts = {}
        charts.update(self.generate_bubble_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式气泡图
        """
        charts = {}
        charts.update(self.generate_interactive_bubble_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证气泡图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"气泡图缺少必要参数: {param}")
        
        X = self.params["X"]
        if X.shape[1] < 2:
            raise ValueError("气泡图需要至少2维数据")

    def generate_bubble_plot(self) -> Dict[str, Figure]:
        """
        生成静态气泡图
        """
        X = self.params["X"]
        y = self.params.get("y")
        sizes = self.params.get("sizes")
        
        # 使用前两维作为x和y坐标
        x_data = X[:, 0]
        y_data = X[:, 1]
        
        # 确定气泡大小
        if sizes is not None:
            bubble_sizes = sizes
        elif X.shape[1] > 2:
            # 使用第三维作为气泡大小
            bubble_sizes = X[:, 2]
        else:
            # 默认大小
            bubble_sizes = np.ones(len(x_data)) * 50
        
        # 归一化气泡大小
        bubble_sizes = 100 * (bubble_sizes - bubble_sizes.min()) / (bubble_sizes.max() - bubble_sizes.min() + 1e-8) + 20
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 绘制气泡图
        if y is not None:
            scatter = ax.scatter(x_data, y_data, s=bubble_sizes, c=y, cmap='viridis', alpha=0.6)
            plt.colorbar(scatter, ax=ax)
        else:
            ax.scatter(x_data, y_data, s=bubble_sizes, alpha=0.6)
        
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('气泡图')
        
        return {"bubble_plot": fig}

    def generate_interactive_bubble_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式气泡图
        """
        X = self.params["X"]
        y = self.params.get("y")
        sizes = self.params.get("sizes")
        
        # 使用前两维作为x和y坐标
        x_data = X[:, 0]
        y_data = X[:, 1]
        
        # 确定气泡大小
        if sizes is not None:
            bubble_sizes = sizes
        elif X.shape[1] > 2:
            # 使用第三维作为气泡大小
            bubble_sizes = X[:, 2]
        else:
            # 默认大小
            bubble_sizes = np.ones(len(x_data)) * 50
        
        # 归一化气泡大小
        bubble_sizes = 50 * (bubble_sizes - bubble_sizes.min()) / (bubble_sizes.max() - bubble_sizes.min() + 1e-8) + 10
        
        fig = go.Figure()
        
        # 添加气泡图
        if y is not None:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='markers',
                marker=dict(
                    size=bubble_sizes,
                    color=y,
                    colorscale='Viridis',
                    showscale=True,
                    opacity=0.6
                ),
                name='数据点'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='markers',
                marker=dict(
                    size=bubble_sizes,
                    opacity=0.6
                ),
                name='数据点'
            ))
        
        fig.update_layout(
            title="气泡图",
            xaxis_title="特征 1",
            yaxis_title="特征 2"
        )
        
        return {"bubble_plot": fig}