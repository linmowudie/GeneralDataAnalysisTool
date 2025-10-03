"""
Src/DataAnalyzer/visualization/interactive_plots/timeseries.py
时间序列交互式可视化模块

该模块提供时间序列数据的交互式可视化功能，
包括时间序列折线图和多序列对比显示。
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any
from ..interactive_registry import interactive_plot_registry
import logging

logger = logging.getLogger(__name__)

@interactive_plot_registry.register("transformer", "timeseries")
def plot_time_series_interactive(params: Dict[str, Any]) -> Dict[str, go.Figure]:
    """时间序列交互式可视化"""
    figures = {}
    feature = params["feature"]
    
    try:
        # 确保数据按时间排序
        if 'date' in feature.columns:
            feature = feature.sort_values('date')
            x_col = 'date'
        else:
            # 假设第一列是时间列
            x_col = feature.columns[0]
            feature = feature.sort_values(x_col)
        
        # 主要时间序列图
        y_col = [col for col in feature.columns if col != x_col]
        
        if len(y_col) == 1:
            # 单序列时间序列图
            fig1 = px.line(feature, x=x_col, y=y_col[0],
                          title=f'{y_col[0]} 时间序列图',
                          labels={x_col: '时间', y_col[0]: y_col[0]})
            
            # 添加范围滑块
            fig1.update_xaxes(rangeslider_visible=True)
            
            figures["time_series_single_interactive"] = fig1
            
        else:
            # 多序列时间序列图
            fig1 = go.Figure()
            
            for col in y_col:
                fig1.add_trace(go.Scatter(
                    x=feature[x_col],
                    y=feature[col],
                    mode='lines',
                    name=col
                ))
            
            fig1.update_layout(
                title='多序列时间序列图',
                xaxis_title='时间',
                yaxis_title='数值',
                xaxis_rangeslider_visible=True
            )
            
            figures["time_series_multiple_interactive"] = fig1

        # 时间序列统计信息（直方图）
        if len(y_col) == 1:
            fig2 = px.histogram(feature, x=y_col[0], 
                               title=f'{y_col[0]} 分布直方图',
                               labels={y_col[0]: y_col[0], 'count': '频次'})
            
            figures["time_series_histogram_interactive"] = fig2

    except Exception as e:
        logger.error(f"时间序列交互式可视化过程中出现错误: {str(e)}")
        raise
    
    return figures