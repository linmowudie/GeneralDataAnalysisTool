"""
backend/Models/visualization/dispatcher.py
数据可视化分发器（原 Engine/ModuleInterfaces/data_visualization.py 迁入）

负责参数校验和绘图分发（静态图 / 交互式图）。
"""
import logging
from typing import Dict, Any, Union
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure as MatplotlibFigure
    from plotly.graph_objects import Figure as PlotlyFigure

from .registry import plot_registry
from .interactive_registry import interactive_plot_registry

# 确保导入所有可视化插件
from .Plots import linearregression, logisticregression, kmeans
from .Plots import three_d, no_model  # 3D可视化模块和无模型可视化模块
from .InteractivePlots import linearregression as interactive_linearregression
from .InteractivePlots import kmeans as interactive_kmeans
from .InteractivePlots import three_d as interactive_three_d  # 交互式3D可视化模块
from .InteractivePlots import decisiontreeclassifier as interactive_decisiontreeclassifier
from .InteractivePlots import timeseries as interactive_timeseries
from .InteractivePlots import featureimportance as interactive_featureimportance
from .InteractivePlots import no_model as interactive_no_model  # 交互式无模型可视化模块

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
            - chart_type: 图表类型 (仅在model_name为no_model时使用)
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

    def plot_chart(self) -> Dict[str, Union[Figure, go.Figure]]:
        """生成图表"""
        # 首先确保数据一致性
        self._ensure_data_consistency()

        self.validate_params()

        # 检查是否需要生成交互式图表
        use_interactive = self.param_dict.get("interactive", False)

        if use_interactive:
            return self._plot_interactive_chart()
        else:
            return self._plot_static_chart()

    def _ensure_data_consistency(self) -> None:
        """确保可视化数据的一致性"""
        # 检查target和predict的一致性
        if "target" in self.param_dict and "predict" in self.param_dict:
            target = self.param_dict["target"]
            predict = self.param_dict["predict"]

            # 如果target和predict都存在，确保它们的索引一致
            if target is not None and predict is not None:
                # 处理predict是numpy数组的情况
                if isinstance(predict, np.ndarray):
                    if isinstance(target, pd.Series):
                        if len(predict) == len(target):
                            # 转换为具有相同索引的Series
                            self.param_dict["predict"] = pd.Series(predict, index=target.index)
                        else:
                            logger.warning(f"预测值长度({len(predict)})与目标值长度({len(target)})不匹配")
                    else:
                        # 如果target不是Series，创建一个新的Series
                        self.param_dict["predict"] = pd.Series(predict)

                # 处理两者都是Series的情况
                elif isinstance(target, pd.Series) and isinstance(predict, pd.Series):
                    # 获取共同索引
                    common_index = target.index.intersection(predict.index)
                    if len(common_index) > 0:
                        # 只保留共同索引的数据
                        self.param_dict["target"] = target.loc[common_index]
                        self.param_dict["predict"] = predict.loc[common_index]
                        # 同时更新feature（如果存在）
                        if "feature" in self.param_dict and isinstance(self.param_dict["feature"], pd.DataFrame):
                            self.param_dict["feature"] = self.param_dict["feature"].loc[common_index]
                    else:
                        logger.warning("目标值和预测值没有共同索引")

    def _plot_static_chart(self) -> Dict[str, Union[Figure, go.Figure]]:
        """生成静态图表"""
        task_type = self.param_dict["task_type"]
        model_name = self.param_dict["model_name"].lower()

        logger.debug(f"尝试获取 {model_name} ({task_type}) 的绘图函数")
        # 获取绘图函数
        plot_func = self.registry.get_plot_function(task_type, model_name)
        if not plot_func:
            logger.warning(
                f"No plot implemented for {model_name} ({task_type})"
            )
            return {}  # 返回空字典而不是抛出异常

        # 应用全局样式
        self.apply_global_styles()

        # 调用具体绘图函数
        logger.debug(f"调用 {model_name} ({task_type}) 的绘图函数")
        result = plot_func(self.param_dict)
        logger.debug(f"绘图函数返回了 {len(result)} 个图表")
        return result

    def _plot_interactive_chart(self) -> Dict[str, Union[Figure, go.Figure]]:
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
