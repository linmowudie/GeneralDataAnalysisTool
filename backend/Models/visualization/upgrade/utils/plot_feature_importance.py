"""
绘制特征重要性工具函数
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_feature_importance(importances, feature_names=None, top_n=20, figsize=(10, 6)):
    """
    绘制特征重要性图
    
    Args:
        importances: 特征重要性数组
        feature_names: 特征名称列表
        top_n: 显示前N个重要特征
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 获取特征名称
    if feature_names is None:
        feature_names = [f'特征{i}' for i in range(len(importances))]
    
    # 确保特征名称和重要性数组长度一致
    if len(feature_names) != len(importances):
        raise ValueError("特征名称数量与重要性数量不匹配")
    
    # 排序特征重要性
    sorted_idx = np.argsort(importances)[::-1]
    
    # 只显示前top_n个特征
    if len(sorted_idx) > top_n:
        sorted_idx = sorted_idx[:top_n]
    
    sorted_importances = importances[sorted_idx]
    sorted_features = [feature_names[i] for i in sorted_idx]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    y_pos = np.arange(len(sorted_importances))
    ax.barh(y_pos, sorted_importances)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_features)
    ax.set_xlabel('重要性')
    ax.set_title('特征重要性')
    
    return fig, ax