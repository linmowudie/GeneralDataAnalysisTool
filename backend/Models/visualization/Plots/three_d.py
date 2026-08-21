"""
Src/DataAnalyzer/VisualizationModule/Plots/three_d.py
3D可视化模块

该模块提供3D数据可视化功能，
包括3D散点图、3D曲面图等。
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numpy as np
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)

@plot_registry.register("transformer", "3d")
def plot_3d_scatter(params: Dict[str, Any]) -> Dict[str, Figure]:
    """3D散点图可视化"""
    figures = {}
    feature = params["feature"]
    
    try:
        if feature.shape[1] < 3:
            raise ValueError("需要至少3个特征来进行3D可视化")
        
        # 创建3D散点图
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 获取数据
        x = feature.iloc[:, 0]
        y = feature.iloc[:, 1]
        z = feature.iloc[:, 2]
        
        # 获取颜色映射（如果有）
        colors = params.get("target", None)
        
        # 绘制3D散点图
        if colors is not None:
            scatter = ax.scatter(x, y, z, c=colors, cmap='viridis', alpha=0.7)
            plt.colorbar(scatter)
        else:
            ax.scatter(x, y, z, alpha=0.7)
        
        # 设置标签
        label_style = params.get("label_style", {})
        ax.set_xlabel(label_style.get("x", feature.columns[0] if hasattr(feature, 'columns') else "X"))
        ax.set_ylabel(label_style.get("y", feature.columns[1] if hasattr(feature, 'columns') and len(feature.columns) > 1 else "Y"))
        ax.set_zlabel(label_style.get("z", feature.columns[2] if hasattr(feature, 'columns') and len(feature.columns) > 2 else "Z"))
        ax.set_title(label_style.get("title", "3D Scatter Plot"))
        
        figures["3d_scatter"] = fig
        
    except Exception as e:
        logger.error(f"3D散点图可视化过程中出现错误: {str(e)}")
        raise
    
    return figures

@plot_registry.register("transformer", "surface")
def plot_3d_surface(params: Dict[str, Any]) -> Dict[str, Figure]:
    """3D曲面图可视化"""
    figures = {}
    
    try:
        # 获取数据
        x = params.get("x")
        y = params.get("y")
        z = params.get("z")
        
        if x is None or y is None or z is None:
            raise ValueError("需要提供x、y、z数据进行3D曲面图可视化")
        
        # 创建网格数据
        if len(x.shape) == 1 and len(y.shape) == 1:
            X, Y = np.meshgrid(x, y)
            Z = z
        else:
            X, Y, Z = x, y, z
        
        # 创建3D曲面图
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 绘制3D曲面
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        
        # 添加颜色条
        fig.colorbar(surf, shrink=0.5, aspect=5)
        
        # 设置标签
        label_style = params.get("label_style", {})
        ax.set_xlabel(label_style.get("x", "X"))
        ax.set_ylabel(label_style.get("y", "Y"))
        ax.set_zlabel(label_style.get("z", "Z"))
        ax.set_title(label_style.get("title", "3D Surface Plot"))
        
        figures["3d_surface"] = fig
        
    except Exception as e:
        logger.error(f"3D曲面图可视化过程中出现错误: {str(e)}")
        raise
    
    return figures