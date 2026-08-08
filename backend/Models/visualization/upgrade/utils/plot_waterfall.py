"""
绘制瀑布图工具函数
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_waterfall(contributions, labels=None, title="瀑布图", figsize=(10, 6)):
    """
    绘制瀑布图，用于显示各部分对总体的贡献
    
    Args:
        contributions: 贡献值列表
        labels: 标签列表
        title: 图表标题
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 确保贡献值是numpy数组
    contributions = np.array(contributions)
    
    # 获取标签
    if labels is None:
        labels = [f'部分{i+1}' for i in range(len(contributions))]
    
    # 计算累积值
    cumulative = np.cumsum(contributions)
    initial_value = 0
    final_value = cumulative[-1] if len(cumulative) > 0 else 0
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制柱状图
    x_pos = np.arange(len(contributions))
    
    # 确定每个柱子的颜色（正值为绿色，负值为红色）
    colors = ['green' if x >= 0 else 'red' for x in contributions]
    
    # 绘制柱子
    ax.bar(x_pos, contributions, color=colors, bottom=np.concatenate([[initial_value], cumulative[:-1]]))
    
    # 添加标签
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel('值')
    ax.set_title(title)
    
    # 添加网格
    ax.grid(True, alpha=0.3)
    
    return fig, ax