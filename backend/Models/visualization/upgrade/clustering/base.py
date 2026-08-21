"""
聚类任务可视化基础策略
"""

from typing import Dict, Any
from ..base_visualization import VisualizationStrategy
import numpy as np


class ClusteringStrategy(VisualizationStrategy):
    """
    聚类任务可视化策略基类
    """

    def validate_params(self) -> None:
        """
        验证聚类任务参数
        """
        # 检查是否提供了特征数据
        if "X" not in self.params and "X_train" not in self.params:
            raise ValueError("聚类任务需要提供特征数据(X或X_train)")
            
        # 检查是否提供了标签或模型
        if "labels" not in self.params and "model" not in self.params:
            raise ValueError("聚类任务需要提供标签(labels)或模型(model)")

    def _get_cluster_labels(self):
        """
        获取聚类标签
        """
        if "labels" in self.params:
            return self.params["labels"]
        
        if "model" in self.params:
            model = self.params["model"]
            if hasattr(model, "labels_"):
                return model.labels_
            elif hasattr(model, "predict"):
                X = self.params.get("X", self.params.get("X_train"))
                if X is not None:
                    return model.predict(X)
                else:
                    raise ValueError("模型需要特征数据进行预测")
            else:
                raise ValueError("模型对象没有标签或预测方法")
        
        raise ValueError("无法获取聚类标签")
        
    def _get_feature_data(self):
        """
        获取特征数据
        """
        X = self.params.get("X", self.params.get("X_train"))
        if X is None:
            raise ValueError("无法获取特征数据")
        return X