"""
绘制缺失值矩阵工具函数
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_missing_value_matrix(data, figsize=(10, 6)):
    """
    绘制缺失值矩阵
    
    Args:
        data: 数据矩阵
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 确保数据是numpy数组
    data = np.array(data)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 创建缺失值掩码（True表示缺失值）
    missing_mask = np.isnan(data) if data.dtype.kind in 'fc' else (data == None)
    
    # 绘制热力图
    im = ax.imshow(missing_mask.T, cmap='Greys', aspect='auto', interpolation='nearest')
    
    ax.set_xlabel('样本')
    ax.set_ylabel('特征')
    ax.set_title('缺失值矩阵（白色表示缺失值）')
    
    return fig, ax