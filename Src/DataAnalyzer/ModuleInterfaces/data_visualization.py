# data_visualization.py
import logging
from typing import Dict, Any
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.graph_objects as go

from ..VisualizationModule.registry import plot_registry
from ..VisualizationModule.interactive_registry import interactive_plot_registry

# 确保导入所有可视化插件
from ..VisualizationModule.Plots import linearregression, logisticregression, kmeans
from ..VisualizationModule.Plots import three_d  # 3D可视化模块
from ..VisualizationModule.InteractivePlots import linearregression as interactive_linearregression
from ..VisualizationModule.InteractivePlots import kmeans as interactive_kmeans
from ..VisualizationModule.InteractivePlots import three_d as interactive_three_d  # 交互式3D可视化模块
from ..VisualizationModule.InteractivePlots import decisiontreeclassifier as interactive_decisiontreeclassifier
from ..VisualizationModule.InteractivePlots import timeseries as interactive_timeseries
from ..VisualizationModule.InteractivePlots import featureimportance as interactive_featureimportance

logger = logging.getLogger(__name__)

class DataVisualization:
    """数据可视化基类，负责参数校验和绘图分发"""
    
    def __init__(self, param_dict: Dict[str, Any]) -> None:
        """
        :param param_dict: 参数字典
            - task_type: 任务类型 (classification, regression, clustering, transformer)
            - model_name: 模型名称 (小写)
            - feature: 特征矩阵 (pandas.DataFrame)
            - target: 目标值 (pandas.Series, 可选)
            - predict: 预测值 (pandas.Series, 可选)
            - label_style: 标签样式 {x: str, y: str, title: str}
            - plot_style: 绘图风格 (matplotlib风格)
            - shape_style: 形状样式 {points: {size: int, colors: list}, lines: {width: float, styles: list}}
            - font_style: 字体样式
            - model_specific: 模型特定参数 (如聚类中心、解释方差等)
            - interactive: 是否使用交互式可视化 (布尔值，默认为False)
        """
        self.param_dict = param_dict
        self.registry = plot_registry
        self.interactive_registry = interactive_plot_registry
        
    def validate_params(self) -> None:
        """验证必要参数"""
        required = ["task_type", "model_name", "feature"]
        for param in required:
            if param not in self.param_dict:
                raise ValueError(f"Missing required parameter: {param}")
                
        # 任务特定参数验证
        task_type = self.param_dict["task_type"]
        if task_type in ["classification", "regression"]:
            if "target" not in self.param_dict or "predict" not in self.param_dict:
                raise ValueError(f"{task_type} tasks require 'target' and 'predict' parameters")
    
    def plot_chart(self) -> Dict[str, Figure]:
        """生成图表"""
        self.validate_params()
        
        # 检查是否需要生成交互式图表
        use_interactive = self.param_dict.get("interactive", False)
        
        if use_interactive:
            return self._plot_interactive_chart()
        else:
            return self._plot_static_chart()
    
    def _plot_static_chart(self) -> Dict[str, Figure]:
        """生成静态图表"""
        task_type = self.param_dict["task_type"]
        model_name = self.param_dict["model_name"].lower()
        
        # 获取绘图函数
        plot_func = self.registry.get_plot_function(task_type, model_name)
        if not plot_func:
            raise NotImplementedError(
                f"No plot implemented for {model_name} ({task_type})"
            )
        
        # 应用全局样式
        self.apply_global_styles()
        
        # 调用具体绘图函数
        return plot_func(self.param_dict)
    
    def _plot_interactive_chart(self) -> Dict[str, go.Figure]:
        """生成交互式图表"""
        task_type = self.param_dict["task_type"]
        model_name = self.param_dict["model_name"].lower()
        
        # 获取交互式绘图函数
        plot_func = self.interactive_registry.get_plot_function(task_type, model_name)
        if not plot_func:
            raise NotImplementedError(
                f"No interactive plot implemented for {model_name} ({task_type})"
            )
        
        # 调用具体交互式绘图函数
        return plot_func(self.param_dict)
    
    def apply_global_styles(self) -> None:
        """应用全局绘图样式"""
        # 设置绘图风格
        if "plot_style" in self.param_dict:
            plt.style.use(self.param_dict["plot_style"])
        
        # 设置字体
        if "font_style" in self.param_dict:
            plt.rcParams.update({"font.family": self.param_dict["font_style"]})