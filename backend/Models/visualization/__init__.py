"""backend.Models.visualization：可视化模型（原 Engine/VisualizationModule + DataVisualisationUpgrade 迁入）"""
from .dispatcher import DataVisualization
from .registry import plot_registry
from .interactive_registry import interactive_plot_registry

__all__ = ["DataVisualization", "plot_registry", "interactive_plot_registry"]
