"""
通用成对图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from typing import Union


class PairPlotStrategy(VisualizationStrategy):
    """
    成对图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态成对图
        """
        charts = {}
        charts.update(self.generate_pair_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式成对图
        """
        charts = {}
        charts.update(self.generate_interactive_pair_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证成对图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"成对图缺少必要参数: {param}")

    def generate_pair_plot(self) -> Dict[str, Figure]:
        """
        生成静态成对图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        # 限制特征数量以避免图表过于复杂
        n_features = min(X.shape[1], 5)
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(n_features)])
        
        self.apply_styles()
        
        # 创建子图网格
        fig, axes = plt.subplots(n_features, n_features, figsize=(3*n_features, 3*n_features))
        
        # 绘制成对图
        for i in range(n_features):
            for j in range(n_features):
                # 获取当前子图
                if n_features == 1:
                    ax = axes
                else:  # n_features > 1
                    # 将axes转换为numpy数组以便索引
                    axes_array = np.array(axes)
                    ax = axes_array[i, j]
                
                if i == j:
                    # 对角线显示直方图
                    ax.hist(X[:, j], bins=20, alpha=0.7)
                    ax.set_title(feature_names[j])
                else:
                    # 非对角线显示散点图
                    if y is not None:
                        ax.scatter(X[:, j], X[:, i], c=y, cmap='viridis', alpha=0.7)
                    else:
                        ax.scatter(X[:, j], X[:, i], alpha=0.7)
                
                # 设置坐标轴标签
                if i == n_features - 1:
                    ax.set_xlabel(feature_names[j])
                if j == 0:
                    ax.set_ylabel(feature_names[i])
        
        plt.tight_layout()
        fig.suptitle('成对图', y=1.02)
        
        return {"pair_plot": fig}

    def generate_interactive_pair_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式成对图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        # 限制特征数量以避免图表过于复杂
        n_features = min(X.shape[1], 5)
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(n_features)])
        
        # 创建子图
        fig = go.Figure()
        
        # 为每一对特征创建散点图
        for i in range(n_features):
            for j in range(n_features):
                if i != j:  # 只绘制非对角线元素
                    # 添加散点图轨迹
                    if y is not None:
                        fig.add_trace(go.Scatter(
                            x=X[:, j],
                            y=X[:, i],
                            mode='markers',
                            marker=dict(
                                color=y,
                                colorscale='Viridis',
                                showscale=(i == 1 and j == 0)  # 只在一个轨迹上显示颜色条
                            ),
                            name=f'{feature_names[j]} vs {feature_names[i]}',
                            visible='legendonly' if (i != 1 or j != 0) else True  # 默认只显示一个
                        ))
                    else:
                        fig.add_trace(go.Scatter(
                            x=X[:, j],
                            y=X[:, i],
                            mode='markers',
                            name=f'{feature_names[j]} vs {feature_names[i]}',
                            visible='legendonly' if (i != 1 or j != 0) else True  # 默认只显示一个
                        ))
        
        fig.update_layout(
            title="成对图 (请在图例中选择要显示的特征对)",
            xaxis_title="特征值",
            yaxis_title="特征值"
        )
        
        return {"pair_plot": fig}