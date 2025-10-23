"""
绘制线性模型系数工具函数
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_coefficients(coefficients, feature_names=None, top_n=20, figsize=(10, 6)):
    """
    绘制线性模型系数图
    
    Args:
        coefficients: 系数数组
        feature_names: 特征名称列表
        top_n: 显示前N个系数特征
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 获取特征名称
    if feature_names is None:
        feature_names = [f'特征{i}' for i in range(len(coefficients))]
    
    # 确保特征名称和系数数组长度一致
    if len(feature_names) != len(coefficients):
        raise ValueError("特征名称数量与系数数量不匹配")
    
    # 排序系数（按绝对值）
    sorted_idx = np.argsort(np.abs(coefficients))[::-1]
    
    # 只显示前top_n个特征
    if len(sorted_idx) > top_n:
        sorted_idx = sorted_idx[:top_n]
    
    sorted_coefficients = coefficients[sorted_idx]
    sorted_features = [feature_names[i] for i in sorted_idx]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    y_pos = np.arange(len(sorted_coefficients))
    colors = ['red' if c < 0 else 'blue' for c in sorted_coefficients]
    
    ax.barh(y_pos, sorted_coefficients, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_features)
    ax.set_xlabel('系数值')
    ax.set_title('模型系数')
    
    return fig, ax