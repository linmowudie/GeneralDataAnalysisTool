"""
逻辑回归分类模型可视化策略
"""

from typing import Dict, Any
from .base import ClassificationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class LogisticRegressionStrategy(ClassificationStrategy):
    """
    逻辑回归模型可视化策略
    """
    
    def generate_static_charts(self):
        """
        生成静态图表
        """
        # 默认实现，可以被子类覆盖
        return {}
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def validate_params(self) -> None:
        """
        验证逻辑回归模型参数
        """
        super().validate_params()
        # 确保是二分类问题
        y_test = self.params["y_test"]
        if len(np.unique(y_test)) != 2:
            raise ValueError("逻辑回归可视化当前仅支持二分类问题")

    def generate_confusion_matrix(self) -> Dict[str, Figure]:
        """
        生成混淆矩阵图
        """
        from sklearn.metrics import confusion_matrix
        import matplotlib.pyplot as plt
        
        y_test = self.params["y_test"]
        y_pred, _ = self._get_model_predictions()
        
        cm = confusion_matrix(y_test, y_pred)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
        ax.figure.colorbar(im, ax=ax)
        
        # 标注
        tick_marks = np.arange(len(cm))
        ax.set_xticks(tick_marks)
        ax.set_yticks(tick_marks)
        
        # 添加数值标注
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], 'd'),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")
        
        ax.set_xlabel('预测标签')
        ax.set_ylabel('真实标签')
        ax.set_title('逻辑回归混淆矩阵')
        
        return {"logistic_regression_confusion_matrix": fig}

    def generate_roc_curve(self) -> Dict[str, Figure]:
        """
        生成ROC曲线图
        """
        from sklearn.metrics import roc_curve, auc
        import matplotlib.pyplot as plt
        
        y_test = self.params["y_test"]
        _, y_pred_proba = self._get_model_predictions()
        
        if y_pred_proba is None:
            raise ValueError("模型不支持概率预测，无法绘制ROC曲线")
        
        # 二分类情况
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba[:, 1])
        roc_auc = auc(fpr, tpr)
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(fpr, tpr, label=f'ROC曲线 (AUC = {roc_auc:.2f})')
        ax.plot([0, 1], [0, 1], 'k--', label='随机分类器')
        ax.set_xlim(0.0, 1.0)
        ax.set_ylim(0.0, 1.05)
        ax.set_xlabel('假正率')
        ax.set_ylabel('真正率')
        ax.set_title('逻辑回归ROC曲线')
        ax.legend(loc="lower right")
        
        return {"logistic_regression_roc_curve": fig}

    def generate_feature_coefficients(self) -> Dict[str, Figure]:
        """
        生成特征系数图
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        
        if not hasattr(model, "coef_"):
            raise ValueError("模型没有coef_属性")
        
        coef = model.coef_[0]
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(len(coef))])
        
        # 排序特征系数
        sorted_idx = np.argsort(np.abs(coef))[::-1]
        sorted_coef = coef[sorted_idx]
        sorted_features = [feature_names[i] for i in sorted_idx]
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        y_pos = np.arange(len(sorted_coef))
        colors = ['red' if c < 0 else 'blue' for c in sorted_coef]
        
        ax.barh(y_pos, sorted_coef, color=colors)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(sorted_features)
        ax.set_xlabel('系数值')
        ax.set_title('逻辑回归特征系数')
        
        return {"logistic_regression_feature_coefficients": fig}