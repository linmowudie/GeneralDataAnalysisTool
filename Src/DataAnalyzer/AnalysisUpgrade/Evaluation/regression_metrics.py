"""
mse, mae, r2
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class RegressionMetrics:
    """
    回归任务评估指标类
    """
    
    @staticmethod
    def mse(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算均方误差
        
        参数:
            y_true (pd.Series): 真实值
            y_pred (pd.Series): 预测值
            
        返回:
            float: 均方误差
        """
        from sklearn.metrics import mean_squared_error
        return float(mean_squared_error(y_true, y_pred))
        
    @staticmethod
    def mae(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算平均绝对误差
        
        参数:
            y_true (pd.Series): 真实值
            y_pred (pd.Series): 预测值
            
        返回:
            float: 平均绝对误差
        """
        from sklearn.metrics import mean_absolute_error
        return float(mean_absolute_error(y_true, y_pred))
        
    @staticmethod
    def r2(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算R2分数
        
        参数:
            y_true (pd.Series): 真实值
            y_pred (pd.Series): 预测值
            
        返回:
            float: R2分数
        """
        from sklearn.metrics import r2_score
        return float(r2_score(y_true, y_pred))