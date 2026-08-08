"""
通用散点图可视化策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


class ScatterPlotStrategy(VisualizationStrategy):
    """
    通用散点图可视化策略
    """
    
    def generate_static_charts(self):
        """
        生成静态图表
        """
        charts = {}
        charts.update(self.generate_scatter_plot())
        return charts
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        """
        charts = {}
        charts.update(self.generate_interactive_scatter_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证散点图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"散点图缺少必要参数: {param}")
        
        X = self.params["X"]
        if X.shape[1] < 2:
            raise ValueError("散点图需要至少2维数据")

    def generate_scatter_plot(self) -> Dict[str, Figure]:
        """
        生成散点图
        """
        import matplotlib.pyplot as plt
        
        X = self.params["X"]
        y = self.params.get("y")
        
        # 只使用前两维进行可视化
        x_data = X[:, 0]
        y_data = X[:, 1]
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if y is not None:
            scatter = ax.scatter(x_data, y_data, c=y, cmap='viridis')
            plt.colorbar(scatter, ax=ax)
        else:
            ax.scatter(x_data, y_data)
        
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('散点图')
        
        return {"scatter_plot": fig}

    def generate_interactive_scatter_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式散点图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        # 只使用前两维进行可视化
        x_data = X[:, 0]
        y_data = X[:, 1]
        
        fig = go.Figure()
        
        if y is not None:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='markers',
                marker=dict(
                    color=y,
                    colorscale='Viridis',
                    colorbar=dict(title="值")
                ),
                name='数据点'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='markers',
                name='数据点'
            ))
        
        fig.update_layout(
            title="散点图",
            xaxis_title="特征 1",
            yaxis_title="特征 2"
        )
        
        return {"scatter_plot": fig}


class LinePlotStrategy(VisualizationStrategy):
    """
    折线图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态折线图
        """
        charts = {}
        charts.update(self.generate_line_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式折线图
        """
        charts = {}
        charts.update(self.generate_interactive_line_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证折线图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"折线图缺少必要参数: {param}")

    def generate_line_plot(self) -> Dict[str, Figure]:
        """
        生成静态折线图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            ax.plot(X, y)
            ax.set_ylabel('值')
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                ax.plot(X[:, 0])
            else:
                ax.plot(X)
        
        ax.set_xlabel('索引')
        ax.set_title('折线图')
        
        return {"line_plot": fig}

    def generate_interactive_line_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式折线图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        fig = go.Figure()
        
        if y is not None:
            fig.add_trace(go.Scatter(
                x=list(range(len(y))),
                y=y,
                mode='lines+markers',
                name='数据'
            ))
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                y_data = X[:, 0]
            else:
                y_data = X
            fig.add_trace(go.Scatter(
                x=list(range(len(y_data))),
                y=y_data,
                mode='lines+markers',
                name='数据'
            ))
        
        fig.update_layout(
            title="折线图",
            xaxis_title="索引",
            yaxis_title="值"
        )
        
        return {"line_plot": fig}


class BarPlotStrategy(VisualizationStrategy):
    """
    柱状图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态柱状图
        """
        charts = {}
        charts.update(self.generate_bar_plot())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式柱状图
        """
        charts = {}
        charts.update(self.generate_interactive_bar_plot())
        return charts

    def validate_params(self) -> None:
        """
        验证柱状图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"柱状图缺少必要参数: {param}")

    def generate_bar_plot(self) -> Dict[str, Figure]:
        """
        生成静态柱状图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            ax.bar(range(len(y)), y)
            ax.set_ylabel('值')
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                y_data = X[:, 0]
            else:
                y_data = X
            ax.bar(range(len(y_data)), y_data)
        
        ax.set_xlabel('索引')
        ax.set_title('柱状图')
        
        return {"bar_plot": fig}

    def generate_interactive_bar_plot(self) -> Dict[str, go.Figure]:
        """
        生成交互式柱状图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        if y is not None:
            x_data = list(range(len(y)))
            y_data = y
        else:
            # 如果没有y值，使用X的第一列作为y值
            if len(X.shape) > 1:
                y_data = X[:, 0]
            else:
                y_data = X
            x_data = list(range(len(y_data)))
        
        fig = go.Figure(data=[
            go.Bar(x=x_data, y=y_data)
        ])
        
        fig.update_layout(
            title="柱状图",
            xaxis_title="索引",
            yaxis_title="值"
        )
        
        return {"bar_plot": fig}


class HistogramStrategy(VisualizationStrategy):
    """
    直方图可视化策略
    """
    
    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态直方图
        """
        charts = {}
        charts.update(self.generate_histogram())
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式直方图
        """
        charts = {}
        charts.update(self.generate_interactive_histogram())
        return charts

    def validate_params(self) -> None:
        """
        验证直方图参数
        """
        required = ["X"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"直方图缺少必要参数: {param}")

    def generate_histogram(self) -> Dict[str, Figure]:
        """
        生成静态直方图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if y is not None:
            ax.hist(y, bins=30)
            ax.set_xlabel('值')
        else:
            # 如果没有y值，使用X的第一列
            if len(X.shape) > 1:
                data = X[:, 0]
            else:
                data = X
            ax.hist(data, bins=30)
            ax.set_xlabel('值')
        
        ax.set_ylabel('频率')
        ax.set_title('直方图')
        
        return {"histogram": fig}

    def generate_interactive_histogram(self) -> Dict[str, go.Figure]:
        """
        生成交互式直方图
        """
        X = self.params["X"]
        y = self.params.get("y")
        
        if y is not None:
            data = y
        else:
            # 如果没有y值，使用X的第一列
            if len(X.shape) > 1:
                data = X[:, 0]
            else:
                data = X
        
        fig = go.Figure(data=[
            go.Histogram(x=data)
        ])
        
        fig.update_layout(
            title="直方图",
            xaxis_title="值",
            yaxis_title="频率"
        )
        
        return {"histogram": fig}