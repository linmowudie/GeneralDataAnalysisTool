"""
决策树回归模型可视化策略
"""

from typing import Dict, Any
from .base import RegressionStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class DecisionTreeRegressorStrategy(RegressionStrategy):
    """
    决策树回归模型可视化策略
    """
    
    def validate_params(self) -> None:
        """
        验证决策树回归参数
        """
        super().validate_params()
        # 决策树回归可以使用基础验证

    def generate_static_charts(self) -> Dict[str, Figure]:
        """
        生成静态图表
        """
        charts = {}
        
        # 生成实际值vs预测值图
        actual_vs_predicted_charts = self.generate_actual_vs_predicted()
        charts.update(actual_vs_predicted_charts)
        
        # 生成残差图
        residuals_charts = self.generate_residuals_plot()
        charts.update(residuals_charts)
        
        # 生成特征重要性图
        try:
            feature_importance_charts = self.generate_feature_importance()
            charts.update(feature_importance_charts)
        except Exception:
            pass  # 如果无法生成特征重要性图，则跳过
        
        return charts
        
    def generate_interactive_charts(self) -> Dict[str, go.Figure]:
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def generate_actual_vs_predicted(self) -> Dict[str, Figure]:
        """
        生成实际值vs预测值图
        """
        import matplotlib.pyplot as plt
        
        X_test, y_test = self._get_test_data()
        y_pred = self._get_model_predictions()
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 绘制散点图
        ax.scatter(y_test, y_pred, alpha=0.7)
        
        # 绘制完美预测线
        min_val = min(min(y_test), min(y_pred))
        max_val = max(max(y_test), max(y_pred))
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        
        ax.set_xlabel('实际值')
        ax.set_ylabel('预测值')
        ax.set_title('决策树回归实际值 vs 预测值')
        
        return {"decision_tree_regressor_actual_vs_predicted": fig}

    def generate_residuals_plot(self) -> Dict[str, Figure]:
        """
        生成残差图
        """
        import matplotlib.pyplot as plt
        
        X_test, y_test = self._get_test_data()
        y_pred = self._get_model_predictions()
        
        # 计算残差
        residuals = y_test - y_pred
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 绘制残差散点图
        ax.scatter(y_pred, residuals, alpha=0.7)
        ax.axhline(y=0, color='r', linestyle='--')
        
        ax.set_xlabel('预测值')
        ax.set_ylabel('残差')
        ax.set_title('决策树回归残差图')
        
        return {"decision_tree_regressor_residuals_plot": fig}

    def generate_feature_importance(self) -> Dict[str, Figure]:
        """
        生成特征重要性图
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        
        if not hasattr(model, "feature_importances_"):
            raise ValueError("模型没有feature_importances_属性")
        
        importances = model.feature_importances_
        feature_names = self.params.get("feature_names", [f"特征{i}" for i in range(len(importances))])
        
        # 排序特征重要性
        sorted_idx = np.argsort(importances)[::-1]
        sorted_importances = importances[sorted_idx]
        sorted_features = [feature_names[i] for i in sorted_idx]
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        y_pos = np.arange(len(sorted_importances))
        
        ax.barh(y_pos, sorted_importances, color='skyblue')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(sorted_features)
        ax.set_xlabel('重要性')
        ax.set_title('决策树回归特征重要性')
        
        return {"decision_tree_regressor_feature_importance": fig}