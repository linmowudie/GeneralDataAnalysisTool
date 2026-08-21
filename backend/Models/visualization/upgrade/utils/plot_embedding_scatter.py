"""
绘制嵌入空间散点图工具函数
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_embedding_scatter(embedding, labels=None, figsize=(10, 8)):
    """
    绘制嵌入空间散点图（如t-SNE或UMAP结果）
    
    Args:
        embedding: 嵌入数据（通常是2D或3D）
        labels: 标签数据（可选）
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 确保嵌入数据是numpy数组
    embedding = np.array(embedding)
    
    # 检查维度
    if embedding.ndim != 2 or embedding.shape[1] not in [2, 3]:
        raise ValueError("嵌入数据应为二维数组，且特征数应为2或3")
    
    # 创建图表
    if embedding.shape[1] == 2:
        # 2D散点图
        fig, ax = plt.subplots(figsize=figsize)
        
        if labels is not None:
            scatter = ax.scatter(embedding[:, 0], embedding[:, 1], c=labels, cmap='viridis', alpha=0.7)
            plt.colorbar(scatter)
        else:
            ax.scatter(embedding[:, 0], embedding[:, 1], alpha=0.7)
            
        ax.set_xlabel('嵌入维度 1')
        ax.set_ylabel('嵌入维度 2')
        ax.set_title('嵌入空间散点图')
        
    else:
        # 3D散点图
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        if labels is not None:
            scatter = ax.scatter(embedding[:, 0], embedding[:, 1], embedding[:, 2], 
                               c=labels, cmap='viridis', alpha=0.7)
            plt.colorbar(scatter)
        else:
            ax.scatter(embedding[:, 0], embedding[:, 1], embedding[:, 2], alpha=0.7)
            
        ax.set_xlabel('嵌入维度 1')
        ax.set_ylabel('嵌入维度 2')
        ax.set_zlabel('嵌入维度 3')
        ax.set_title('3D嵌入空间散点图')
    
    return fig, ax