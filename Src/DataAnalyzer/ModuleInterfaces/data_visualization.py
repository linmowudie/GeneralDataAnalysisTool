# data_visualization.py
import logging
from typing import Dict, Any
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .visualization.registry import plot_registry

# 确保导入所有可视化插件
from .visualization.plots import linearregression, logisticregression, kmeans

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
        """
        self.param_dict = param_dict
        self.registry = plot_registry
        
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
    
    def apply_global_styles(self) -> None:
        """应用全局绘图样式"""
        # 设置绘图风格
        if "plot_style" in self.param_dict:
            plt.style.use(self.param_dict["plot_style"])
        
        # 设置字体
        if "font_style" in self.param_dict:
            plt.rcParams.update({"font.family": self.param_dict["font_style"]})