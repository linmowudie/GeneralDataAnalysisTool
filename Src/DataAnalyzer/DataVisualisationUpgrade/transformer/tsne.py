"""
t-SNE降维变换器可视化策略
"""

from typing import Dict, Any
from .base import TransformerStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class TSNEStrategy(TransformerStrategy):
    """
    t-SNE降维变换器可视化策略
    """
    
    def validate_params(self) -> None:
        """
        验证t-SNE参数
        """
        super().validate_params()
        if "model" not in self.params:
            raise ValueError("t-SNE可视化需要模型对象")

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        """
        charts = {}
        
        # 生成嵌入散点图
        embedding_charts = self.generate_embedding_scatter()
        charts.update(embedding_charts)
        
        # 生成困惑度比较图
        perplexity_charts = self.generate_perplexity_comparison()
        charts.update(perplexity_charts)
        
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
        ax.set_xlabel('t-SNE 第一维')
        ax.set_ylabel('t-SNE 第二维')
        ax.set_title('t-SNE 降维嵌入散点图')
        
        # 添加颜色条
        plt.colorbar(scatter, ax=ax)
        
        return {"tsne_embedding_scatter": fig}

    def generate_perplexity_comparison(self) -> Dict[str, Figure]:
        """
        生成困惑度比较图
        """
        import matplotlib.pyplot as plt
        from sklearn.manifold import TSNE
        
        X_train = self._get_training_data()
        
        # 测试不同的困惑度值
        perplexities = [5, 10, 20, 30, 50]
        n_perplexities = len(perplexities)
        
        self.apply_styles()
        fig, axes = plt.subplots(1, n_perplexities, figsize=(5*n_perplexities, 5))
        
        # 如果只有一个困惑度，调整axes的形状
        if n_perplexities == 1:
            axes = [axes]
        
        for i, perplexity in enumerate(perplexities):
            # 应用t-SNE
            tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
            X_transformed = tsne.fit_transform(X_train)
            
            # 绘制散点图
            axes[i].scatter(X_transformed[:, 0], X_transformed[:, 1], alpha=0.7)
            axes[i].set_title(f'困惑度 = {perplexity}')
            axes[i].set_xlabel('t-SNE 第一维')
            axes[i].set_ylabel('t-SNE 第二维')
        
        plt.tight_layout()
        fig.suptitle('t-SNE 不同困惑度效果比较', y=1.02)
        
        return {"tsne_perplexity_comparison": fig}