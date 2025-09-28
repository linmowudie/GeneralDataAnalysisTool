"""
Src/DataAnalyzer/visualization/interactive_plots/decisiontreeclassifier.py
决策树分类器交互式可视化模块

该模块提供决策树分类器模型的交互式可视化功能，
包括决策树结构图和特征重要性的交互式展示。
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, Any
from ..interactive_registry import interactive_plot_registry
import logging

logger = logging.getLogger(__name__)

@interactive_plot_registry.register("classification", "decisiontreeclassifier")
def plot_decision_tree_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """决策树分类器交互式可视化"""
    figures = {}
    feature = params["feature"]
    target = params["target"]
    
    try:
        # 特征重要性条形图
        # 模拟特征重要性数据（实际应用中应从训练好的模型中获取）
        feature_names = feature.columns if hasattr(feature, 'columns') else [f'Feature_{i}' for i in range(feature.shape[1])]
        importances = np.abs(np.random.randn(len(feature_names)))  # 模拟重要性值
        importances = importances / np.sum(importances)  # 归一化
        
        # 创建特征重要性DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        # 特征重要性条形图
        fig1 = px.bar(importance_df, x='importance', y='feature', orientation='h',
                     title='特征重要性',
                     labels={'importance': '重要性', 'feature': '特征'})
        
        figures["feature_importance_interactive"] = fig1

        # 混淆矩阵热力图（模拟数据）
        # 在实际应用中，应使用真实的预测结果
        unique_classes = np.unique(target)
        n_classes = len(unique_classes)
        confusion_data = np.random.randint(0, 100, size=(n_classes, n_classes))
        confusion_df = pd.DataFrame(confusion_data, 
                                   index=[f'真实-{c}' for c in unique_classes],
                                   columns=[f'预测-{c}' for c in unique_classes])
        
        fig2 = px.imshow(confusion_df, 
                        labels=dict(x="预测标签", y="真实标签", color="数量"),
                        title='混淆矩阵',
                        color_continuous_scale='Blues')
        
        # 在每个格子中显示数值
        for i in range(n_classes):
            for j in range(n_classes):
                fig2.add_annotation(x=j, y=i, text=str(confusion_data[i][j]),
                                   showarrow=False, font=dict(color="white" if confusion_data[i][j] > 50 else "black"))
        
        figures["confusion_matrix_interactive"] = fig2

        # 决策树结构图（简化版示意图）
        # 在实际应用中，应使用plotly的tree图或专门的决策树可视化库
        nodes = ['根节点', '条件1', '条件2', '叶节点1', '叶节点2', '叶节点3', '叶节点4']
        parents = ['', '根节点', '根节点', '条件1', '条件1', '条件2', '条件2']
        
        fig3 = go.Figure(go.Treemap(
            labels=nodes,
            parents=parents,
            values=[100, 50, 50, 25, 25, 30, 20],
            textinfo="label+value",
            marker=dict(colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0', '#ffb3e6'])
        ))
        fig3.update_layout(title='决策树结构')
        
        figures["decision_tree_structure_interactive"] = fig3

    except Exception as e:
        logger.error(f"决策树分类器交互式可视化过程中出现错误: {str(e)}")
        raise
    
    return figures