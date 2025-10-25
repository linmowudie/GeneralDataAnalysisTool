"""
accuracy, precision, recall, f1
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class ClassificationMetrics:
    """
    分类任务评估指标类
    """
    
    @staticmethod
    def accuracy(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算准确率
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测标签
            
        返回:
            float: 准确率
        """
        from sklearn.metrics import accuracy_score
        return float(accuracy_score(y_true, y_pred))
        
    @staticmethod
    def precision(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算精确率
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测标签
            
        返回:
            float: 精确率
        """
        from sklearn.metrics import precision_score
        return float(precision_score(y_true, y_pred, average='macro', zero_division=0))
        
    @staticmethod
    def recall(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算召回率
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测标签
            
        返回:
            float: 召回率
        """
        from sklearn.metrics import recall_score
        return float(recall_score(y_true, y_pred, average='macro', zero_division=0))
        
    @staticmethod
    def f1_score(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算F1分数
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测标签
            
        返回:
            float: F1分数
        """
        from sklearn.metrics import f1_score
        return float(f1_score(y_true, y_pred, average='macro', zero_division=0))