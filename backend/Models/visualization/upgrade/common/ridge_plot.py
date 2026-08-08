"""
山脊线图（Ridgeline Plot）可视化策略
山脊线图用于可视化和比较多个组或类别的数值分布情况
"""

import numpy as np
from typing import Dict, Any, List, Optional
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..base_visualization import VisualizationStrategy


class RidgePlotStrategy(VisualizationStrategy):
    """
    山脊线图可视化策略
    """

    def validate_params(self) -> None:
        """
        验证参数
        """
        required_params = ["data"]
        for param in required_params:
            if param not in self.params:
                raise ValueError(f"缺少必要参数: {param}")
        
        data = self.params["data"]
        if not isinstance(data, (list, np.ndarray)):
            raise ValueError("数据必须是列表或numpy数组")
            
        if isinstance(data, list) and len(data) == 0:
            raise ValueError("数据不能为空")

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态山脊线图
        
        Returns:
            包含图表名称和Figure对象的字典
        """
        self.validate_params()
        data = self.params["data"]
        labels = self.params.get("labels", None)
        title = self.params.get("title", "Ridgeline Plot")
        overlap = self.params.get("overlap", 0.5)
        fill_color = self.params.get("fill_color", "skyblue")
        
        # 如果数据是列表格式，转换为适合的格式
        if isinstance(data, list):
            if all(isinstance(d, (list, np.ndarray)) for d in data):
                # 多组数据
                pass
            else:
                # 单组数据
                data = [data]
                if labels:
                    labels = [labels] if isinstance(labels, str) else labels[:1]
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 生成山脊线图
        self._plot_ridgeline_matplotlib(ax, data, labels, overlap, fill_color)
        
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        return {"ridge_plot": fig}

    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式山脊线图
        
        Returns:
            包含图表名称和plotly Figure对象的字典
        """
        self.validate_params()
        data = self.params["data"]
        labels = self.params.get("labels", None)
        title = self.params.get("title", "Ridgeline Plot")
        fill_color = self.params.get("fill_color", "skyblue")
        
        # 如果数据是列表格式，转换为适合的格式
        if isinstance(data, list):
            if all(isinstance(d, (list, np.ndarray)) for d in data):
                # 多组数据
                pass
            else:
                # 单组数据
                data = [data]
                if labels:
                    labels = [labels] if isinstance(labels, str) else labels[:1]
        
        # 创建图形
        fig = make_subplots(rows=len(data), cols=1, shared_xaxes=True, 
                           vertical_spacing=0.02)
        
        # 生成交互式山脊线图
        self._plot_ridgeline_plotly(fig, data, labels, fill_color)
        
        fig.update_layout(title=title, showlegend=False)
        
        return {"ridge_plot": fig}

    def _plot_ridgeline_matplotlib(self, ax, data, labels, overlap, fill_color):
        """
        使用matplotlib绘制山脊线图
        """
        n_distributions = len(data)
        if labels is None:
            labels = [f"Group {i+1}" for i in range(n_distributions)]
        elif len(labels) < n_distributions:
            labels.extend([f"Group {i+len(labels)+1}" for i in range(n_distributions - len(labels))])
        
        # 计算所有数据的范围
        all_data = np.concatenate(data)
        x_min, x_max = np.min(all_data), np.max(all_data)
        x = np.linspace(x_min, x_max, 300)
        
        # 为每个分布计算密度并绘制
        for i, (group_data, label) in enumerate(zip(data, labels)):
            try:
                # 使用高斯核密度估计计算密度
                density = gaussian_kde(group_data)
                y = density(x)
                
                # 调整y轴位置以创建重叠效果
                y_offset = i * (1 - overlap)
                y_values = y + y_offset
                
                # 绘制填充区域
                ax.fill_between(x, y_offset, y_values, alpha=0.7, color=fill_color)
                
                # 绘制线条
                ax.plot(x, y_values, color='black', linewidth=0.8)
                
                # 添加标签
                ax.text(x_max + (x_max - x_min) * 0.02, y_offset + np.max(y) / 2, 
                       label, verticalalignment='center', fontsize=9)
            except Exception as e:
                # 如果某个分布无法计算密度，则跳过
                continue
        
        # 设置y轴标签
        ax.set_yticks([])
        ax.set_ylabel("Distributions")
        ax.set_xlabel("Value")

    def _plot_ridgeline_plotly(self, fig, data, labels, fill_color):
        """
        使用plotly绘制山脊线图
        """
        n_distributions = len(data)
        if labels is None:
            labels = [f"Group {i+1}" for i in range(n_distributions)]
        elif len(labels) < n_distributions:
            labels.extend([f"Group {i+len(labels)+1}" for i in range(n_distributions - len(labels))])
        
        # 计算所有数据的范围
        all_data = np.concatenate(data)
        x_min, x_max = np.min(all_data), np.max(all_data)
        x = np.linspace(x_min, x_max, 300)
        
        # 为每个分布计算密度并绘制
        for i, (group_data, label) in enumerate(zip(data, labels)):
            try:
                # 使用高斯核密度估计计算密度
                density = gaussian_kde(group_data)
                y = density(x)
                
                # 添加迹线
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y + i,  # 添加偏移量
                        mode='lines',
                        fill='tonexty',
                        name=label,
                        line=dict(color='black', width=1),
                        fillcolor=fill_color
                    ),
                    row=i+1, col=1
                )
            except Exception as e:
                # 如果某个分布无法计算密度，则跳过
                continue