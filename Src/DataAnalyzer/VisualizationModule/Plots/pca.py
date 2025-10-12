# visualization/plots/pca.py
"""
Src/DataAnalyzer/VisualizationModule/Plots/pca.py
主成分分析(PCA)可视化模块

该模块提供主成分分析模型的可视化功能，
包括降维结果和主成分分布的可视化展示。
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure

@plot_registry.register("transformer", "pca")
def plot_pca(params: Dict[str, Any]) -> Dict[str, Figure]:
    """PCA可视化"""
    figures = {}
    features = params["feature"]
    explained_variance = params.get("model_specific", {}).get("explained_variance_ratio")
    
    # 方差解释率
    if explained_variance is not None:
        fig1, ax1 = plt.subplots()
        cum_var = np.cumsum(explained_variance)
        ax1.bar(range(1, len(explained_variance)+1), explained_variance, alpha=0.6)
        ax1.plot(range(1, len(cum_var)+1), cum_var, 'ro-')
        ax1.axhline(y=0.95, color='g', linestyle='--')
        ax1.set(
            title="方差解释率",
            xlabel="主成分数量",
            ylabel="解释方差比率"
        )
        figures["variance_explained"] = fig1
    
    # 主成分投影（仅展示前两维）
    if features.shape[1] >= 2:
        label_style = params.get("label_style", {})
        fig2, ax2 = plt.subplots()
        ax2.scatter(features.iloc[:, 0], features.iloc[:, 1], alpha=0.6)
        ax2.set(
            title=label_style.get("title", "主成分投影") or "主成分投影",
            xlabel=label_style.get("x", "第一主成分") or "第一主成分",
            ylabel=label_style.get("y", "第二主成分") or "第二主成分"
        )
        figures["component_projection"] = fig2
    
    return figures