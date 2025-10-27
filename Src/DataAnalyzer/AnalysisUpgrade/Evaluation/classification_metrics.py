"""
accuracy, precision, recall, f1, roc_auc, log_loss, confusion_matrix
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
        return float(precision_score(y_true, y_pred, average='macro', zero_division='warn'))
        
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
        return float(recall_score(y_true, y_pred, average='macro', zero_division='warn'))
        
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
        return float(f1_score(y_true, y_pred, average='macro', zero_division='warn'))
        
    @staticmethod
    def roc_auc(y_true: pd.Series, y_pred_proba: pd.Series, average: str = 'macro') -> float:
        """
        计算ROC曲线下面积
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred_proba (pd.Series): 预测概率
            average (str): 平均方法 ('macro', 'micro', 'weighted')
            
        返回:
            float: ROC AUC分数
        """
        from sklearn.metrics import roc_auc_score
        try:
            # 处理多分类情况
            if len(np.unique(y_true)) > 2:
                return float(roc_auc_score(y_true, y_pred_proba, multi_class='ovr', average=average))
            else:
                return float(roc_auc_score(y_true, y_pred_proba, average=average))
        except Exception as e:
            print(f"计算ROC AUC失败: {e}")
            return float('nan')
        
    @staticmethod
    def log_loss(y_true: pd.Series, y_pred_proba: pd.Series) -> float:
        """
        计算对数损失
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred_proba (pd.Series): 预测概率
            
        返回:
            float: 对数损失
        """
        from sklearn.metrics import log_loss
        try:
            return float(log_loss(y_true, y_pred_proba))
        except Exception as e:
            print(f"计算对数损失失败: {e}")
            return float('nan')
        
    @staticmethod
    def confusion_matrix(y_true: pd.Series, y_pred: pd.Series) -> np.ndarray:
        """
        计算混淆矩阵
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测标签
            
        返回:
            np.ndarray: 混淆矩阵
        """
        from sklearn.metrics import confusion_matrix
        try:
            return confusion_matrix(y_true, y_pred)
        except Exception as e:
            print(f"计算混淆矩阵失败: {e}")
            return np.array([])