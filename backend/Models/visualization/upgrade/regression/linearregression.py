"""
线性回归模型可视化策略
"""

from typing import Dict, Any
from .base import RegressionStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class LinearRegressionStrategy(RegressionStrategy):
    """
    线性回归模型可视化策略
    """
    
    def generate_static_charts(self):
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
        
        # 生成特征系数图
        try:
            feature_coefficients_charts = self.generate_feature_coefficients()
            charts.update(feature_coefficients_charts)
        except Exception:
            pass  # 如果无法生成特征系数图，则跳过
        
        return charts
        
    def generate_interactive_charts(self):
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
        ax.set_title('线性回归实际值 vs 预测值')
        
        return {"linear_regression_actual_vs_predicted": fig}

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
        ax.set_title('线性回归残差图')
        
        return {"linear_regression_residuals_plot": fig}

    def generate_feature_coefficients(self) -> Dict[str, Figure]:
        """
        生成特征系数图
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        
        if not hasattr(model, "coef_"):
            raise ValueError("模型没有coef_属性")
        
        coef = model.coef_
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
        ax.set_title('线性回归特征系数')
        
        return {"linear_regression_feature_coefficients": fig}