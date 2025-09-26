"""
Src/DataAnalyzer/visualization/interactive_plots/linearregression.py
线性回归交互式可视化模块

该模块提供线性回归模型的交互式可视化功能，
包括回归线和数据点的交互式展示。
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, Any
from ..interactive_registry import interactive_plot_registry
import logging

logger = logging.getLogger(__name__)

@interactive_plot_registry.register("regression", "linearregression")
def plot_linear_regression_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """线性回归交互式可视化"""
    figures = {}
    target = params["target"]
    predict = params["predict"]
    
    try:
        # 创建DataFrame用于绘图
        df = pd.DataFrame({
            'Actual': target,
            'Predicted': predict
        })
        
        # 真实值 vs 预测值散点图
        fig1 = px.scatter(df, x='Actual', y='Predicted', 
                         title='真实值 vs 预测值',
                         labels={'Actual': '真实值', 'Predicted': '预测值'})
        
        # 添加对角线
        min_val = min(min(target), min(predict))
        max_val = max(max(target), max(predict))
        fig1.add_shape(type='line',
                      x0=min_val, y0=min_val,
                      x1=max_val, y1=max_val,
                      line=dict(color='Red', dash='dash'))
        
        # 计算R²值用于显示
        ss_res = np.sum((target - predict) ** 2)
        ss_tot = np.sum((target - np.mean(target)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        fig1.add_annotation(x=min_val + (max_val-min_val)*0.05, 
                           y=max_val - (max_val-min_val)*0.05,
                           text=f'R² = {r_squared:.3f}',
                           showarrow=False,
                           font=dict(size=14))
        
        figures["pred_vs_actual_interactive"] = fig1

        # 残差图
        residuals = target - predict
        df_residuals = pd.DataFrame({
            'Predicted': predict,
            'Residuals': residuals
        })
        
        fig2 = px.scatter(df_residuals, x='Predicted', y='Residuals',
                         title='残差图',
                         labels={'Predicted': '预测值', 'Residuals': '残差'})
        
        fig2.add_hline(y=0, line_dash="dash", line_color="red")
        
        # 添加残差统计信息
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        fig2.add_annotation(x=0.02, y=0.98,
                           xref="paper", yref="paper",
                           text=f'平均残差: {mean_residual:.3f}<br>标准差: {std_residual:.3f}',
                           showarrow=False,
                           font=dict(size=12),
                           align='left',
                           bgcolor="white",
                           bordercolor="black",
                           borderwidth=1)
        
        figures["residual_plot_interactive"] = fig2
        
    except Exception as e:
        logger.error(f"线性回归交互式可视化过程中出现错误: {str(e)}")
        raise
    
    return figures