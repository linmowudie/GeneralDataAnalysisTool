"""
聚类策略：根据簇数选择最佳展示方式
"""

from typing import Dict, Any, List
import numpy as np


class ClusteringStrategySelector:
    """
    聚类任务策略选择器
    根据簇的数量和数据特征选择合适的图表类型
    """

    def select_charts(self, params: Dict[str, Any]) -> List[str]:
        """
        为聚类任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        selected_charts = []
        
        # 获取模型名称
        model_name = params.get("model_name", "").lower()
        
        # 获取簇标签
        labels = None
        if "labels" in params:
            labels = params["labels"]
        elif "model" in params:
            model = params["model"]
            if hasattr(model, "labels_"):
                labels = model.labels_
        
        # 如果没有标签信息，则返回默认图表
        if labels is None:
            return ["cluster_scatter", "cluster_bar"]
        
        # 获取簇的数量
        n_clusters = len(set(labels))
        
        # 添加基本图表
        selected_charts.append("cluster_scatter")
        selected_charts.append("cluster_bar")
        
        # 根据簇数量选择额外图表
        if n_clusters <= 10:  # 簇数较少时添加轮廓分析
            selected_charts.append("silhouette_analysis")
        
        # 根据模型类型选择特定图表
        if model_name == "kmeans":
            # 添加肘部法图（适用于KMeans等算法）
            model = params.get("model")
            if model and hasattr(model, "inertia_"):
                selected_charts.append("elbow_method_plot")
        elif model_name == "meanshift":
            # MeanShift添加1D直方图
            selected_charts.append("histogram_1d")
        elif model_name in ["agglomerativeclustering", "hierarchical"]:
            # 层次聚类添加树状图
            selected_charts.append("dendrogram")
        
        # 根据数据维度选择3D图表
        X = params.get("X", params.get("X_train"))
        if X is not None and X.shape[1] >= 3:
            selected_charts.append("projection_3d")
        
        # 添加降维投影图表
        if X is not None and X.shape[0] <= 10000:  # 数据量不太大时添加
            selected_charts.append("t_sne_projection")
            selected_charts.append("umap_projection")
        
        return selected_charts