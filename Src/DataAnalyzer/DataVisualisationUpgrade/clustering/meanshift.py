"""
MeanShift聚类模型可视化策略
"""

from typing import Dict, Any
from .base import ClusteringStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class MeanShiftStrategy(ClusteringStrategy):
    """
    MeanShift聚类模型可视化策略
    """
    
    def validate_params(self) -> None:
        """
        验证MeanShift聚类参数
        """
        super().validate_params()
        # 检查特征数据
        X = self._get_feature_data()
        
        # 检查维度
        if X.shape[1] < 2:
            raise ValueError("MeanShift聚类可视化需要至少2维特征数据")

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        """
        charts = {}
        
        # 生成聚类散点图
        cluster_scatter_charts = self.generate_cluster_scatter()
        charts.update(cluster_scatter_charts)
        
        # 生成聚类柱状图
        cluster_bar_charts = self.generate_cluster_bar()
        charts.update(cluster_bar_charts)
        
        # 生成1D直方图
        histogram_charts = self.generate_histogram_1d()
        charts.update(histogram_charts)
        
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def generate_cluster_scatter(self) -> Dict[str, Figure]:
        """
        生成聚类散点图
        """
        import matplotlib.pyplot as plt
        
        X = self._get_feature_data()
        labels = self._get_cluster_labels()
        
        # 只使用前两维进行可视化
        X_vis = X[:, :2]
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        scatter = ax.scatter(X_vis[:, 0], X_vis[:, 1], c=labels, cmap='viridis')
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('MeanShift聚类散点图')
        
        # 添加颜色条
        plt.colorbar(scatter, ax=ax)
        
        return {"meanshift_cluster_scatter": fig}

    def generate_cluster_bar(self) -> Dict[str, Figure]:
        """
        生成聚类柱状图
        """
        import matplotlib.pyplot as plt
        
        labels = self._get_cluster_labels()
        
        # 计算每个簇的样本数量
        unique_labels, counts = np.unique(labels, return_counts=True)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        bars = ax.bar(unique_labels, counts)
        ax.set_xlabel('簇')
        ax.set_ylabel('样本数量')
        ax.set_title('MeanShift各簇样本数量分布')
        
        # 在柱子上添加数值标签
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                   str(count), ha='center', va='bottom')
        
        return {"meanshift_cluster_bar": fig}

    def generate_histogram_1d(self) -> Dict[str, Figure]:
        """
        生成1D直方图
        """
        import matplotlib.pyplot as plt
        
        X = self._get_feature_data()
        labels = self._get_cluster_labels()
        unique_labels = np.unique(labels)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 为每个簇绘制直方图
        for label in unique_labels:
            cluster_data = X[labels == label, 0]  # 使用第一维特征
            ax.hist(cluster_data, alpha=0.7, label=f'簇 {label}', bins=30)
        
        ax.set_xlabel('特征值')
        ax.set_ylabel('频率')
        ax.set_title('MeanShift聚类1D直方图')
        ax.legend()
        
        return {"meanshift_histogram_1d": fig}