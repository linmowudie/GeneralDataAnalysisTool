"""
绘制仪表盘图工具函数
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def plot_gauge_chart(value, max_value=100, title="仪表盘图", figsize=(8, 6)):
    """
    绘制仪表盘图
    
    Args:
        value: 当前值
        max_value: 最大值
        title: 图表标题
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 计算百分比
    percentage = min(100, max(0, value / max_value * 100))
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 创建仪表盘
    # 外圈（完整的圆环）
    outer_ring = patches.Circle((0, 0), 0.5, color='lightgray', fill=False, linewidth=10)
    ax.add_artist(outer_ring)
    
    # 内圈（表示当前值的部分圆环）
    angle = percentage * 3.6  # 转换为角度
    inner_ring = patches.Wedge((0, 0), 0.4, 90, 90-angle, color='lightblue', fill=False, linewidth=10)
    ax.add_artist(inner_ring)
    
    # 添加数值文本
    ax.text(0, 0, f'{value}/{max_value}', ha='center', va='center', fontsize=20)
    ax.text(0, -0.2, f'{percentage:.1f}%', ha='center', va='center', fontsize=16)
    
    # 设置坐标轴
    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(-0.6, 0.6)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title)
    
    return fig, ax