# visualization/plots/linear_regression.py
"""
Src/data_analyzer/visualization/plots/linearregression.py
线性回归可视化模块

该模块提供线性回归模型的可视化功能，
包括回归线和数据点的可视化展示。
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure

@plot_registry.register("regression", "linearregression")
def plot_linear_regression(params: Dict[str, Any]) -> Dict[str, Figure]:
    """线性回归可视化"""
    figures = {}
    target = params["target"]
    predict = params["predict"]
    
    # 样式设置
    label_style = params.get("label_style", {})
    shape_style = params.get("shape_style", {})
    point_size = shape_style.get("points", {}).get("size", 30)
    point_colors = shape_style.get("points", {}).get("colors", ["blue"])
    
    # 真实值 vs 预测值
    fig1, ax1 = plt.subplots()
    ax1.scatter(target, predict, s=point_size, alpha=0.6, color=point_colors[0])
    
    # 添加对角线
    min_val = min(min(target), min(predict))
    max_val = max(max(target), max(predict))
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--')
    
    ax1.set(
        title=label_style.get("title", "真实值 vs 预测值") or "真实值 vs 预测值",
        xlabel=label_style.get("x", "真实值"),
        ylabel=label_style.get("y", "预测值")
    )
    figures["pred_vs_actual"] = fig1

    # 残差图
    residuals = target - predict
    fig2, ax2 = plt.subplots()
    ax2.scatter(predict, residuals, s=point_size, alpha=0.6, color=point_colors[0])
    ax2.axhline(y=0, color='r', linestyle='--')
    ax2.set(
        title="残差图",
        xlabel="预测值",
        ylabel="残差"
    )
    figures["residual_plot"] = fig2
    
    return figures