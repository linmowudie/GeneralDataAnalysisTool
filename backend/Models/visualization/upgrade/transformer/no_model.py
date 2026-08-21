"""
无模型图表可视化策略
"""

from typing import Dict, Any
from .base import TransformerStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class NoModelStrategy(TransformerStrategy):
    """
    无模型图表可视化策略
    """
    
    def validate_params(self) -> None:
        """
        验证无模型图表参数
        """
        super().validate_params()
        # 无模型图表可以使用基础验证

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        """
        charts = {}
        
        # 根据任务列表生成相应图表
        task_list = self.params.get("task_list", [])
        
        for task in task_list:
            if task == "pie":
                pie_charts = self.generate_pie()
                charts.update(pie_charts)
            elif task == "word_cloud":
                word_cloud_charts = self.generate_word_cloud()
                charts.update(word_cloud_charts)
            elif task == "network_graph":
                network_charts = self.generate_network_graph()
                charts.update(network_charts)
            elif task == "gauge_chart":
                gauge_charts = self.generate_gauge_chart()
                charts.update(gauge_charts)
            elif task == "waterfall_chart":
                waterfall_charts = self.generate_waterfall_chart()
                charts.update(waterfall_charts)
            elif task == "calendar_heatmap":
                heatmap_charts = self.generate_calendar_heatmap()
                charts.update(heatmap_charts)
        
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式图表
        """
        charts = {}
        
        # 根据任务列表生成相应图表
        task_list = self.params.get("task_list", [])
        
        for task in task_list:
            if task == "gauge_chart":
                gauge_charts = self.generate_gauge_chart()
                charts.update(gauge_charts)
            elif task == "waterfall_chart":
                waterfall_charts = self.generate_waterfall_chart()
                charts.update(waterfall_charts)
            elif task == "scatter_3d":
                scatter_charts = self.generate_scatter_3d_interactive()
                charts.update(scatter_charts)
            elif task == "surface_3d":
                surface_charts = self.generate_surface_3d()
                charts.update(surface_charts)
            elif task == "wireframe_3d":
                wireframe_charts = self.generate_wireframe_3d()
                charts.update(wireframe_charts)
        
        return charts

    def generate_pie(self) -> Dict[str, Figure]:
        """
        生成饼图
        """
        import matplotlib.pyplot as plt
        
        # 获取数据
        values = self.params.get("values", [])
        labels = self.params.get("labels", [f"部分{i}" for i in range(len(values))])
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # 绘制饼图
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('饼图')
        
        return {"no_model_pie": fig}

    def generate_word_cloud(self) -> Dict[str, Figure]:
        """
        生成词云图
        """
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
        except ImportError:
            # 如果没有安装wordcloud库，则返回空图表
            fig = Figure()
            return {"no_model_word_cloud": fig}
        
        # 获取文本数据
        text = self.params.get("text", "")
        if not text:
            raise ValueError("生成词云图需要提供文本数据")
        
        # 创建词云
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # 显示词云
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('词云图')
        
        return {"no_model_word_cloud": fig}

    def generate_network_graph(self) -> Dict[str, Figure]:
        """
        生成网络图
        """
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
        except ImportError:
            # 如果没有安装networkx库，则返回空图表
            fig = Figure()
            return {"no_model_network_graph": fig}
        
        # 获取网络数据
        edges = self.params.get("edges", [])
        if not edges:
            raise ValueError("生成网络图需要提供边数据")
        
        # 创建图
        G = nx.Graph()
        G.add_edges_from(edges)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 绘制网络图
        pos = nx.spring_layout(G)
        nx.draw(G, pos, ax=ax, with_labels=True, node_color='lightblue', 
                node_size=500, font_size=10, font_weight='bold')
        ax.set_title('网络图')
        
        return {"no_model_network_graph": fig}

    def generate_gauge_chart(self) -> Dict[str, go.Figure]:
        """
        生成仪表盘图
        """
        value = self.params.get("value", 0)
        max_value = self.params.get("max_value", 100)
        
        # 创建仪表盘图
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "仪表盘图"},
            gauge={'axis': {'range': [None, max_value]}}
        ))
        
        return {"no_model_gauge_chart": fig}

    def generate_waterfall_chart(self) -> Dict[str, go.Figure]:
        """
        生成瀑布图
        """
        # 获取数据
        values = self.params.get("values", [])
        labels = self.params.get("labels", [f"步骤{i}" for i in range(len(values))])
        
        # 创建瀑布图
        fig = go.Figure(go.Waterfall(
            name="瀑布图",
            orientation="v",
            measure=["relative"] * len(values),
            x=labels,
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="瀑布图",
            waterfallgap=0.3
        )
        
        return {"no_model_waterfall_chart": fig}

    def generate_calendar_heatmap(self) -> Dict[str, Figure]:
        """
        生成日历热力图
        """
        try:
            import seaborn as sns
            import matplotlib.pyplot as plt
        except ImportError:
            # 如果没有安装seaborn库，则返回空图表
            fig = Figure()
            return {"no_model_calendar_heatmap": fig}
        
        # 获取数据
        data = self.params.get("data", np.random.rand(7, 52))  # 默认生成随机数据
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(15, 5))
        
        # 绘制热力图
        sns.heatmap(data, ax=ax, cmap="YlGn")
        ax.set_title('日历热力图')
        ax.set_xlabel('周')
        ax.set_ylabel('天')
        
        return {"no_model_calendar_heatmap": fig}
        
    def generate_scatter_3d_interactive(self) -> Dict[str, go.Figure]:
        """
        生成交互式3D散点图
        """
        X_train = self._get_training_data()
        
        # 创建交互式3D散点图
        fig = go.Figure(data=[go.Scatter3d(
            x=X_train[:, 0],
            y=X_train[:, 1],
            z=X_train[:, 2],
            mode='markers',
            marker=dict(
                size=5,
                opacity=0.8
            )
        )])
        
        fig.update_layout(
            title='交互式3D散点图',
            scene=dict(
                xaxis_title='X轴',
                yaxis_title='Y轴',
                zaxis_title='Z轴'
            )
        )
        
        return {"no_model_scatter_3d_interactive": fig}

    def generate_surface_3d(self) -> Dict[str, go.Figure]:
        """
        生成3D表面图
        """
        X_train = self._get_training_data()
        
        # 创建3D表面图
        fig = go.Figure(data=[go.Surface(
            z=X_train[:50, :50],  # 限制数据大小以提高性能
        )])
        
        fig.update_layout(
            title='3D表面图',
            scene=dict(
                xaxis_title='X轴',
                yaxis_title='Y轴',
                zaxis_title='Z轴'
            )
        )
        
        return {"no_model_surface_3d": fig}

    def generate_wireframe_3d(self) -> Dict[str, go.Figure]:
        """
        生成3D线框图
        """
        X_train = self._get_training_data()
        
        # 创建3D线框图
        fig = go.Figure(data=[go.Scatter3d(
            x=X_train[:, 0],
            y=X_train[:, 1],
            z=X_train[:, 2],
            mode='lines',
            line=dict(
                width=2,
                color='blue'
            )
        )])
        
        fig.update_layout(
            title='3D线框图',
            scene=dict(
                xaxis_title='X轴',
                yaxis_title='Y轴',
                zaxis_title='Z轴'
            )
        )
        
        return {"no_model_wireframe_3d": fig}