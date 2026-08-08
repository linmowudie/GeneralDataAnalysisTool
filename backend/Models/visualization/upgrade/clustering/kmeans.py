"""
KMeans聚类模型可视化策略
"""

from typing import Dict, Any
from .base import ClusteringStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class KMeansStrategy(ClusteringStrategy):
    """
    KMeans聚类模型可视化策略
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
        验证KMeans聚类参数
        """
        super().validate_params()
        # 检查特征数据
        X = self._get_feature_data()
        
        # 检查维度
        if X.shape[1] < 2:
            raise ValueError("KMeans聚类可视化需要至少2维特征数据")

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
        ax.set_title('KMeans聚类散点图')
        
        # 添加颜色条
        plt.colorbar(scatter, ax=ax)
        
        return {"kmeans_cluster_scatter": fig}

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
        ax.set_title('KMeans各簇样本数量分布')
        
        # 在柱子上添加数值标签
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                   str(count), ha='center', va='bottom')
        
        return {"kmeans_cluster_bar": fig}

    def generate_elbow_method_plot(self) -> Dict[str, Figure]:
        """
        生成肘部法图
        """
        import matplotlib.pyplot as plt
        from sklearn.cluster import KMeans
        
        X = self._get_feature_data()
        
        # 获取KMeans模型
        model = self.params.get("model")
        if not model or not hasattr(model, 'n_clusters'):
            raise ValueError("肘部法图需要KMeans模型对象")
        
        # 计算不同k值的惯性
        k_range = range(1, min(11, len(X)))  # 最多计算到10个簇
        inertias = []
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(k_range, inertias, marker='o')
        ax.set_xlabel('簇数量 (k)')
        ax.set_ylabel('惯性')
        ax.set_title('KMeans肘部法图')
        
        return {"kmeans_elbow_method_plot": fig}