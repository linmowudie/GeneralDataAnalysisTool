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
        charts = {}
        
        # 生成混淆矩阵
        charts.update(self.generate_confusion_matrix())
        
        # 生成ROC曲线
        charts.update(self.generate_roc_curve())
        
        # 生成特征系数图
        charts.update(self.generate_feature_coefficients())
        
        # 生成精确率-召回率曲线
        charts.update(self.generate_precision_recall_curve())
        
        # 生成校准曲线
        charts.update(self.generate_calibration_curve())
            
        return charts
        
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

    def generate_confusion_matrix(self) -> Dict[str, Figure]:
        """
        生成混淆矩阵图
        """
        from ..utils.plot_confusion_matrix import plot_confusion_matrix
        
        y_test = self.params["y_test"]
        y_pred, _ = self._get_model_predictions()
        
        self.apply_styles()
        fig, ax = plot_confusion_matrix(y_test, y_pred, figsize=(8, 6))
        ax.set_title('逻辑回归混淆矩阵')
        
        return {"logistic_regression_confusion_matrix": fig}

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
        ax.set_title('逻辑回归ROC曲线')
        
        return {"logistic_regression_roc_curve": fig}

    def generate_feature_coefficients(self) -> Dict[str, Figure]:
        """
        生成特征系数图
        """
        from ..utils.plot_coefficients import plot_coefficients
        
        model = self.params["model"]
        
        if not hasattr(model, "coef_"):
            raise ValueError("模型没有coef_属性")
        
        coef = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(len(coef))])
        
        self.apply_styles()
        fig, ax = plot_coefficients(coef, feature_names, figsize=(10, 6))
        ax.set_title('逻辑回归特征系数')
        
        return {"logistic_regression_feature_coefficients": fig}

    def generate_precision_recall_curve(self) -> Dict[str, Figure]:
        """
        生成精确率-召回率曲线
        """
        from ..utils.plot_precision_recall_curve import plot_precision_recall_curve
        
        y_test = self.params["y_test"]
        _, y_pred_proba = self._get_model_predictions()
        
        if y_pred_proba is None:
            raise ValueError("模型不支持概率预测，无法绘制精确率-召回率曲线")
        
        self.apply_styles()
        fig, ax = plot_precision_recall_curve(y_test, y_pred_proba, figsize=(8, 6))
        ax.set_title('逻辑回归精确率-召回率曲线')
        
        return {"logistic_regression_precision_recall_curve": fig}

    def generate_calibration_curve(self) -> Dict[str, Figure]:
        """
        生成校准曲线
        """
        try:
            from sklearn.calibration import calibration_curve
            import matplotlib.pyplot as plt
            
            y_test = self.params["y_test"]
            _, y_pred_proba = self._get_model_predictions()
            
            if y_pred_proba is None:
                raise ValueError("模型不支持概率预测，无法绘制校准曲线")
            
            if len(np.unique(y_test)) == 2:
                # 二分类情况
                fraction_of_positives, mean_predicted_value = calibration_curve(
                    y_test, y_pred_proba[:, 1], n_bins=10)
                
                self.apply_styles()
                fig, ax = plt.subplots(figsize=(8, 6))
                
                ax.plot(mean_predicted_value, fraction_of_positives, "s-", label="逻辑回归")
                ax.plot([0, 1], [0, 1], "k:", label="完美校准")
                
                ax.set_xlabel("预测概率")
                ax.set_ylabel("实际概率")
                ax.set_title("逻辑回归校准曲线")
                ax.legend()
                
                return {"logistic_regression_calibration_curve": fig}
            else:
                # 多分类情况不支持校准曲线
                raise ValueError("多分类模型不支持校准曲线")
        except ImportError:
            raise ImportError("需要安装sklearn来绘制校准曲线")