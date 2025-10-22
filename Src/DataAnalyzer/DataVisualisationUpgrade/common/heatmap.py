"""
通用热力图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class HeatmapStrategy(VisualizationStrategy):
    """
    热力图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态热力图
        """
        charts = {}
        charts.update(self.generate_heatmap())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式热力图
        """
        charts = {}
        charts.update(self.generate_interactive_heatmap())
        return charts

    def validate_params(self) -> None:
        """
        验证热力图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"热力图缺少必要参数: {param}")

    def generate_heatmap(self) -> Dict[str, Figure]:
        """
        生成静态热力图
        """
        X = self.params["X"]
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 创建热力图
        im = ax.imshow(X, cmap='viridis', aspect='auto')
        plt.colorbar(im, ax=ax)
        
        ax.set_title('热力图')
        
        return {"heatmap": fig}

    def generate_interactive_heatmap(self) -> Dict[str, go.Figure]:
        """
        生成交互式热力图
        """
        X = self.params["X"]
        
        fig = go.Figure(data=go.Heatmap(
            z=X,
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title="热力图"
        )
        
        return {"heatmap": fig}