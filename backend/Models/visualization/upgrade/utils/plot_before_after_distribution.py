"""
绘制变换前后分布对比工具函数
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_before_after_distribution(X_before, X_after, feature_names=None, figsize=(12, 6)):
    """
    绘制变换前后分布对比图
    
    Args:
        X_before: 变换前数据
        X_after: 变换后数据
        feature_names: 特征名称列表
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 确保数据是numpy数组
    X_before = np.array(X_before)
    X_after = np.array(X_after)
    
    # 获取特征数量
    if X_before.ndim == 1:
        n_features = 1
        X_before = X_before.reshape(-1, 1)
        X_after = X_after.reshape(-1, 1)
    else:
        n_features = X_before.shape[1]
    
    # 获取特征名称
    if feature_names is None:
        feature_names = [f'特征{i}' for i in range(n_features)]
    
    # 创建图表
    fig, axes = plt.subplots(nrows=2, ncols=n_features, figsize=figsize)
    
    # 如果只有一个特征，调整axes的形状
    if n_features == 1:
        axes = axes.reshape(-1, 1)
    
    # 绘制每个特征的变换前后分布
    for i in range(n_features):
        # 变换前分布
        axes[0, i].hist(X_before[:, i], bins=30, alpha=0.7, color='blue')
        axes[0, i].set_title(f'{feature_names[i]} (变换前)')
        if i == 0:
            axes[0, i].set_ylabel('频率')
        
        # 变换后分布
        axes[1, i].hist(X_after[:, i], bins=30, alpha=0.7, color='green')
        axes[1, i].set_title(f'{feature_names[i]} (变换后)')
        axes[1, i].set_xlabel('值')
        if i == 0:
            axes[1, i].set_ylabel('频率')
    
    plt.tight_layout()
    
    return fig, axes