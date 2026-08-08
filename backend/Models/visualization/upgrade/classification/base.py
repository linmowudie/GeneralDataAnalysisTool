"""
分类任务可视化基础策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
import numpy as np


class ClassificationStrategy(VisualizationStrategy):
    """
    分类任务可视化策略基类
    """

    def validate_params(self) -> None:
        """
        验证分类任务参数
        """
        required = ["model", "X_test", "y_test"]
        for param in required:
            if param not in self.params:
                raise ValueError(f"分类任务缺少必要参数: {param}")

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
            
        if hasattr(model, "predict_proba"):
            try:
                y_pred_proba = model.predict_proba(X_test)
            except:
                y_pred_proba = None
        else:
            y_pred_proba = None
            
        return y_pred, y_pred_proba