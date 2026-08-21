"""
XGBoost分类模型可视化策略
"""

from typing import Dict, Any
from .base import ClassificationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class XGBoostClassifierStrategy(ClassificationStrategy):
    """
    XGBoost分类模型可视化策略
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
        
        # 生成特征重要性图
        charts.update(self.generate_feature_importance())
        
        # 生成增益重要性图
        charts.update(self.generate_gain_importance())
            
        return charts
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def validate_params(self) -> None:
        """
        验证XGBoost分类模型参数
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
        ax.set_title('XGBoost混淆矩阵')
        
        return {"xgboost_confusion_matrix": fig}

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
        ax.set_title('XGBoostROC曲线')
        
        return {"xgboost_roc_curve": fig}

    def generate_feature_importance(self) -> Dict[str, Figure]:
        """
        生成特征重要性图
        """
        from ..utils.plot_feature_importance import plot_feature_importance
        
        model = self.params["model"]
        
        # XGBoost有多种特征重要性计算方式
        if not (hasattr(model, "feature_importances_") or hasattr(model, "get_booster")):
            raise ValueError("模型没有特征重要性属性")
        
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        else:
            # 对于XGBoost原生模型
            booster = model.get_booster()
            importance_dict = booster.get_score(importance_type='weight')
            feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(len(importance_dict))])
            importances = [importance_dict.get(f'f{i}', 0) for i in range(len(feature_names))]
        
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(len(importances))])
        
        self.apply_styles()
        fig, ax = plot_feature_importance(importances, feature_names, figsize=(10, 6))
        ax.set_title('XGBoost特征重要性')
        
        return {"xgboost_feature_importance": fig}

    def generate_gain_importance(self) -> Dict[str, Figure]:
        """
        生成增益重要性图
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        
        try:
            # 尝试获取增益重要性
            if hasattr(model, "get_booster"):
                booster = model.get_booster()
                gain_dict = booster.get_score(importance_type='gain')
                feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(len(gain_dict))])
                gains = [gain_dict.get(f'f{i}', 0) for i in range(len(feature_names))]
                
                # 排序
                sorted_idx = np.argsort(gains)[::-1]
                sorted_gains = gains[sorted_idx]
                sorted_features = [feature_names[i] for i in sorted_idx]
                
                self.apply_styles()
                fig, ax = plt.subplots(figsize=(10, 6))
                
                y_pos = np.arange(len(sorted_gains))
                ax.barh(y_pos, sorted_gains)
                ax.set_yticks(y_pos)
                ax.set_yticklabels(sorted_features)
                ax.set_xlabel('增益')
                ax.set_title('XGBoost增益重要性')
                
                return {"xgboost_gain_importance": fig}
            else:
                raise ValueError("模型不支持增益重要性计算")
        except Exception as e:
            raise ValueError(f"无法生成增益重要性图: {str(e)}")