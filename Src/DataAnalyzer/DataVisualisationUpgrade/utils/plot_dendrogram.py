"""
绘制树状图工具函数
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram


def plot_dendrogram(model, figsize=(12, 8)):
    """
    绘制层次聚类树状图
    
    Args:
        model: 层次聚类模型（应包含linkage_matrix属性）或linkage矩阵
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制树状图
    if hasattr(model, 'linkage_matrix'):
        # 如果模型有linkage_matrix属性
        dendrogram(model.linkage_matrix, ax=ax)
    else:
        # 假设model本身就是linkage矩阵
        dendrogram(model, ax=ax)
    
    ax.set_xlabel('样本索引或聚类大小')
    ax.set_ylabel('距离')
    ax.set_title('层次聚类树状图')
    
    return fig, ax