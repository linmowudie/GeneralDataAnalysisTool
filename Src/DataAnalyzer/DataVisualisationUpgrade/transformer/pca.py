"""
PCA变换器可视化策略
"""

from typing import Dict, Any
from .base import TransformerStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class PCAStrategy(TransformerStrategy):
    """
    PCA变换器可视化策略
    """
    
    def generate_static_charts(self):
        """
        生成静态图表
        """
        # 默认实现，可以被子类覆盖
        return {}
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def validate_params(self) -> None:
        """
        验证PCA参数
        """
        super().validate_params()
        if "model" not in self.params:
            raise ValueError("PCA可视化需要模型对象")
        
        model = self.params["model"]
        if not hasattr(model, "explained_variance_ratio_"):
            raise ValueError("模型对象没有explained_variance_ratio_属性")

    def generate_explained_variance(self) -> Dict[str, Figure]:
        """
        生成解释方差图
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        explained_variance_ratio = model.explained_variance_ratio_
        n_components = len(explained_variance_ratio)
        
        self.apply_styles()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 各主成分解释方差
        ax1.bar(range(1, n_components + 1), explained_variance_ratio)
        ax1.set_xlabel('主成分')
        ax1.set_ylabel('解释方差比例')
        ax1.set_title('各主成分解释方差比例')
        
        # 累积解释方差
        cumsum_variance = np.cumsum(explained_variance_ratio)
        ax2.plot(range(1, n_components + 1), cumsum_variance, marker='o')
        ax2.set_xlabel('主成分数量')
        ax2.set_ylabel('累积解释方差比例')
        ax2.set_title('累积解释方差比例')
        
        plt.tight_layout()
        fig.suptitle('PCA解释方差分析', y=1.02)
        
        return {"pca_explained_variance": fig}

    def generate_principal_components_scatter(self) -> Dict[str, Figure]:
        """
        生成主成分散点图
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        X_train = self.params["X_train"]
        
        # 变换数据到主成分空间
        X_transformed = model.transform(X_train)
        
        # 只使用前两个主成分进行可视化
        pc1 = X_transformed[:, 0]
        pc2 = X_transformed[:, 1]
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        scatter = ax.scatter(pc1, pc2, alpha=0.7)
        ax.set_xlabel('第一主成分')
        ax.set_ylabel('第二主成分')
        ax.set_title('PCA主成分散点图')
        
        # 添加颜色条
        plt.colorbar(scatter, ax=ax)
        
        return {"pca_principal_components_scatter": fig}

    def generate_biplot(self) -> Dict[str, Figure]:
        """
        生成生物图（Biplot）
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        X_train = self.params["X_train"]
        
        # 获取主成分和特征向量
        components = model.components_
        explained_variance = model.explained_variance_ratio_
        
        # 变换数据到主成分空间
        X_transformed = model.transform(X_train)
        
        # 只使用前两个主成分进行可视化
        pc1 = X_transformed[:, 0]
        pc2 = X_transformed[:, 1]
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 绘制数据点
        ax.scatter(pc1, pc2, alpha=0.5)
        ax.set_xlabel(f'第一主成分 ({explained_variance[0]:.2%} 方差)')
        ax.set_ylabel(f'第二主成分 ({explained_variance[1]:.2%} 方差)')
        ax.set_title('PCA Biplot')
        
        # 绘制特征向量
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(components.shape[1])])
        
        scale_factor = np.max(np.abs(pc1)) / np.max(np.abs(components[0, :])) * 0.8
        
        for i in range(min(len(feature_names), components.shape[1])):
            ax.arrow(0, 0, 
                    components[0, i] * scale_factor, 
                    components[1, i] * scale_factor,
                    head_width=0.05, head_length=0.1, fc='red', ec='red')
            ax.text(components[0, i] * scale_factor * 1.1, 
                   components[1, i] * scale_factor * 1.1,
                   feature_names[i], 
                   color='red', ha='center', va='center')
        
        ax.grid(True)
        
        return {"pca_biplot": fig}