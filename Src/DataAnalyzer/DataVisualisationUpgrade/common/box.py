"""
通用箱线图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class BoxPlotStrategy(VisualizationStrategy):
    """
    箱线图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态箱线图
        """
        charts = {}
        charts.update(self.generate_box_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式箱线图
        """
        charts = {}
        charts.update(self.generate_interactive_box_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证箱线图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"箱线图缺少必要参数: {param}")

    def generate_box_plot(self) -> Dict[str, Figure]:
        """
        生成静态箱线图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            ax.boxplot(y)
            ax.set_ylabel('值')
        else:
            # 如果没有y值，使用X的所有列
            if len(X.shape) > 1:
                data = [X[:, i] for i in range(X.shape[1])]
                ax.boxplot(data)
                ax.set_xlabel('特征')
            else:
                ax.boxplot(X)
                ax.set_xlabel('数据')
        
        ax.set_ylabel('值')
        ax.set_title('箱线图')
        
        return {"box_plot": fig}

    def generate_interactive_box_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式箱线图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        fig = go.Figure()
        
        if y is not None:
            fig.add_trace(go.Box(y=y, name='数据'))
        else:
            # 如果没有y值，使用X的所有列
            if len(X.shape) > 1:
                for i in range(X.shape[1]):
                    fig.add_trace(go.Box(y=X[:, i], name=f'特征 {i+1}'))
            else:
                fig.add_trace(go.Box(y=X, name='数据'))
        
        fig.update_layout(
            title="箱线图",
            yaxis_title="值"
        )
        
        return {"box_plot": fig}