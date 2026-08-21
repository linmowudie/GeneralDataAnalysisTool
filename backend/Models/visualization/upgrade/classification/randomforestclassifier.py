"""
随机森林分类模型可视化策略
"""

from typing import Dict, Any
from .base import ClassificationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class RandomForestClassifierStrategy(ClassificationStrategy):
    """
    随机森林分类模型可视化策略
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
        
        # 生成ROC曲线
        charts.update(self.generate_roc_curve())
            
        return charts
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def validate_params(self) -> None:
        """
        验证随机森林分类模型参数
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
        ax.set_title('随机森林混淆矩阵')
        
        return {"random_forest_confusion_matrix": fig}

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
        ax.set_title('随机森林特征重要性')
        
        return {"random_forest_feature_importance": fig}

    def generate_roc_curve(self) -> Dict[str, Figure]:
        """
        生成ROC曲线图
        """
        from ..utils.plot_roc_curve import plot_roc_curve
        
        y_test = self.params["y_test"]
        _, y_pred_proba = self._get_model_predictions()
        
        if y_pred_proba is None:
            raise ValueError("模型不支持概率预测，无法绘制ROC曲线")
        
        self.apply_styles()
        fig, ax = plot_roc_curve(y_test, y_pred_proba, figsize=(8, 6))
        ax.set_title('随机森林ROC曲线')
        
        return {"random_forest_roc_curve": fig}

    def generate_oob_error(self) -> Dict[str, Figure]:
        """
        生成袋外误差图
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        
        if not hasattr(model, "oob_score_"):
            raise ValueError("模型没有启用OOB评分")
        
        if not hasattr(model, "estimators_"):
            raise ValueError("模型没有estimators_属性")
        
        # 计算不同树数量下的OOB误差
        oob_errors = []
        n_estimators_range = range(1, len(model.estimators_) + 1)
        
        for i in n_estimators_range:
            # 这里简化处理，实际应该重新训练模型
            # 在实际应用中，需要在训练时记录每个阶段的OOB误差
            if i <= len(model.estimators_):
                oob_errors.append(1 - model.oob_score_)  # 简化处理
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(n_estimators_range, oob_errors, marker='o')
        ax.set_xlabel('树的数量')
        ax.set_ylabel('袋外误差')
        ax.set_title('随机森林袋外误差随树数量变化')
        ax.grid(True)
        
        return {"random_forest_oob_error": fig}