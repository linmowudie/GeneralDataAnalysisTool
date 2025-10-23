"""
3D投影变换器可视化策略
"""

from typing import Dict, Any
from .base import TransformerStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class ThreeDStrategy(TransformerStrategy):
    """
    3D投影变换器可视化策略
    """
    
    def validate_params(self) -> None:
        """
        验证3D投影参数
        """
        super().validate_params()
        X_train = self._get_training_data()
        
        # 检查数据维度是否至少为3维
        if X_train.shape[1] < 3:
            raise ValueError("3D投影需要至少3维数据")

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        """
        charts = {}
        
        # 生成3D散点图
        scatter_charts = self.generate_scatter_3d()
        charts.update(scatter_charts)
        
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式图表
        """
        charts = {}
        
        # 生成3D散点图
        scatter_charts = self.generate_scatter_3d_interactive()
        charts.update(scatter_charts)
        
        # 生成3D表面图
        surface_charts = self.generate_surface_3d()
        charts.update(surface_charts)
        
        # 生成3D线框图
        wireframe_charts = self.generate_wireframe_3d()
        charts.update(wireframe_charts)
        
        return charts

    def generate_scatter_3d(self) -> Dict[str, Figure]:
        """
        生成3D散点图
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        X_train = self._get_training_data()
        
        self.apply_styles()
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 绘制3D散点图（只使用前三个维度）
        scatter = ax.scatter(X_train[:, 0], X_train[:, 1], X_train[:, 2], alpha=0.7)
        ax.set_xlabel('X轴')
        ax.set_ylabel('Y轴')
        ax.set_zlabel('Z轴')
        ax.set_title('3D散点图')
        
        return {"three_d_scatter": fig}

    def generate_scatter_3d_interactive(self) -> Dict[str, go.Figure]:
        """
        生成交互式3D散点图
        """
        X_train = self._get_training_data()
        
        # 创建交互式3D散点图
        fig = go.Figure(data=[go.Scatter3d(
            x=X_train[:, 0],
            y=X_train[:, 1],
            z=X_train[:, 2],
            mode='markers',
            marker=dict(
                size=5,
                opacity=0.8
            )
        )])
        
        fig.update_layout(
            title='交互式3D散点图',
            scene=dict(
                xaxis_title='X轴',
                yaxis_title='Y轴',
                zaxis_title='Z轴'
            )
        )
        
        return {"three_d_scatter_interactive": fig}

    def generate_surface_3d(self) -> Dict[str, go.Figure]:
        """
        生成3D表面图
        """
        X_train = self._get_training_data()
        
        # 创建3D表面图
        fig = go.Figure(data=[go.Surface(
            z=X_train[:50, :50],  # 限制数据大小以提高性能
        )])
        
        fig.update_layout(
            title='3D表面图',
            scene=dict(
                xaxis_title='X轴',
                yaxis_title='Y轴',
                zaxis_title='Z轴'
            )
        )
        
        return {"three_d_surface": fig}

    def generate_wireframe_3d(self) -> Dict[str, go.Figure]:
        """
        生成3D线框图
        """
        X_train = self._get_training_data()
        
        # 创建3D线框图
        fig = go.Figure(data=[go.Scatter3d(
            x=X_train[:, 0],
            y=X_train[:, 1],
            z=X_train[:, 2],
            mode='lines',
            line=dict(
                width=2,
                color='blue'
            )
        )])
        
        fig.update_layout(
            title='3D线框图',
            scene=dict(
                xaxis_title='X轴',
                yaxis_title='Y轴',
                zaxis_title='Z轴'
            )
        )
        
        return {"three_d_wireframe": fig}