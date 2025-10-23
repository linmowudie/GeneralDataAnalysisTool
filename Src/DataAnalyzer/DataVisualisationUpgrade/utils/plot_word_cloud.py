"""
生成词云图工具函数
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_word_cloud(frequencies, figsize=(10, 6)):
    """
    生成词云图（简易版本，使用条形图代替）
    
    Args:
        frequencies: 词频字典 {'词语': 频率}
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 按频率排序并取前20个
    sorted_items = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)[:20]
    words, freqs = zip(*sorted_items) if sorted_items else ([], [])
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制水平条形图
    y_pos = np.arange(len(words))
    ax.barh(y_pos, freqs)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(words)
    ax.invert_yaxis()  # 最高频率在上
    ax.set_xlabel('频率')
    ax.set_title('词频统计（词云图替代）')
    
    return fig, ax