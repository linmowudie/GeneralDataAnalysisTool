"""
绘制残差图工具函数
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_residuals(y_true, y_pred, figsize=(8, 6)):
    """
    绘制残差图
    
    Args:
        y_true: 真实值
        y_pred: 预测值
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 计算残差
    residuals = y_true - y_pred
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制残差散点图
    ax.scatter(y_pred, residuals, alpha=0.7)
    ax.axhline(y=0, color='r', linestyle='--')
    
    ax.set_xlabel('预测值')
    ax.set_ylabel('残差')
    ax.set_title('残差图')
    
    return fig, ax