"""
Src/DataAnalyzer/VisualizationModule/InteractivePlots/featureimportance.py
特征重要性交互式可视化模块

该模块提供模型特征重要性的交互式可视化功能，
包括特征重要性条形图和排序功能。
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any
from ..interactive_registry import interactive_plot_registry
import logging

logger = logging.getLogger(__name__)

@interactive_plot_registry.register("analysis", "featureimportance")
def plot_feature_importance_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """特征重要性交互式可视化"""
    figures = {}
    feature = params["feature"]
    
    try:
        # 检查数据格式
        if 'feature' in feature.columns and 'importance' in feature.columns:
            # 数据已经是正确格式
            importance_df = feature.sort_values('importance', ascending=False)
        else:
            # 假设feature列是特征名，其他列包含重要性值
            feature_names = feature.columns
            importances = feature.iloc[0].values  # 假设第一行包含重要性值
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
        
        # 特征重要性条形图
        fig1 = px.bar(importance_df, x='importance', y='feature', orientation='h',
                     title='特征重要性分析',
                     labels={'importance': '重要性', 'feature': '特征'})
        
        # 添加数值标签
        fig1.update_traces(texttemplate='%{x:.3f}', textposition='outside')
        
        # 更新布局
        fig1.update_layout(
            height=max(400, len(importance_df) * 20),  # 根据特征数量调整高度
            yaxis={'categoryorder': 'total ascending'}  # 按值排序
        )
        
        figures["feature_importance_bar_interactive"] = fig1

        # 特征重要性饼图（仅显示Top N）
        top_n = params.get('top_n', 10)
        top_features = importance_df.head(top_n)
        
        fig2 = px.pie(top_features, values='importance', names='feature',
                     title=f'Top {top_n} 特征重要性分布')
        
        figures["feature_importance_pie_interactive"] = fig2

    except Exception as e:
        logger.error(f"特征重要性交互式可视化过程中出现错误: {str(e)}")
        raise
    
    return figures