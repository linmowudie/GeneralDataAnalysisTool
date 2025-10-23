"""
StandardScaler标准化变换器可视化策略
"""

from typing import Dict, Any
from .base import TransformerStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class StandardScalerStrategy(TransformerStrategy):
    """
    StandardScaler标准化变换器可视化策略
    """
    
    def validate_params(self) -> None:
        """
        验证StandardScaler参数
        """
        super().validate_params()
        if "model" not in self.params:
            raise ValueError("StandardScaler可视化需要模型对象")
        
        model = self.params["model"]
        if not hasattr(model, "scale_") or not hasattr(model, "mean_"):
            raise ValueError("模型对象没有scale_或mean_属性")

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        """
        charts = {}
        
        # 生成变换前后分布对比图
        before_after_charts = self.generate_before_after_distribution()
        charts.update(before_after_charts)
        
        # 生成缩放特征箱线图
        scaled_features_charts = self.generate_scaled_features_box()
        charts.update(scaled_features_charts)
        
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def generate_before_after_distribution(self) -> Dict[str, Figure]:
        """
        生成变换前后分布对比图
        """
        import matplotlib.pyplot as plt
        from ..utils.plot_before_after_distribution import plot_before_after_distribution
        
        X_train = self._get_training_data()
        model = self.params["model"]
        
        # 应用变换
        X_transformed = model.transform(X_train)
        
        # 获取特征名称
        feature_names = self.params.get("feature_names", None)
        
        # 绘制变换前后分布对比图
        fig, axes = plot_before_after_distribution(
            X_train, X_transformed, 
            feature_names=feature_names,
            figsize=(12, 8)
        )
        
        fig.suptitle('StandardScaler标准化变换前后分布对比', y=1.02)
        
        return {"standardscaler_before_after_distribution": fig}

    def generate_scaled_features_box(self) -> Dict[str, Figure]:
        """
        生成缩放特征箱线图
        """
        import matplotlib.pyplot as plt
        
        X_train = self._get_training_data()
        model = self.params["model"]
        
        # 应用变换
        X_transformed = model.transform(X_train)
        
        # 获取特征名称
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(X_transformed.shape[1])])
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 绘制箱线图
        ax.boxplot(X_transformed)
        ax.set_xticklabels(feature_names)
        ax.set_xlabel('特征')
        ax.set_ylabel('标准化值')
        ax.set_title('StandardScaler标准化后特征分布箱线图')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        return {"standardscaler_scaled_features_box": fig}