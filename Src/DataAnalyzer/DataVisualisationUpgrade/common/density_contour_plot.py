"""
通用密度等高线图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


class DensityContourPlotStrategy(VisualizationStrategy):
    """
    密度等高线图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态密度等高线图
        """
        charts = {}
        charts.update(self.generate_density_contour_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式密度等高线图
        """
        charts = {}
        charts.update(self.generate_interactive_density_contour_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证密度等高线图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"密度等高线图缺少必要参数: {param}")
        
        X = self.params["X"]
        if X.shape[1] < 2:
            raise ValueError("密度等高线图需要至少2维数据")

    def generate_density_contour_plot(self) -> Dict[str, Figure]:
        """
        生成静态密度等高线图
        """
        X = self.params["X"]
        
        # 只使用前两维进行可视化
        x_data = X[:, 0]
        y_data = X[:, 1]
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 创建2D核密度估计
        xmin, xmax = x_data.min(), x_data.max()
        ymin, ymax = y_data.min(), y_data.max()
        
        # 扩展范围以更好地显示边缘
        x_range = xmax - xmin
        y_range = ymax - ymin
        xmin -= 0.1 * x_range
        xmax += 0.1 * x_range
        ymin -= 0.1 * y_range
        ymax += 0.1 * y_range
        
        # 创建网格
        xx, yy = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
        positions = np.vstack([xx.ravel(), yy.ravel()])
        values = np.vstack([x_data, y_data])
        
        # 计算核密度估计
        kernel = stats.gaussian_kde(values)
        f = np.reshape(kernel(positions).T, xx.shape)
        
        # 绘制等高线图
        ax.contourf(xx, yy, f, cmap='Blues')
        contour = ax.contour(xx, yy, f, colors='black', alpha=0.5)
        ax.clabel(contour, inline=True, fontsize=8)
        
        ax.scatter(x_data, y_data, c='red', s=10, alpha=0.6)
        
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('密度等高线图')
        
        return {"density_contour_plot": fig}

    def generate_interactive_density_contour_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式密度等高线图
        """
        X = self.params["X"]
        
        # 只使用前两维进行可视化
        x_data = X[:, 0]
        y_data = X[:, 1]
        
        # 创建2D核密度估计
        xmin, xmax = x_data.min(), x_data.max()
        ymin, ymax = y_data.min(), y_data.max()
        
        # 扩展范围以更好地显示边缘
        x_range = xmax - xmin
        y_range = ymax - ymin
        xmin -= 0.1 * x_range
        xmax += 0.1 * x_range
        ymin -= 0.1 * y_range
        ymax += 0.1 * y_range
        
        # 创建网格
        xx, yy = np.mgrid[xmin:xmax:50j, ymin:ymax:50j]
        positions = np.vstack([xx.ravel(), yy.ravel()])
        values = np.vstack([x_data, y_data])
        
        # 计算核密度估计
        kernel = stats.gaussian_kde(values)
        f = np.reshape(kernel(positions).T, xx.shape)
        
        fig = go.Figure()
        
        # 添加等高线图
        fig.add_trace(go.Contour(
            x=np.linspace(xmin, xmax, 50),
            y=np.linspace(ymin, ymax, 50),
            z=f,
            colorscale='Blues',
            contours_coloring='fill',
            name='密度'
        ))
        
        # 添加散点图
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='markers',
            marker=dict(
                color='red',
                size=5,
                opacity=0.6
            ),
            name='数据点'
        ))
        
        fig.update_layout(
            title="密度等高线图",
            xaxis_title="特征 1",
            yaxis_title="特征 2"
        )
        
        return {"density_contour_plot": fig}