"""
回归内部策略：根据误差分布选择图表
"""

from typing import Dict, Any, List
import numpy as np


class RegressionStrategySelector:
    """
    回归任务策略选择器
    根据回归任务的特点和误差分布选择合适的图表类型
    """

    def select_charts(self, params: Dict[str, Any]) -> List[str]:
        """
        为回归任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        selected_charts = []
        
        # 添加基本图表
        selected_charts.extend([
            "actual_vs_predicted",
            "residuals_plot"
        ])
        
        # 获取模型名称
        model_name = params.get("model_name", "").lower()
        
        # 获取测试数据
        y_test = params.get("y_test")
        model = params.get("model")
        X_test = params.get("X_test")
        
        if y_test is not None and model is not None and X_test is not None:
            try:
                # 获取预测值
                y_pred = model.predict(X_test)
                
                # 计算残差
                residuals = y_test - y_pred
                
                # 根据残差分布选择额外图表
                # 添加Q-Q图来检查残差的正态性
                selected_charts.append("qq_plot_residuals")
                
                # 根据模型类型选择特定图表
                if model_name == "linearregression":
                    # 线性回归添加系数图和诊断图
                    if X_test.shape[1] <= 10:  # 特征数适中时显示特征系数
                        selected_charts.append("feature_coefficients")
                    selected_charts.extend([
                        "cooks_distance_plot",
                        "leverage_plot"
                    ])
                elif model_name in ["decisiontreeregressor", "randomforestregressor"]:
                    # 树模型添加特征重要性图
                    if X_test.shape[1] <= 20:  # 特征数适中时显示特征重要性
                        selected_charts.append("feature_importance")
                        
                # 根据数据规模选择其他图表
                if len(y_test) <= 5000:  # 数据量不太大时添加
                    selected_charts.append("prediction_interval_plot")
                    
            except Exception as e:
                # 如果计算出错，不添加额外图表
                pass
        
        return selected_charts