"""
UMAP降维变换器可视化策略
"""

from typing import Dict, Any
from .base import TransformerStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class UMAPStrategy(TransformerStrategy):
    """
    UMAP降维变换器可视化策略
    """
    
    def validate_params(self) -> None:
        """
        验证UMAP参数
        """
        super().validate_params()
        if "model" not in self.params:
            raise ValueError("UMAP可视化需要模型对象")

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        """
        charts = {}
        
        # 生成嵌入散点图
        embedding_charts = self.generate_embedding_scatter()
        charts.update(embedding_charts)
        
        # 生成连接图
        connectivity_charts = self.generate_connectivity_plot()
        charts.update(connectivity_charts)
        
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def generate_embedding_scatter(self) -> Dict[str, Figure]:
        """
        生成嵌入散点图
        """
        import matplotlib.pyplot as plt
        
        X_train = self._get_training_data()
        model = self.params["model"]
        
        # 应用变换
        X_transformed = model.fit_transform(X_train)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 绘制散点图（只使用前两个维度）
        scatter = ax.scatter(X_transformed[:, 0], X_transformed[:, 1], alpha=0.7)
        ax.set_xlabel('UMAP 第一维')
        ax.set_ylabel('UMAP 第二维')
        ax.set_title('UMAP 降维嵌入散点图')
        
        # 添加颜色条
        plt.colorbar(scatter, ax=ax)
        
        return {"umap_embedding_scatter": fig}

    def generate_connectivity_plot(self) -> Dict[str, Figure]:
        """
        生成连接图
        """
        import matplotlib.pyplot as plt
        
        X_train = self._get_training_data()
        model = self.params["model"]
        
        # 应用变换
        X_transformed = model.fit_transform(X_train)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 绘制散点图
        scatter = ax.scatter(X_transformed[:, 0], X_transformed[:, 1], alpha=0.7)
        
        # 如果模型有graph_属性，则绘制连接
        if hasattr(model, 'graph_'):
            # 获取图的连接信息
            graph = model.graph_
            # 这里简化处理，实际应用中可能需要更复杂的连接可视化
            ax.set_title('UMAP 连接图')
        else:
            ax.set_title('UMAP 降维嵌入散点图（无连接信息）')
        
        ax.set_xlabel('UMAP 第一维')
        ax.set_ylabel('UMAP 第二维')
        
        # 添加颜色条
        plt.colorbar(scatter, ax=ax)
        
        return {"umap_connectivity_plot": fig}