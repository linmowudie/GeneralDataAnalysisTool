# data_visualization/plots/meanshift.py
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure
import pandas as pd
import numpy as np


@plot_registry.register("clustering", "meanshift")
def plot_meanshift(params: Dict[str, Any]) -> Dict[str, Figure]:
    figures = {}
    feature = params["feature"]
    model = params.get("model_specific", {}).get("trained_model")
    label_style = params.get("label_style", {})
    shape_style = params.get("shape_style", {})
    point_size = shape_style.get("points", {}).get("size", 30)

    if feature.shape[1] < 2:
        fig, ax = plt.subplots()
        sns.histplot(feature.iloc[:, 0], kde=True, ax=ax)
        ax.set(title="Mean-Shift Histogram (1-D)")
        figures["histogram_1d"] = fig
        return figures

    # 1. 二维聚类散点
    fig1, ax1 = plt.subplots()
    labels = model.labels_ if model else np.zeros(len(feature))
    centers = model.cluster_centers_ if model else None
    scatter = ax1.scatter(
        feature.iloc[:, 0],
        feature.iloc[:, 1],
        c=labels,
        s=point_size,
        cmap="tab20",
        alpha=0.7
    )
    if centers is not None:
        ax1.scatter(centers[:, 0], centers[:, 1], c="red", s=200, marker="X")
    ax1.set(
        title=label_style.get("title", "Mean-Shift Clustering") or "Mean-Shift Clustering",
        xlabel=label_style.get("x", "Feature 1") or "Feature 1",
        ylabel=label_style.get("y", "Feature 2") or "Feature 2"
    )
    plt.colorbar(scatter, ax=ax1)
    figures["cluster_scatter"] = fig1

    # 2. 簇大小
    cluster_counts = pd.Series(labels).value_counts().sort_index()
    fig2, ax2 = plt.subplots()
    cluster_counts.plot(kind="bar", ax=ax2)
    ax2.set(title="Cluster Sizes", xlabel="Cluster", ylabel="Count")
    figures["cluster_sizes"] = fig2

    return figures