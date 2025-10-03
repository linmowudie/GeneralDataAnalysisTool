"""
Src/DataAnalyzer/visualization/interactive_plots/three_d.py
3D交互式可视化模块

该模块提供基于Plotly的3D数据交互式可视化功能。
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any
from ..interactive_registry import interactive_plot_registry
import logging

logger = logging.getLogger(__name__)

@interactive_plot_registry.register("transformer", "3d")
def plot_3d_scatter_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """3D交互式散点图可视化"""
    figures = {}
    feature = params["feature"]
    
    try:
        if feature.shape[1] < 3:
            raise ValueError("需要至少3个特征来进行3D可视化")
        
        # 创建DataFrame用于绘图
        plot_data = pd.DataFrame({
            'x': feature.iloc[:, 0],
            'y': feature.iloc[:, 1],
            'z': feature.iloc[:, 2]
        })
        
        if hasattr(feature, 'columns'):
            plot_data.columns = [
                feature.columns[0] if len(feature.columns) > 0 else "X",
                feature.columns[1] if len(feature.columns) > 1 else "Y",
                feature.columns[2] if len(feature.columns) > 2 else "Z"
            ]
        
        # 获取颜色映射（如果有）
        color = params.get("target", None)
        
        # 创建3D散点图
        if color is not None:
            plot_data['color'] = color
            fig = px.scatter_3d(plot_data, 
                               x=plot_data.columns[0], 
                               y=plot_data.columns[1], 
                               z=plot_data.columns[2],
                               color='color',
                               title='3D Scatter Plot')
        else:
            fig = px.scatter_3d(plot_data, 
                               x=plot_data.columns[0], 
                               y=plot_data.columns[1], 
                               z=plot_data.columns[2],
                               title='3D Scatter Plot')
        
        # 设置标签
        label_style = params.get("label_style", {})
        fig.update_layout(
            scene=dict(
                xaxis_title=label_style.get("x", plot_data.columns[0]),
                yaxis_title=label_style.get("y", plot_data.columns[1]),
                zaxis_title=label_style.get("z", plot_data.columns[2])
            ),
            title=label_style.get("title", "3D Scatter Plot")
        )
        
        figures["3d_scatter_interactive"] = fig
        
    except Exception as e:
        logger.error(f"3D交互式散点图可视化过程中出现错误: {str(e)}")
        raise
    
    return figures

@interactive_plot_registry.register("transformer", "surface")
def plot_3d_surface_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """3D交互式曲面图可视化"""
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
        fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
        
        # 设置标签
        label_style = params.get("label_style", {})
        fig.update_layout(
            scene=dict(
                xaxis_title=label_style.get("x", "X"),
                yaxis_title=label_style.get("y", "Y"),
                zaxis_title=label_style.get("z", "Z")
            ),
            title=label_style.get("title", "3D Surface Plot")
        )
        
        figures["3d_surface_interactive"] = fig
        
    except Exception as e:
        logger.error(f"3D交互式曲面图可视化过程中出现错误: {str(e)}")
        raise
    
    return figures