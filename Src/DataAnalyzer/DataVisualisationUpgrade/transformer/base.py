"""
变换器任务可视化基础策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
import numpy as np


class TransformerStrategy(VisualizationStrategy):
    """
    变换器任务可视化策略基类
    """

    def validate_params(self) -> None:
        """
        验证变换器任务参数
        """
        required = ["X_train"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"变换器任务缺少必要参数: {param}")
                
    def _get_training_data(self):
        """
        获取训练数据
        """
        X_train = self.params.get("X_train")
        if X_train is None:
            raise ValueError("无法获取训练数据")
        return X_train