"""
backend/Models/visualization/upgrade/factory.py
新版数据可视化模块工厂文件（原 Engine/DataVisualisationUpgrade/factory.py 迁入）

负责根据模型类型和任务类型创建相应的可视化策略实例。
"""

import json
import os
from typing import Dict, Any, List
from .base_visualization import VisualizationStrategy

# backend 目录（当前文件位于 backend/Models/visualization/upgrade/）
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CONFIG_PATH = os.path.join(_BACKEND_DIR, "Infrastructures", "Configs", "model_visualization.json")


class VisualizationFactory:
    """
    可视化工厂类
    负责根据模型类型和任务类型创建相应的可视化策略实例
    """

    def __init__(self):
        """
        初始化工厂类，加载配置文件
        """
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        加载模型可视化配置文件
        
        Returns:
            配置字典
        """
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {CONFIG_PATH}")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件格式错误: {CONFIG_PATH}")
            
    def get_model_supported_tasks(self, model_name: str) -> List[str]:
        """
        获取模型支持的任务类型
        
        Args:
            model_name: 模型名称
            
        Returns:
            支持的任务类型列表
        """
        supported_tasks = []
        task_config = self.config.get("task", {})
        
        # 遍历所有任务类型查找支持的模型
        for task_type, models in task_config.items():
            # 跳过common类型，因为它不是具体的任务类型
            if task_type == "common":
                continue
                
            # 检查模型是否在该任务类型中
            if model_name.lower() in [m.lower() for m in models.keys()]:
                supported_tasks.append(task_type)
                
        return supported_tasks
        
    def get_supported_models(self) -> List[str]:
        """
        获取所有支持的模型列表
        
        Returns:
            支持的模型列表
        """
        return self.config.get("supported_models", [])
        
    def is_common_chart(self, chart_type: str) -> bool:
        """
        判断是否为通用图表类型
        
        Args:
            chart_type: 图表类型
            
        Returns:
            是否为通用图表
        """
        common_charts = self.config.get("task", {}).get("common", [])
        return chart_type.lower() in [c.lower() for c in common_charts]
        
    def create_visualization_strategy(
        self, 
        model_name: str, 
        task_type: str, 
        params: Dict[str, Any]
    ) -> VisualizationStrategy:
        """
        创建可视化策略实例
        
        Args:
            model_name: 模型名称
            task_type: 任务类型
            params: 参数字典
            
        Returns:
            可视化策略实例
        """
        # 检查是否为通用图表
        task_list = params.get("task_list", [])
        if task_list and len(task_list) > 0:
            # 如果任务列表中的第一个任务是通用图表，则创建通用图表策略
            if self.is_common_chart(task_list[0]):
                return self._create_common_strategy(task_list[0], params)
                
        # 根据任务类型创建特定策略
        if task_type == "classification":
            return self._create_classification_strategy(model_name, params)
        elif task_type == "regression":
            return self._create_regression_strategy(model_name, params)
        elif task_type == "clustering":
            return self._create_clustering_strategy(model_name, params)
        elif task_type == "transformer":
            return self._create_transformer_strategy(model_name, params)
        else:
            raise ValueError(f"不支持的任务类型: {task_type}")
            
    def select_charts(
        self,
        model_name: str,
        task_type: str,
        params: Dict[str, Any]
    ) -> list:
        """
        根据任务类型和模型选择合适的图表类型
        
        Args:
            model_name: 模型名称
            task_type: 任务类型
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        # 导入策略选择器
        from .strategy import VisualizationStrategySelector
        selector = VisualizationStrategySelector()
        
        # 根据任务类型选择图表
        return selector.select_charts(task_type, params)
            
    def _create_common_strategy(
        self, 
        chart_type: str, 
        params: Dict[str, Any]
    ) -> VisualizationStrategy:
        """
        创建通用图表策略
        
        Args:
            chart_type: 图表类型
            params: 参数字典
            
        Returns:
            通用图表策略实例
        """
        # 根据图表类型创建对应的策略
        if chart_type.lower() == "scatter":
            try:
                from .common.scatter import ScatterPlotStrategy
                return ScatterPlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "line":
            try:
                from .common.line import LinePlotStrategy
                return LinePlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "bar":
            try:
                from .common.bar import BarPlotStrategy
                return BarPlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "histogram":
            try:
                from .common.histogram import HistogramStrategy
                return HistogramStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "box":
            try:
                from .common.box import BoxPlotStrategy
                return BoxPlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "heatmap":
            try:
                from .common.heatmap import HeatmapStrategy
                return HeatmapStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "violin_plot":
            try:
                from .common.violin_plot import ViolinPlotStrategy
                return ViolinPlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "pair_plot":
            try:
                from .common.pair_plot import PairPlotStrategy
                return PairPlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "density_contour_plot":
            try:
                from .common.density_contour_plot import DensityContourPlotStrategy
                return DensityContourPlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "bubble_plot":
            try:
                from .common.bubble_plot import BubblePlotStrategy
                return BubblePlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "area_plot":
            try:
                from .common.area_plot import AreaPlotStrategy
                return AreaPlotStrategy(params)
            except ImportError:
                pass
        elif chart_type.lower() == "step_plot":
            try:
                from .common.step_plot import StepPlotStrategy
                return StepPlotStrategy(params)
            except ImportError:
                pass
        # 如果没有找到特定的策略类，则使用基础策略
        return BasicVisualizationStrategy(params)

    def _create_classification_strategy(
        self, 
        model_name: str, 
        params: Dict[str, Any]
    ) -> VisualizationStrategy:
        """
        创建分类任务策略
        
        Args:
            model_name: 模型名称
            params: 参数字典
            
        Returns:
            分类任务策略实例
        """
        # 根据具体的模型名称创建对应的策略
        if model_name.lower() == "logisticregression":
            try:
                from .classification.logisticregression import LogisticRegressionStrategy
                return LogisticRegressionStrategy(params)
            except ImportError:
                pass
        
        # 如果没有找到特定的策略类，则使用基础策略
        from .base_visualization import VisualizationStrategy
        return BasicVisualizationStrategy(params)
        
    def _create_regression_strategy(
        self, 
        model_name: str, 
        params: Dict[str, Any]
    ) -> VisualizationStrategy:
        """
        创建回归任务策略
        
        Args:
            model_name: 模型名称
            params: 参数字典
            
        Returns:
            回归任务策略实例
        """
        # 根据具体的模型名称创建对应的策略
        if model_name.lower() == "linearregression":
            try:
                from .regression.linearregression import LinearRegressionStrategy
                return LinearRegressionStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() == "decisiontreeregressor":
            try:
                from .regression.decisiontreeregressor import DecisionTreeRegressorStrategy
                return DecisionTreeRegressorStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() == "randomforestregressor":
            try:
                from .regression.randomforestregressor import RandomForestRegressorStrategy
                return RandomForestRegressorStrategy(params)
            except ImportError:
                pass
        
        # 如果没有找到特定的策略类，则使用基础策略
        from .base_visualization import VisualizationStrategy
        return BasicVisualizationStrategy(params)
        
    def _create_clustering_strategy(
        self, 
        model_name: str, 
        params: Dict[str, Any]
    ) -> VisualizationStrategy:
        """
        创建聚类任务策略
        
        Args:
            model_name: 模型名称
            params: 参数字典
            
        Returns:
            聚类任务策略实例
        """
        # 根据具体的模型名称创建对应的策略
        if model_name.lower() == "kmeans":
            try:
                from .clustering.kmeans import KMeansStrategy
                return KMeansStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() == "meanshift":
            try:
                from .clustering.meanshift import MeanShiftStrategy
                return MeanShiftStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() in ["agglomerativeclustering", "hierarchical"]:
            try:
                from .clustering.agglomerativeclustering import AgglomerativeClusteringStrategy
                return AgglomerativeClusteringStrategy(params)
            except ImportError:
                pass
        
        # 如果没有找到特定的策略类，则使用基础策略
        from .base_visualization import VisualizationStrategy
        return BasicVisualizationStrategy(params)
        
    def _create_transformer_strategy(
        self, 
        model_name: str, 
        params: Dict[str, Any]
    ) -> VisualizationStrategy:
        """
        创建变换器任务策略
        
        Args:
            model_name: 模型名称
            params: 参数字典
            
        Returns:
            变换器任务策略实例
        """
        # 根据具体的模型名称创建对应的策略
        if model_name.lower() == "pca":
            try:
                from .transformer.pca import PCAStrategy
                return PCAStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() == "standardscaler":
            try:
                from .transformer.standardscaler import StandardScalerStrategy
                return StandardScalerStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() == "tsne":
            try:
                from .transformer.tsne import TSNEStrategy
                return TSNEStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() == "umap":
            try:
                from .transformer.umap import UMAPStrategy
                return UMAPStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() == "three_d":
            try:
                from .transformer.three_d import ThreeDStrategy
                return ThreeDStrategy(params)
            except ImportError:
                pass
        elif model_name.lower() == "no_model":
            try:
                from .transformer.no_model import NoModelStrategy
                return NoModelStrategy(params)
            except ImportError:
                pass
        
        # 如果没有找到特定的策略类，则使用基础策略
        from .base_visualization import VisualizationStrategy
        return BasicVisualizationStrategy(params)


class BasicVisualizationStrategy(VisualizationStrategy):
    """
    基础可视化策略实现类
    用于占位和基本功能实现
    """
    
    def validate_params(self) -> None:
        """
        验证参数
        """
        # 基础实现，不做特殊验证
        pass
        
    def generate_static_charts(self):
        """
        生成静态图表
        
        Returns:
            包含图表名称和Figure对象的字典
        """
        from matplotlib.figure import Figure
        return {"basic_chart": Figure()}
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        
        Returns:
            包含图表名称和plotly Figure对象的字典
        """
        import plotly.graph_objects as go
        return {"basic_interactive_chart": go.Figure()}