"""
绘制轮廓系数图工具函数
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_samples, silhouette_score


def plot_silhouette(X, labels, figsize=(10, 6)):
    """
    绘制轮廓系数图
    
    Args:
        X: 特征数据
        labels: 聚类标签
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 计算轮廓系数
    silhouette_avg = silhouette_score(X, labels)
    sample_silhouette_values = silhouette_samples(X, labels)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    y_lower = 10
    n_clusters = len(np.unique(labels))
    
    for i in range(n_clusters):
        # 获取第i个簇的轮廓系数并排序
        ith_cluster_silhouette_values = sample_silhouette_values[labels == i]
        ith_cluster_silhouette_values.sort()
        
        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i
        
        # 修复: 使用 get_cmap 函数获取 colormap，避免静态类型检查错误
        color = plt.cm.get_cmap('nipy_spectral')(float(i) / n_clusters)
        ax.fill_betweenx(np.arange(y_lower, y_upper),
                         0, ith_cluster_silhouette_values,
                         facecolor=color, edgecolor=color, alpha=0.7)
        
        # 在簇中间标记簇号
        ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
        
        # 为下一个簇计算新的y_lower
        y_lower = y_upper + 10  # 10为簇间的间隙
    
    # 添加平均轮廓系数线
    ax.axvline(x=silhouette_avg, color="red", linestyle="--", 
               label=f'平均轮廓系数: {silhouette_avg:.2f}')
    
    ax.set_xlabel('轮廓系数值')
    ax.set_ylabel('簇标签')
    ax.set_title('轮廓系数图')
    ax.legend()
    
    return fig, ax