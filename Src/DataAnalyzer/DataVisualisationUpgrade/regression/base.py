"""
回归任务可视化基础策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
import numpy as np


class RegressionStrategy(VisualizationStrategy):
    """
    回归任务可视化策略基类
    """

    def validate_params(self) -> None:
        """
        验证回归任务参数
        """
        required = ["model", "X_test", "y_test"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"回归任务缺少必要参数: {param}")

    def _get_model_predictions(self):
        """
        获取模型预测结果
        """
        model = self.params["model"]
        X_test = self.params["X_test"]
        
        if hasattr(model, "predict"):
            y_pred = model.predict(X_test)
        else:
            raise ValueError("模型对象没有predict方法")
            
        return y_pred