"""
欢乐图（Joy Plot）可视化策略
欢乐图是一种堆叠的、部分重叠的密度图，用于可视化多个组或类别的数值分布情况
"""

import numpy as np
from typing import Dict, Any, List, Optional
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..base_visualization import VisualizationStrategy


class JoyPlotStrategy(VisualizationStrategy):
    """
    欢乐图可视化策略
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
        生成静态欢乐图
        
        Returns:
            包含图表名称和Figure对象的字典
        """
        self.validate_params()
        data = self.params["data"]
        labels = self.params.get("labels", None)
        title = self.params.get("title", "Joy Plot")
        overlap = self.params.get("overlap", 0.7)
        colors = self.params.get("colors", None)
        
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
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 生成欢乐图
        self._plot_joy_matplotlib(ax, data, labels, overlap, colors)
        
        ax.set_title(title, fontsize=16, pad=20)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(False)
        
        return {"joy_plot": fig}

    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式欢乐图
        
        Returns:
            包含图表名称和plotly Figure对象的字典
        """
        self.validate_params()
        data = self.params["data"]
        labels = self.params.get("labels", None)
        title = self.params.get("title", "Joy Plot")
        colors = self.params.get("colors", None)
        
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
        fig = go.Figure()
        
        # 生成交互式欢乐图
        self._plot_joy_plotly(fig, data, labels, colors)
        
        fig.update_layout(
            title=title,
            showlegend=False,
            xaxis_title="Value",
            yaxis_title="Groups"
        )
        
        return {"joy_plot": fig}

    def _plot_joy_matplotlib(self, ax, data, labels, overlap, colors):
        """
        使用matplotlib绘制欢乐图
        """
        n_distributions = len(data)
        if labels is None:
            labels = [f"Series {i+1}" for i in range(n_distributions)]
        elif len(labels) < n_distributions:
            labels.extend([f"Series {i+len(labels)+1}" for i in range(n_distributions - len(labels))])
        
        # 如果没有指定颜色，使用默认颜色循环
        if colors is None:
            cmap = plt.get_cmap('Set2')
            colors = cmap(np.linspace(0, 1, n_distributions))
        elif len(colors) < n_distributions:
            # 扩展颜色列表
            cmap = plt.get_cmap('Set2')
            colors = list(colors) + list(cmap(np.linspace(0, 1, n_distributions - len(colors))))
        
        # 计算所有数据的范围
        all_data = np.concatenate(data)
        x_min, x_max = np.min(all_data), np.max(all_data)
        x = np.linspace(x_min, x_max, 300)
        
        # 为每个分布计算密度并绘制
        for i, (group_data, label, color) in enumerate(zip(data, labels, colors)):
            try:
                # 使用高斯核密度估计计算密度
                density = gaussian_kde(group_data)
                y = density(x)
                
                # 调整y轴位置以创建重叠效果
                y_offset = i * (1 - overlap)
                y_values = y + y_offset
                
                # 绘制填充区域
                ax.fill_between(x, y_offset, y_values, alpha=0.7, color=color)
                
                # 绘制线条
                ax.plot(x, y_values, color='darkblue', linewidth=1)
                
                # 添加标签
                ax.text(x_max + (x_max - x_min) * 0.02, y_offset + np.max(y) / 2, 
                       label, verticalalignment='center', fontsize=10)
            except Exception as e:
                # 如果某个分布无法计算密度，则跳过
                continue
        
        # 设置y轴标签
        ax.set_yticks([])
        ax.set_ylabel("Distribution Groups")
        ax.set_xlabel("Value")

    def _plot_joy_plotly(self, fig, data, labels, colors):
        """
        使用plotly绘制欢乐图
        """
        n_distributions = len(data)
        if labels is None:
            labels = [f"Series {i+1}" for i in range(n_distributions)]
        elif len(labels) < n_distributions:
            labels.extend([f"Series {i+len(labels)+1}" for i in range(n_distributions - len(labels))])
        
        # 如果没有指定颜色，使用默认颜色
        if colors is None:
            colors = [f"hsl({i * 360 / n_distributions}, 70%, 50%)" for i in range(n_distributions)]
        elif len(colors) < n_distributions:
            # 扩展颜色列表
            colors = list(colors) + [f"hsl({i * 360 / n_distributions}, 70%, 50%)" 
                                   for i in range(len(colors), n_distributions)]
        
        # 计算所有数据的范围
        all_data = np.concatenate(data)
        x_min, x_max = np.min(all_data), np.max(all_data)
        x = np.linspace(x_min, x_max, 300)
        
        # 为每个分布计算密度并绘制
        for i, (group_data, label, color) in enumerate(zip(data, labels, colors)):
            try:
                # 使用高斯核密度估计计算密度
                density = gaussian_kde(group_data)
                y = density(x)
                
                # 添加迹线
                fig.add_trace(
                    go.Scatter(
                        x=np.concatenate([x, x[::-1]]),  # x坐标和反向x坐标
                        y=np.concatenate([y + i, np.full_like(x[::-1], i)]),  # 密度值加上偏移量和底部值
                        mode='lines',
                        fill='toself',
                        name=label,
                        line=dict(color='darkblue', width=1),
                        fillcolor=color,
                        opacity=0.7
                    )
                )
            except Exception as e:
                # 如果某个分布无法计算密度，则跳过
                continue
        
        # 更新y轴
        fig.update_yaxes(showticklabels=False, title_text="Distribution Groups")
        fig.update_xaxes(title_text="Value")