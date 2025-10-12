# visualization/plots/no_model.py
"""
Src/DataAnalyzer/VisualizationModule/Plots/no_model.py
无模型可视化模块

该模块提供无特定模型的通用可视化功能，
支持散点图、折线图、柱状图等各种基本图表类型。
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)

@plot_registry.register("transformer", "no_model")
def plot_no_model(params: Dict[str, Any]) -> Dict[str, Figure]:
    """
    无模型通用可视化函数
    
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
            figures = _plot_scatter(params)
        elif chart_type == "line":
            figures = _plot_line(params)
        elif chart_type == "bar":
            figures = _plot_bar(params)
        elif chart_type == "histogram":
            figures = _plot_histogram(params)
        elif chart_type == "box":
            figures = _plot_box(params)
        elif chart_type == "heatmap":
            figures = _plot_heatmap(params)
        elif chart_type == "pie":
            figures = _plot_pie(params)
        else:
            logger.warning(f"Unsupported chart type: {chart_type}")
            # 默认绘制散点图
            figures = _plot_scatter(params)
            
    except Exception as e:
        logger.error(f"Error in no_model visualization: {str(e)}")
        raise
    
    return figures

def _plot_scatter(params: Dict[str, Any]) -> Dict[str, Figure]:
    """绘制散点图"""
    figures = {}
    feature = params["feature"]
    target = params.get("target")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if feature.shape[1] >= 2:
        x_data = feature.iloc[:, 0]
        y_data = feature.iloc[:, 1]
        
        if target is not None:
            scatter = ax.scatter(x_data, y_data, c=target, cmap='viridis')
            plt.colorbar(scatter, ax=ax)
        else:
            ax.scatter(x_data, y_data)
            
        ax.set_xlabel(feature.columns[0] if hasattr(feature, 'columns') else 'X')
        ax.set_ylabel(feature.columns[1] if hasattr(feature, 'columns') and len(feature.columns) > 1 else 'Y')
        ax.set_title(params.get("label_style", {}).get("title", "Scatter Plot"))
    else:
        logger.warning("Need at least 2 features for scatter plot")
        
    figures["scatter_plot"] = fig
    return figures

def _plot_line(params: Dict[str, Any]) -> Dict[str, Figure]:
    """绘制折线图"""
    figures = {}
    feature = params["feature"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if feature.shape[1] >= 1:
        x_data = range(len(feature))
        if feature.shape[1] == 1:
            y_data = feature.iloc[:, 0]
            ax.plot(x_data, y_data)
            ax.set_ylabel(feature.columns[0] if hasattr(feature, 'columns') else 'Value')
        else:
            for i in range(feature.shape[1]):
                y_data = feature.iloc[:, i]
                ax.plot(x_data, y_data, label=feature.columns[i] if hasattr(feature, 'columns') else f'Series {i}')
            ax.legend()
            
        ax.set_xlabel('Index')
        ax.set_title(params.get("label_style", {}).get("title", "Line Plot"))
    else:
        logger.warning("No data for line plot")
        
    figures["line_plot"] = fig
    return figures

def _plot_bar(params: Dict[str, Any]) -> Dict[str, Figure]:
    """绘制柱状图"""
    figures = {}
    feature = params["feature"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if feature.shape[1] >= 1:
        if feature.shape[1] == 1:
            # 单列数据，绘制该列的值分布
            y_data = feature.iloc[:, 0]
            x_labels = feature.index if hasattr(feature, 'index') else list(range(len(y_data)))
            ax.bar(range(len(y_data)), y_data)
            ax.set_xticks(range(len(y_data)))
            ax.set_xticklabels([str(label) for label in x_labels], rotation=45)
            ax.set_ylabel(feature.columns[0] if hasattr(feature, 'columns') else 'Value')
        else:
            # 多列数据，绘制每列的平均值
            means = feature.mean()
            ax.bar(range(len(means)), means)
            ax.set_xticks(range(len(means)))
            ax.set_xticklabels([str(col) for col in (feature.columns if hasattr(feature, 'columns') else [f'Column {i}' for i in range(len(means))])], rotation=45)
            ax.set_ylabel('Mean Value')
            
        ax.set_title(params.get("label_style", {}).get("title", "Bar Plot"))
    else:
        logger.warning("No data for bar plot")
        
    figures["bar_plot"] = fig
    return figures

def _plot_histogram(params: Dict[str, Any]) -> Dict[str, Figure]:
    """绘制直方图"""
    figures = {}
    feature = params["feature"]
    
    if feature.shape[1] >= 1:
        n_cols = min(4, feature.shape[1])  # 最多显示4个子图
        cols = feature.columns[:n_cols] if hasattr(feature, 'columns') else range(n_cols)
        
        fig, axes = plt.subplots(1, n_cols, figsize=(5*n_cols, 5))
        if n_cols == 1:
            axes = [axes]
            
        for i, col in enumerate(cols):
            data = feature.iloc[:, i] if not hasattr(feature, 'columns') else feature[col]
            axes[i].hist(data, bins=30)
            axes[i].set_title(f'Histogram of {col}' if hasattr(feature, 'columns') else f'Histogram of Column {i}')
            axes[i].set_xlabel('Value')
            axes[i].set_ylabel('Frequency')
            
        plt.tight_layout()
        figures["histogram_plot"] = fig
    else:
        logger.warning("No data for histogram plot")
        
    return figures

def _plot_box(params: Dict[str, Any]) -> Dict[str, Figure]:
    """绘制箱线图"""
    figures = {}
    feature = params["feature"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if feature.shape[1] >= 1:
        if feature.shape[1] == 1:
            # 单列数据
            data = feature.iloc[:, 0]
            ax.boxplot(data)
            ax.set_ylabel(feature.columns[0] if hasattr(feature, 'columns') else 'Value')
        else:
            # 多列数据
            data = [feature.iloc[:, i] for i in range(feature.shape[1])]
            ax.boxplot(data)
            ax.set_xticklabels([str(col) for col in (feature.columns if hasattr(feature, 'columns') else [f'Column {i}' for i in range(feature.shape[1])])])
            ax.set_ylabel('Value')
            
        ax.set_title(params.get("label_style", {}).get("title", "Box Plot"))
    else:
        logger.warning("No data for box plot")
        
    figures["box_plot"] = fig
    return figures

def _plot_heatmap(params: Dict[str, Any]) -> Dict[str, Figure]:
    """绘制热力图"""
    figures = {}
    feature = params["feature"]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if feature.shape[1] >= 2:
        # 对于热力图，我们使用feature的相关性矩阵
        corr = feature.corr() if hasattr(feature, 'corr') else np.corrcoef(feature.T)
        im = ax.imshow(corr, cmap='coolwarm', aspect='auto')
        
        # 添加颜色条
        plt.colorbar(im, ax=ax)
        
        # 设置标签
        if hasattr(feature, 'columns'):
            ax.set_xticks(range(len(feature.columns)))
            ax.set_yticks(range(len(feature.columns)))
            ax.set_xticklabels([str(col) for col in feature.columns], rotation=45)
            ax.set_yticklabels([str(col) for col in feature.columns])
        else:
            ax.set_xticks(range(feature.shape[1]))
            ax.set_yticks(range(feature.shape[1]))
            ax.set_xticklabels([f'Col {i}' for i in range(feature.shape[1])], rotation=45)
            ax.set_yticklabels([f'Col {i}' for i in range(feature.shape[1])])
            
        ax.set_title(params.get("label_style", {}).get("title", "Heatmap"))
    else:
        logger.warning("Need at least 2 features for heatmap")
        
    figures["heatmap_plot"] = fig
    return figures

def _plot_pie(params: Dict[str, Any]) -> Dict[str, Figure]:
    """绘制饼图"""
    figures = {}
    feature = params["feature"]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    if feature.shape[1] >= 1:
        if feature.shape[1] == 1:
            # 单列数据，使用值作为饼图的各个部分
            data = feature.iloc[:, 0]
            labels = feature.index if hasattr(feature, 'index') else [f'Part {i}' for i in range(len(data))]
            ax.pie(data, labels=[str(label) for label in labels], autopct='%1.1f%%')
        else:
            # 多列数据，使用每列的平均值
            means = feature.mean()
            ax.pie(means, labels=[str(col) for col in (feature.columns if hasattr(feature, 'columns') else [f'Column {i}' for i in range(len(means))])], autopct='%1.1f%%')
            
        ax.set_title(params.get("label_style", {}).get("title", "Pie Chart"))
    else:
        logger.warning("No data for pie chart")
        
    figures["pie_chart"] = fig
    return figures