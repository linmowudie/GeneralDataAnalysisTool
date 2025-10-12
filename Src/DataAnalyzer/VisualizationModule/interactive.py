"""
Src/DataAnalyzer/VisualizationModule/interactive.py
交互式可视化模块

该模块提供基于Plotly的交互式可视化功能，
增强现有的matplotlib静态可视化能力。
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class InteractiveVisualization:
    """交互式可视化基类"""
    
    def __init__(self, params: Dict[str, Any]):
        """
        初始化交互式可视化对象
        
        Args:
            params: 可视化参数字典
                - data: 数据 (DataFrame)
                - x: x轴数据
                - y: y轴数据
                - title: 图表标题
                - labels: 轴标签字典
                - color: 颜色映射列
                - size: 大小映射列
                - hover_data: 悬停显示数据
        """
        self.params = params
        self.data = params.get('data')
        self.x = params.get('x')
        self.y = params.get('y')
        self.title = params.get('title', 'Interactive Plot')
        self.labels = params.get('labels', {})
        self.color = params.get('color')
        self.size = params.get('size')
        self.hover_data = params.get('hover_data')
        
    def scatter_plot(self) -> go.Figure:
        """
        创建交互式散点图
        
        Returns:
            plotly.graph_objects.Figure: 交互式散点图
        """
        try:
            fig = px.scatter(
                self.data,
                x=self.x,
                y=self.y,
                color=self.color,
                size=self.size,
                hover_data=self.hover_data,
                title=self.title,
                labels=self.labels
            )
            return fig
        except Exception as e:
            logger.error(f"创建交互式散点图时出错: {str(e)}")
            raise
            
    def line_plot(self) -> go.Figure:
        """
        创建交互式折线图
        
        Returns:
            plotly.graph_objects.Figure: 交互式折线图
        """
        try:
            fig = px.line(
                self.data,
                x=self.x,
                y=self.y,
                color=self.color,
                hover_data=self.hover_data,
                title=self.title,
                labels=self.labels
            )
            return fig
        except Exception as e:
            logger.error(f"创建交互式折线图时出错: {str(e)}")
            raise
            
    def bar_plot(self) -> go.Figure:
        """
        创建交互式条形图
        
        Returns:
            plotly.graph_objects.Figure: 交互式条形图
        """
        try:
            fig = px.bar(
                self.data,
                x=self.x,
                y=self.y,
                color=self.color,
                hover_data=self.hover_data,
                title=self.title,
                labels=self.labels
            )
            return fig
        except Exception as e:
            logger.error(f"创建交互式条形图时出错: {str(e)}")
            raise
            
    def histogram(self) -> go.Figure:
        """
        创建交互式直方图
        
        Returns:
            plotly.graph_objects.Figure: 交互式直方图
        """
        try:
            fig = px.histogram(
                self.data,
                x=self.x,
                color=self.color,
                hover_data=self.hover_data,
                title=self.title,
                labels=self.labels
            )
            return fig
        except Exception as e:
            logger.error(f"创建交互式直方图时出错: {str(e)}")
            raise
            
    def heatmap(self, z: Optional[Any] = None) -> go.Figure:
        """
        创建交互式热力图
        
        Args:
            z: z轴数据（对于热力图），如果未提供则使用self.data的值
            
        Returns:
            plotly.graph_objects.Figure: 交互式热力图
        """
        try:
            if z is None and self.data is not None:
                z = self.data.values if hasattr(self.data, 'values') else self.data
                
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=self.x,
                y=self.y,
                colorscale='Viridis'
            ))
            fig.update_layout(
                title=self.title,
                xaxis_title=self.labels.get('x', ''),
                yaxis_title=self.labels.get('y', '')
            )
            return fig
        except Exception as e:
            logger.error(f"创建交互式热力图时出错: {str(e)}")
            raise
            
    def box_plot(self) -> go.Figure:
        """
        创建交互式箱线图
        
        Returns:
            plotly.graph_objects.Figure: 交互式箱线图
        """
        try:
            fig = px.box(
                self.data,
                x=self.x,
                y=self.y,
                color=self.color,
                hover_data=self.hover_data,
                title=self.title,
                labels=self.labels
            )
            return fig
        except Exception as e:
            logger.error(f"创建交互式箱线图时出错: {str(e)}")
            raise
            
    def violin_plot(self) -> go.Figure:
        """
        创建交互式小提琴图
        
        Returns:
            plotly.graph_objects.Figure: 交互式小提琴图
        """
        try:
            fig = px.violin(
                self.data,
                x=self.x,
                y=self.y,
                color=self.color,
                hover_data=self.hover_data,
                title=self.title,
                labels=self.labels
            )
            return fig
        except Exception as e:
            logger.error(f"创建交互式小提琴图时出错: {str(e)}")
            raise