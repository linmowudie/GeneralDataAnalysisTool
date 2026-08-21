"""
决策树分类模型可视化策略
"""

from typing import Dict, Any
from .base import ClassificationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class DecisionTreeClassifierStrategy(ClassificationStrategy):
    """
    决策树分类模型可视化策略
    """
    
    def generate_static_charts(self):
        """
        生成静态图表
        """
        charts = {}
        
        # 生成混淆矩阵
        charts.update(self.generate_confusion_matrix())
            
        # 生成特征重要性图
        charts.update(self.generate_feature_importance())
            
        # 生成决策树结构图
        charts.update(self.generate_tree_structure())
            
        return charts
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def validate_params(self) -> None:
        """
        验证决策树分类模型参数
        """
        super().validate_params()

    def generate_confusion_matrix(self) -> Dict[str, Figure]:
        """
        生成混淆矩阵图
        """
        from ..utils.plot_confusion_matrix import plot_confusion_matrix
        
        y_test = self.params["y_test"]
        y_pred, _ = self._get_model_predictions()
        
        self.apply_styles()
        fig, ax = plot_confusion_matrix(y_test, y_pred, figsize=(8, 6))
        ax.set_title('决策树分类混淆矩阵')
        
        return {"decision_tree_confusion_matrix": fig}

    def generate_tree_structure(self) -> Dict[str, Figure]:
        """
        生成决策树结构图
        """
        try:
            from sklearn.tree import plot_tree
            import matplotlib.pyplot as plt
            
            model = self.params["model"]
            
            if not hasattr(model, "tree_"):
                raise ValueError("模型没有tree_属性，不是决策树模型")
            
            self.apply_styles()
            fig, ax = plt.subplots(figsize=(20, 10))
            
            plot_tree(model, 
                     feature_names=self.params.get("feature_names"),
                     class_names=self.params.get("class_names"),
                     filled=True, 
                     ax=ax)
            
            ax.set_title('决策树结构图')
            
            return {"decision_tree_structure": fig}
        except ImportError:
            raise ImportError("需要安装sklearn来绘制决策树结构图")

    def generate_feature_importance(self) -> Dict[str, Figure]:
        """
        生成特征重要性图
        """
        from ..utils.plot_feature_importance import plot_feature_importance
        
        model = self.params["model"]
        
        if not hasattr(model, "feature_importances_"):
            raise ValueError("模型没有feature_importances_属性")
        
        importances = model.feature_importances_
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(len(importances))])
        
        self.apply_styles()
        fig, ax = plot_feature_importance(importances, feature_names, figsize=(10, 6))
        ax.set_title('决策树特征重要性')
        
        return {"decision_tree_feature_importance": fig}