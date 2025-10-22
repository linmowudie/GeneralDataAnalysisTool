#第三方库导入区
import logging
from typing import List, Dict, Any, Union, Optional
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
import plotly.graph_objects as go

#项目文件导入区
from Src.DataAnalyzer.DataVisualisationUpgrade.factory import VisualizationFactory

#静态参数定义
logger = logging.getLogger(__name__)

#接口定义
class DataVisualization:
    """数据可是化接口，负责传递和检验参数，调用数据可视化模块"""

    def __init__(
        self,
        model_name: str,
        model: Any,
        task_list: List[str],
        data_dict: Dict[str, Any],
        label_style: str,
        plot_style: str,
        font_style: str,
        interactive: bool = False
        ) -> None:
        """
        :param model_name: 模型名称，支持各类传统机器学习模型
        :param model: 模型对象，用于获取已训练模型的参数，方便各种模型获取参数
        :param task_list: 任务列表，可指定绘画各种图标，但与模型种类相互绑定
        :param data_dict: 数据字典，包含训练集和测试集，目标类等等所需的数据
        :param label_style: 标签样式，个性化命名特征列名称
        :param plot_style: 绘图样式，个性化绘图
        :param font_style: 字体样式，个性化文字样式
        :param interactive: 交互图表，是否选择交互式图标     
        """
        self.model_name = model_name
        self.model = model
        self.task_list = task_list
        self.data_dict = data_dict
        self.label_style = label_style
        self.plot_style = plot_style
        self.font_style = font_style
        self.interactive = interactive
        
        # 创建工厂实例
        self.factory = VisualizationFactory()

    def generate_plot(self) -> Union[Dict[str, Figure], Dict[str, go.Figure]]:
        """
        生成图表
        
        :return: 生成的图表字典，键为图表名称，值为 matplotlib Figure 对象或 plotly Figure 对象
        """
        # 确定任务类型
        task_type = self._determine_task_type()
        
        # 构建参数字典
        params = {
            "model_name": self.model_name,
            "model": self.model,
            "task_list": self.task_list,
            "label_style": self.label_style,
            "plot_style": self.plot_style,
            "font_style": self.font_style,
        }
        
        # 添加数据字典中的内容到参数中
        params.update(self.data_dict)
        
        # 创建可视化策略
        strategy = self.factory.create_visualization_strategy(
            model_name=self.model_name,
            task_type=task_type,
            params=params
        )
        
        # 验证参数
        strategy.validate_params()
        
        # 生成图表
        if self.interactive:
            return strategy.generate_interactive_charts()
        else:
            return strategy.generate_static_charts()

    def _determine_task_type(self) -> str:
        """
        根据模型名称确定任务类型
        
        :return: 任务类型字符串
        """
        # 获取支持的任务类型
        supported_tasks = self.factory.get_model_supported_tasks(self.model_name)
        
        if not supported_tasks:
            raise ValueError(f"不支持的模型: {self.model_name}")
            
        # 如果只有一个支持的任务类型，直接返回
        if len(supported_tasks) == 1:
            return supported_tasks[0]
            
        # 如果有多个支持的任务类型，需要进一步判断
        # 这里可以根据模型名称或其他规则来判断
        # 简化处理：返回第一个支持的任务类型
        return supported_tasks[0]