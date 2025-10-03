"""
Src/DataAnalyzer/visualization/interactive_plots/kmeans.py
K-Means聚类交互式可视化模块

该模块提供K-Means聚类模型的交互式可视化功能，
包括聚类结果散点图的交互式绘制。
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any
from ..interactive_registry import interactive_plot_registry
import logging

logger = logging.getLogger(__name__)

@interactive_plot_registry.register("clustering", "kmeans")
def plot_kmeans_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """K-Means聚类交互式可视化"""
    figures = {}
    feature = params["feature"]
    model = params.get("model_specific", {}).get("trained_model")
    
    try:
        if feature.shape[1] < 2:
            # 特征维度不足二维，只画直方图
            fig = px.histogram(feature, x=feature.columns[0] if hasattr(feature, 'columns') else feature.columns[0],
                              title="Cluster Histogram (1-D)")
            figures["histogram_1d_interactive"] = fig
            return figures

        # 获取标签
        labels = model.labels_ if model and hasattr(model, 'labels_') else np.zeros(len(feature))
        
        # 创建DataFrame用于绘图
        plot_data = pd.DataFrame({
            'x': feature.iloc[:, 0],
            'y': feature.iloc[:, 1],
            'cluster': labels
        })
        
        if hasattr(feature, 'columns'):
            x_label = feature.columns[0] if len(feature.columns) > 0 else "Feature 1"
            y_label = feature.columns[1] if len(feature.columns) > 1 else "Feature 2"
            plot_data.columns = [x_label, y_label, 'cluster']

        # 二维散点图
        fig1 = px.scatter(plot_data, x=plot_data.columns[0], y=plot_data.columns[1], 
                         color='cluster', title='KMeans Clustering Results',
                         labels={plot_data.columns[0]: x_label, plot_data.columns[1]: y_label})
        
        # 绘制聚类中心
        centers = model.cluster_centers_ if model and hasattr(model, 'cluster_centers_') else None
        if centers is not None:
            fig1.add_trace(go.Scatter(
                x=centers[:, 0],
                y=centers[:, 1],
                mode='markers',
                marker=dict(
                    color='red',
                    size=20,
                    symbol='x',
                    line=dict(width=3, color='DarkSlateGrey')
                ),
                name='Cluster Centers'
            ))
            
        figures["cluster_scatter_interactive"] = fig1

        # 聚类大小条形图
        if model and hasattr(model, 'labels_'):
            cluster_counts = pd.Series(model.labels_).value_counts().sort_index()
            cluster_data = pd.DataFrame({
                'Cluster': [f'Cluster {i}' for i in cluster_counts.index],
                'Count': cluster_counts.values
            })
            
            fig2 = px.bar(cluster_data, x='Cluster', y='Count',
                         title='Cluster Sizes')
            
            # 添加数值标签
            fig2.update_traces(text=cluster_data['Count'], textposition='outside')
            
            figures["cluster_sizes_interactive"] = fig2
            
        # 如果有3个或更多特征，创建成对特征图
        if feature.shape[1] >= 3 and model and hasattr(model, 'labels_'):
            plot_data_3d = pd.DataFrame({
                'x': feature.iloc[:, 2],  # 第三个特征
                'y': feature.iloc[:, 1],  # 第二个特征
                'cluster': labels
            })
            
            if hasattr(feature, 'columns'):
                x_label_3d = feature.columns[2] if len(feature.columns) > 2 else "Feature 3"
                y_label_3d = feature.columns[1] if len(feature.columns) > 1 else "Feature 2"
                plot_data_3d.columns = [x_label_3d, y_label_3d, 'cluster']
            
            fig3 = px.scatter(plot_data_3d, x=plot_data_3d.columns[0], y=plot_data_3d.columns[1],
                             color='cluster', title='KMeans Clustering (Features 3 vs 2)',
                             labels={plot_data_3d.columns[0]: x_label_3d, plot_data_3d.columns[1]: y_label_3d})
            
            figures["cluster_scatter_3v2_interactive"] = fig3

    except Exception as e:
        logger.error(f"KMeans聚类交互式可视化过程中出现错误: {str(e)}")
        raise
    
    return figures