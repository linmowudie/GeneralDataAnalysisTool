# data_visualization/plots/kmeans.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure


@plot_registry.register("clustering", "kmeans")
def plot_kmeans(params: Dict[str, Any]) -> Dict[str, Figure]:
    figures = {}
    feature = params["feature"]
    model = params.get("model_specific", {}).get("trained_model")
    label_style = params.get("label_style", {})
    shape_style = params.get("shape_style", {})
    point_size = shape_style.get("points", {}).get("size", 30)
    point_colors = shape_style.get("points", {}).get("colors", ["tab:blue", "tab:orange", "tab:green"])

    if feature.shape[1] < 2:
        # 特征维度不足二维，只画直方图
        fig, ax = plt.subplots()
        sns.histplot(feature.iloc[:, 0], kde=True, ax=ax)
        ax.set(title="Cluster Histogram (1-D)")
        figures["histogram_1d"] = fig
        return figures

    # 1. 二维散点
    fig1, ax1 = plt.subplots()
    scatter = ax1.scatter(
        feature.iloc[:, 0],
        feature.iloc[:, 1],
        c=model.labels_ if model else 0,
        s=point_size,
        cmap="viridis",
        alpha=0.7
    )
    centers = model.cluster_centers_ if model else None
    if centers is not None:
        ax1.scatter(centers[:, 0], centers[:, 1], c="red", s=200, marker="X")
    ax1.set(
        title=label_style.get("title", "KMeans Clustering") or "KMeans Clustering",
        xlabel=label_style.get("x", "Component 1") or "Component 1",
        ylabel=label_style.get("y", "Component 2") or "Component 2"
    )
    plt.colorbar(scatter, ax=ax1)
    figures["cluster_scatter"] = fig1

    # 2. 聚类大小条形图
    if model:
        cluster_counts = pd.Series(model.labels_).value_counts().sort_index()
        fig2, ax2 = plt.subplots()
        cluster_counts.plot(kind="bar", ax=ax2, color=point_colors)
        ax2.set(title="Cluster Sizes", xlabel="Cluster", ylabel="Count")
        figures["cluster_sizes"] = fig2

    return figures