"""
K线图/蜡烛图（Candlestick Plot）可视化策略
K线图是一种金融图表，用于描述价格变动，显示开盘价、收盘价、最高价和最低价
"""

import numpy as np
from typing import Dict, Any, List, Optional
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.graph_objects as go

from ..base_visualization import VisualizationStrategy


class CandlestickPlotStrategy(VisualizationStrategy):
    """
    K线图/蜡烛图可视化策略
    """

    def validate_params(self) -> None:
        """
        验证参数
        """
        required_params = ["open", "high", "low", "close"]
        for param in required_params:
            if param not in self.params:
                raise ValueError(f"缺少必要参数: {param}")
        
        # 检查数据长度是否一致
        open_data = self.params["open"]
        high_data = self.params["high"]
        low_data = self.params["low"]
        close_data = self.params["close"]
        
        if not (len(open_data) == len(high_data) == len(low_data) == len(close_data)):
            raise ValueError("开盘价、最高价、最低价和收盘价数据长度必须一致")

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态K线图
        
        Returns:
            包含图表名称和Figure对象的字典
        """
        self.validate_params()
        open_data = self.params["open"]
        high_data = self.params["high"]
        low_data = self.params["low"]
        close_data = self.params["close"]
        dates = self.params.get("dates", None)
        title = self.params.get("title", "Candlestick Chart")
        up_color = self.params.get("up_color", "green")
        down_color = self.params.get("down_color", "red")
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 生成K线图
        self._plot_candlestick_matplotlib(ax, open_data, high_data, low_data, close_data, 
                                        dates, up_color, down_color)
        
        ax.set_title(title, fontsize=16)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # 如果有日期数据，设置x轴标签
        if dates is not None:
            ax.set_xlabel("Date")
        else:
            ax.set_xlabel("Period")
        
        ax.set_ylabel("Price")
        
        return {"candlestick_plot": fig}

    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式K线图
        
        Returns:
            包含图表名称和plotly Figure对象的字典
        """
        self.validate_params()
        open_data = self.params["open"]
        high_data = self.params["high"]
        low_data = self.params["low"]
        close_data = self.params["close"]
        dates = self.params.get("dates", None)
        title = self.params.get("title", "Candlestick Chart")
        up_color = self.params.get("up_color", "green")
        down_color = self.params.get("down_color", "red")
        name = self.params.get("name", "Price")
        
        # 创建图形
        fig = go.Figure()
        
        # 添加K线图
        fig.add_trace(go.Candlestick(
            x=dates,
            open=open_data,
            high=high_data,
            low=low_data,
            close=close_data,
            name=name,
            increasing_line_color=up_color,
            decreasing_line_color=down_color
        ))
        
        fig.update_layout(
            title=title,
            yaxis_title="Price",
            xaxis_title="Date" if dates is not None else "Period"
        )
        
        return {"candlestick_plot": fig}

    def _plot_candlestick_matplotlib(self, ax, open_data, high_data, low_data, close_data, 
                                   dates, up_color, down_color):
        """
        使用matplotlib绘制K线图
        """
        length = len(open_data)
        # 如果没有提供日期，则使用索引
        x = dates if dates is not None else list(range(length))
        
        # 绘制影线（上下影线）
        for i in range(length):
            ax.plot([x[i], x[i]], [low_data[i], high_data[i]], color='black', linewidth=1)
        
        # 绘制实体（开盘价和收盘价之间的矩形）
        width = 0.6
        for i in range(length):
            open_price = open_data[i]
            close_price = close_data[i]
            
            # 确定颜色：收盘价高于开盘价为上涨（阳线），否则为下跌（阴线）
            color = up_color if close_price >= open_price else down_color
            
            # 绘制实体
            bottom = min(open_price, close_price)
            height = abs(close_price - open_price)
            if height == 0:  # 如果开盘价等于收盘价，绘制一条线
                ax.plot([x[i] - width/2, x[i] + width/2], [open_price, open_price], 
                       color=color, linewidth=6)
            else:  # 绘制矩形实体
                rect = patches.Rectangle((i - width/2, bottom), width, height, 
                                   facecolor=color, edgecolor='black')
                ax.add_patch(rect)
        
        # 设置x轴
        if dates is not None:
            ax.set_xticks(x[::max(1, len(x)//10)])  # 每隔10个点显示一个标签
            ax.set_xticklabels([str(date) for date in x[::max(1, len(x)//10)]], rotation=45)
        else:
            ax.set_xticks(range(0, length, max(1, length//10)))