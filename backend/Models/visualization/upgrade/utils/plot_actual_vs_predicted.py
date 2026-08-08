"""
绘制真实值vs预测值散点图工具函数
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_actual_vs_predicted(y_true, y_pred, figsize=(8, 6)):
    """
    绘制真实值vs预测值散点图
    
    Args:
        y_true: 真实值
        y_pred: 预测值
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制散点图
    ax.scatter(y_true, y_pred, alpha=0.7)
    
    # 绘制完美预测线
    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
    
    ax.set_xlabel('真实值')
    ax.set_ylabel('预测值')
    ax.set_title('真实值 vs 预测值')
    
    return fig, ax