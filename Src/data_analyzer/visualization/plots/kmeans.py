# visualization/plots/kmeans.py
"""
Src/data_analyzer/visualization/plots/kmeans.py
K-Means聚类可视化模块

该模块提供K-Means聚类模型的可视化功能，
包括聚类结果散点图的绘制。
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)

@plot_registry.register("clustering", "kmeans")
def plot_kmeans(params: Dict[str, Any]) -> Dict[str, Figure]:
    figures = {}
    feature = params["feature"]
    model = params.get("model_specific", {}).get("trained_model")
    label_style = params.get("label_style", {})
    shape_style = params.get("shape_style", {})
    point_size = shape_style.get("points", {}).get("size", 50)
    point_colors = shape_style.get("points", {}).get("colors", ["tab:blue", "tab:orange", "tab:green"])

    try:
        if feature.shape[1] < 2:
            # 特征维度不足二维，只画直方图
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(feature.iloc[:, 0], kde=True, ax=ax)
            ax.set(title=label_style.get("title", "Cluster Histogram (1-D)") or "Cluster Histogram (1-D)")
            figures["histogram_1d"] = fig
            return figures

        # 1. 二维散点图
        fig1, ax1 = plt.subplots(figsize=(10, 8))
        
        # 获取标签
        labels = model.labels_ if model and hasattr(model, 'labels_') else np.zeros(len(feature))
        
        # 绘制散点图
        scatter = ax1.scatter(
            feature.iloc[:, 0],
            feature.iloc[:, 1],
            c=labels,
            s=point_size,
            cmap="viridis",
            alpha=0.7,
            edgecolors='w',
            linewidth=0.5
        )
        
        # 绘制聚类中心
        centers = model.cluster_centers_ if model and hasattr(model, 'cluster_centers_') else None
        if centers is not None:
            ax1.scatter(centers[:, 0], centers[:, 1], c="red", s=300, marker="X", 
                       edgecolors='black', linewidth=2, label='Cluster Centers')
            ax1.legend()
            
        ax1.set(
            title=label_style.get("title", "KMeans Clustering Results") or "KMeans Clustering Results",
            xlabel=label_style.get("x", feature.columns[0] if hasattr(feature, 'columns') else "Feature 1") or "Feature 1",
            ylabel=label_style.get("y", feature.columns[1] if hasattr(feature, 'columns') and len(feature.columns) > 1 else "Feature 2") or "Feature 2"
        )
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1)
        figures["cluster_scatter"] = fig1

        # 2. 聚类大小条形图
        if model and hasattr(model, 'labels_'):
            cluster_counts = pd.Series(model.labels_).value_counts().sort_index()
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            bars = ax2.bar(range(len(cluster_counts)), cluster_counts.values, 
                          color=point_colors[:len(cluster_counts)] if len(point_colors) >= len(cluster_counts) else point_colors)
            ax2.set(title="Cluster Sizes", xlabel="Cluster", ylabel="Number of Points")
            ax2.set_xticks(range(len(cluster_counts)))
            ax2.set_xticklabels([f"Cluster {i}" for i in cluster_counts.index])
            ax2.grid(True, alpha=0.3)
            
            # 在每个条形上添加数值标签
            for i, (bar, count) in enumerate(zip(bars, cluster_counts.values)):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        str(count), ha='center', va='bottom')
            
            figures["cluster_sizes"] = fig2
            
        # 3. 如果有3个或更多特征，创建成对特征图
        if feature.shape[1] >= 3 and model and hasattr(model, 'labels_'):
            fig3, ax3 = plt.subplots(figsize=(10, 8))
            # 使用前三个特征创建3D散点图的投影
            scatter = ax3.scatter(
                feature.iloc[:, 2],  # 第三个特征作为X轴
                feature.iloc[:, 1],  # 第二个特征作为Y轴
                c=labels,
                s=point_size,
                cmap="viridis",
                alpha=0.7,
                edgecolors='w',
                linewidth=0.5
            )
            
            ax3.set(
                title=label_style.get("title", "KMeans Clustering (Features 3 vs 2)") or "KMeans Clustering (Features 3 vs 2)",
                xlabel=label_style.get("x", feature.columns[2] if hasattr(feature, 'columns') and len(feature.columns) > 2 else "Feature 3") or "Feature 3",
                ylabel=label_style.get("y", feature.columns[1] if hasattr(feature, 'columns') and len(feature.columns) > 1 else "Feature 2") or "Feature 2"
            )
            ax3.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax3)
            figures["cluster_scatter_3v2"] = fig3

    except Exception as e:
        logger.error(f"KMeans聚类可视化过程中出现错误: {str(e)}")
        raise
    
    return figures