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
import logging

logger = logging.getLogger(__name__)

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
    
    try:
        # 真实值 vs 预测值
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.scatter(target, predict, s=point_size, alpha=0.6, color=point_colors[0])
        
        # 添加对角线
        min_val = min(min(target), min(predict))
        max_val = max(max(target), max(predict))
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
        
        # 计算R²值用于显示
        ss_res = np.sum((target - predict) ** 2)
        ss_tot = np.sum((target - np.mean(target)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        ax1.set(
            title=label_style.get("title", f"真实值 vs 预测值 (R² = {r_squared:.3f}") or f"真实值 vs 预测值 (R² = {r_squared:.3f}",
            xlabel=label_style.get("x", "真实值"),
            ylabel=label_style.get("y", "预测值")
        )
        ax1.grid(True, alpha=0.3)
        figures["pred_vs_actual"] = fig1

        # 残差图
        residuals = target - predict
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        ax2.scatter(predict, residuals, s=point_size, alpha=0.6, color=point_colors[0])
        ax2.axhline(y=0, color='r', linestyle='--', linewidth=2)
        ax2.set(
            title="残差图",
            xlabel="预测值",
            ylabel="残差"
        )
        ax2.grid(True, alpha=0.3)
        
        # 添加残差统计信息
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        ax2.text(0.05, 0.95, f'平均残差: {mean_residual:.3f}\n标准差: {std_residual:.3f}', 
                transform=ax2.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        figures["residual_plot"] = fig2
        
    except Exception as e:
        logger.error(f"线性回归可视化过程中出现错误: {str(e)}")
        raise
    
    return figures