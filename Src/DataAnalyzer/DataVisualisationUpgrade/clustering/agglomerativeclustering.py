"""
AgglomerativeClustering聚类模型可视化策略
"""

from typing import Dict, Any
from .base import ClusteringStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class AgglomerativeClusteringStrategy(ClusteringStrategy):
    """
    AgglomerativeClustering聚类模型可视化策略
    """
    
    def validate_params(self) -> None:
        """
        验证AgglomerativeClustering聚类参数
        """
        super().validate_params()
        # 检查特征数据
        X = self._get_feature_data()
        
        # 检查维度
        if X.shape[1] < 2:
            raise ValueError("AgglomerativeClustering聚类可视化需要至少2维特征数据")

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        """
        charts = {}
        
        # 生成聚类散点图
        cluster_scatter_charts = self.generate_cluster_scatter()
        charts.update(cluster_scatter_charts)
        
        # 生成树状图
        dendrogram_charts = self.generate_dendrogram()
        charts.update(dendrogram_charts)
        
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
        ax.set_title('层次聚类散点图')
        
        # 添加颜色条
        plt.colorbar(scatter, ax=ax)
        
        return {"agglomerative_cluster_scatter": fig}

    def generate_dendrogram(self) -> Dict[str, Figure]:
        """
        生成树状图
        """
        import matplotlib.pyplot as plt
        from scipy.cluster.hierarchy import dendrogram
        from scipy.spatial.distance import pdist
        from scipy.cluster.hierarchy import linkage
        
        X = self._get_feature_data()
        
        # 如果参数中提供了linkage_matrix，则直接使用
        linkage_matrix = self.params.get("linkage_matrix")
        if linkage_matrix is None:
            # 否则计算linkage矩阵
            distance_matrix = pdist(X)
            linkage_matrix = linkage(distance_matrix, method='ward')
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制树状图
        dendrogram(linkage_matrix, ax=ax)
        
        ax.set_xlabel('样本索引或聚类大小')
        ax.set_ylabel('距离')
        ax.set_title('层次聚类树状图')
        
        return {"agglomerative_dendrogram": fig}