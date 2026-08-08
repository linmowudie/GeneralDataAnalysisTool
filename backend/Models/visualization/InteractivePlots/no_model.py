"""
Src/DataAnalyzer/VisualizationModule/InteractivePlots/no_model.py
无模型交互式可视化模块

该模块提供无特定模型的通用交互式可视化功能，
支持散点图、折线图、柱状图等各种基本图表类型。
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any
from ..interactive_registry import interactive_plot_registry
import logging

logger = logging.getLogger(__name__)

@interactive_plot_registry.register("transformer", "no_model")
def plot_no_model_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """
    无模型通用交互式可视化函数
    
    支持的图表类型：
    - scatter: 散点图
    - line: 折线图
    - bar: 柱状图
    - histogram: 直方图
    - box: 箱线图
    - heatmap: 热力图
    - pie: 饼图
    """
    figures = {}
    chart_type = params.get("chart_type", "scatter").lower()
    
    try:
        if chart_type == "scatter":
            figures = _plot_scatter_interactive(params)
        elif chart_type == "line":
            figures = _plot_line_interactive(params)
        elif chart_type == "bar":
            figures = _plot_bar_interactive(params)
        elif chart_type == "histogram":
            figures = _plot_histogram_interactive(params)
        elif chart_type == "box":
            figures = _plot_box_interactive(params)
        elif chart_type == "heatmap":
            figures = _plot_heatmap_interactive(params)
        elif chart_type == "pie":
            figures = _plot_pie_interactive(params)
        else:
            logger.warning(f"Unsupported chart type: {chart_type}")
            # 默认绘制散点图
            figures = _plot_scatter_interactive(params)
            
    except Exception as e:
        logger.error(f"Error in no_model interactive visualization: {str(e)}")
        raise
    
    return figures

def _plot_scatter_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """绘制交互式散点图"""
    figures = {}
    feature = params["feature"]
    target = params.get("target")
    
    if feature.shape[1] >= 2:
        x_data = feature.iloc[:, 0]
        y_data = feature.iloc[:, 1]
        
        if target is not None:
            fig = px.scatter(x=x_data, y=y_data, color=target,
                           title=params.get("label_style", {}).get("title", "Interactive Scatter Plot"))
        else:
            fig = px.scatter(x=x_data, y=y_data,
                           title=params.get("label_style", {}).get("title", "Interactive Scatter Plot"))
            
        # 设置轴标签
        fig.update_xaxes(title_text=feature.columns[0] if hasattr(feature, 'columns') else 'X')
        fig.update_yaxes(title_text=feature.columns[1] if hasattr(feature, 'columns') and len(feature.columns) > 1 else 'Y')
        
        figures["interactive_scatter_plot"] = fig
    else:
        logger.warning("Need at least 2 features for scatter plot")
        
    return figures

def _plot_line_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """绘制交互式折线图"""
    figures = {}
    feature = params["feature"]
    
    if feature.shape[1] >= 1:
        # 创建用于绘图的DataFrame
        plot_data = pd.DataFrame()
        x_data = list(range(len(feature)))
        
        if feature.shape[1] == 1:
            y_data = feature.iloc[:, 0]
            plot_data['x'] = x_data
            plot_data['y'] = y_data
            fig = px.line(plot_data, x='x', y='y',
                         title=params.get("label_style", {}).get("title", "Interactive Line Plot"))
            fig.update_yaxes(title_text=feature.columns[0] if hasattr(feature, 'columns') else 'Value')
        else:
            # 多列数据，每列一条线
            plot_data['x'] = x_data
            for i in range(feature.shape[1]):
                col_name = feature.columns[i] if hasattr(feature, 'columns') else f'Series {i}'
                plot_data[col_name] = feature.iloc[:, i]
                
            # 使用melt重塑数据以便于绘图
            melted_data = pd.melt(plot_data, id_vars=['x'], var_name='series', value_name='value')
            fig = px.line(melted_data, x='x', y='value', color='series',
                         title=params.get("label_style", {}).get("title", "Interactive Line Plot"))
            
        fig.update_xaxes(title_text='Index')
        figures["interactive_line_plot"] = fig
    else:
        logger.warning("No data for line plot")
        
    return figures

def _plot_bar_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """绘制交互式柱状图"""
    figures = {}
    feature = params["feature"]
    
    if feature.shape[1] >= 1:
        if feature.shape[1] == 1:
            # 单列数据，绘制该列的值分布
            y_data = feature.iloc[:, 0]
            x_labels = feature.index if hasattr(feature, 'index') else list(range(len(y_data)))
            
            fig = px.bar(x=x_labels, y=y_data,
                        title=params.get("label_style", {}).get("title", "Interactive Bar Plot"))
            fig.update_xaxes(title_text='Index')
            fig.update_yaxes(title_text=feature.columns[0] if hasattr(feature, 'columns') else 'Value')
        else:
            # 多列数据，绘制每列的平均值
            means = feature.mean()
            x_labels = feature.columns if hasattr(feature, 'columns') else [f'Column {i}' for i in range(len(means))]
            
            fig = px.bar(x=x_labels, y=means,
                        title=params.get("label_style", {}).get("title", "Interactive Bar Plot"))
            fig.update_xaxes(title_text='Features')
            fig.update_yaxes(title_text='Mean Value')
            
        figures["interactive_bar_plot"] = fig
    else:
        logger.warning("No data for bar plot")
        
    return figures

def _plot_histogram_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """绘制交互式直方图"""
    figures = {}
    feature = params["feature"]
    
    if feature.shape[1] >= 1:
        if feature.shape[1] == 1:
            # 单列数据
            data = feature.iloc[:, 0]
            fig = px.histogram(x=data,
                              title=params.get("label_style", {}).get("title", "Interactive Histogram"))
            fig.update_xaxes(title_text=feature.columns[0] if hasattr(feature, 'columns') else 'Value')
            fig.update_yaxes(title_text='Frequency')
            figures["interactive_histogram_plot"] = fig
        else:
            # 多列数据，创建子图
            fig = go.Figure()
            
            for i in range(min(5, feature.shape[1])):  # 最多显示5个直方图
                col_name = feature.columns[i] if hasattr(feature, 'columns') else f'Column {i}'
                data = feature.iloc[:, i]
                fig.add_trace(go.Histogram(x=data, name=col_name, opacity=0.7))
                
            fig.update_layout(
                title=params.get("label_style", {}).get("title", "Interactive Histogram"),
                barmode='overlay',
                xaxis_title='Value',
                yaxis_title='Frequency'
            )
            
            figures["interactive_histogram_plot"] = fig
    else:
        logger.warning("No data for histogram plot")
        
    return figures

def _plot_box_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """绘制交互式箱线图"""
    figures = {}
    feature = params["feature"]
    
    if feature.shape[1] >= 1:
        if feature.shape[1] == 1:
            # 单列数据
            data = feature.iloc[:, 0]
            fig = px.box(y=data,
                        title=params.get("label_style", {}).get("title", "Interactive Box Plot"))
            fig.update_yaxes(title_text=feature.columns[0] if hasattr(feature, 'columns') else 'Value')
        else:
            # 多列数据
            # 创建用于绘图的DataFrame
            plot_data = pd.DataFrame()
            for i in range(feature.shape[1]):
                col_name = feature.columns[i] if hasattr(feature, 'columns') else f'Column {i}'
                plot_data[col_name] = feature.iloc[:, i]
                
            fig = px.box(plot_data,
                        title=params.get("label_style", {}).get("title", "Interactive Box Plot"))
            fig.update_yaxes(title_text='Value')
            
        figures["interactive_box_plot"] = fig
    else:
        logger.warning("No data for box plot")
        
    return figures

def _plot_heatmap_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """绘制交互式热力图"""
    figures = {}
    feature = params["feature"]
    
    if feature.shape[1] >= 2:
        # 对于热力图，我们使用feature的相关性矩阵
        corr = feature.corr() if hasattr(feature, 'corr') else np.corrcoef(feature.T)
        
        # 获取标签
        labels = feature.columns if hasattr(feature, 'columns') else [f'Col {i}' for i in range(feature.shape[1])]
        
        fig = px.imshow(corr,
                       labels=dict(x="Features", y="Features", color="Correlation"),
                       x=labels,
                       y=labels,
                       title=params.get("label_style", {}).get("title", "Interactive Heatmap"))
        
        figures["interactive_heatmap_plot"] = fig
    else:
        logger.warning("Need at least 2 features for heatmap")
        
    return figures

def _plot_pie_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """绘制交互式饼图"""
    figures = {}
    feature = params["feature"]
    
    if feature.shape[1] >= 1:
        if feature.shape[1] == 1:
            # 单列数据，使用值作为饼图的各个部分
            data = feature.iloc[:, 0]
            labels = feature.index if hasattr(feature, 'index') else [f'Part {i}' for i in range(len(data))]
            
            fig = px.pie(values=data, names=labels,
                        title=params.get("label_style", {}).get("title", "Interactive Pie Chart"))
        else:
            # 多列数据，使用每列的平均值
            means = feature.mean()
            labels = feature.columns if hasattr(feature, 'columns') else [f'Column {i}' for i in range(len(means))]
            
            fig = px.pie(values=means, names=labels,
                        title=params.get("label_style", {}).get("title", "Interactive Pie Chart"))
            
        figures["interactive_pie_chart"] = fig
    else:
        logger.warning("No data for pie chart")
        
    return figures