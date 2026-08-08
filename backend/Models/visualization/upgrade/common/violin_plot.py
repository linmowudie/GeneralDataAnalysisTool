"""
通用小提琴图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class ViolinPlotStrategy(VisualizationStrategy):
    """
    小提琴图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态小提琴图
        """
        charts = {}
        charts.update(self.generate_violin_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式小提琴图
        """
        charts = {}
        charts.update(self.generate_interactive_violin_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证小提琴图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"小提琴图缺少必要参数: {param}")

    def generate_violin_plot(self) -> Dict[str, Figure]:
        """
        生成静态小提琴图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            # 如果提供了y值，将其与X结合绘制小提琴图
            data = [X[:, i] for i in range(min(X.shape[1], 5))]  # 限制为前5个特征
            ax.violinplot(data)
            ax.set_xlabel('特征')
            ax.set_ylabel('值')
        else:
            # 如果没有y值，使用X的所有列
            if len(X.shape) > 1:
                data = [X[:, i] for i in range(min(X.shape[1], 5))]  # 限制为前5个特征
                ax.violinplot(data)
                ax.set_xlabel('特征')
            else:
                ax.violinplot(X)
                ax.set_xlabel('数据')
        
        ax.set_ylabel('值')
        ax.set_title('小提琴图')
        
        return {"violin_plot": fig}

    def generate_interactive_violin_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式小提琴图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        fig = go.Figure()
        
        if y is not None:
            # 如果提供了y值
            fig.add_trace(go.Violin(y=y, name='数据'))
        else:
            # 如果没有y值，使用X的所有列
            if len(X.shape) > 1:
                for i in range(min(X.shape[1], 5)):  # 限制为前5个特征
                    fig.add_trace(go.Violin(y=X[:, i], name=f'特征 {i+1}'))
            else:
                fig.add_trace(go.Violin(y=X, name='数据'))
        
        fig.update_layout(
            title="小提琴图",
            yaxis_title="值"
        )
        
        return {"violin_plot": fig}