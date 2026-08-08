"""backend.Models：可调用的模型汇总层（ML 模型 / 分析 / 可视化 / 清洗 / 报告）"""
from .registry import ModelRegistry, ModelMeta, model_registry
from .factory import ModelFactory, model_factory

# 分析模型门面
from .analysis import DataAnalyzer, analyze_data
# 清洗模型门面
from .cleaning import CleanData, CleanDataMode
# 可视化模型门面
from .visualization import DataVisualization, plot_registry, interactive_plot_registry
# 报告组装
from .reporting import Report

__all__ = [
    "ModelRegistry", "ModelMeta", "model_registry",
    "ModelFactory", "model_factory",
    "DataAnalyzer", "analyze_data",
    "CleanData", "CleanDataMode",
    "DataVisualization", "plot_registry", "interactive_plot_registry",
    "Report",
]
