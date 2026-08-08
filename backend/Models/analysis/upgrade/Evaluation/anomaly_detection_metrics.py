"""
异常检测任务评估指标类
包括 precision_at_k, roc_auc, average_precision 等指标
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, roc_auc_score, average_precision_score


class AnomalyDetectionMetrics:
    """
    异常检测任务评估指标类
    """
    
    @staticmethod
    def precision_at_k(y_true: pd.Series, y_pred: pd.Series, k: int = 10) -> float:
        """
        计算Top-K精确率
        前K个预测为异常的样本中真实异常的比例
        
        参数:
            y_true (pd.Series): 真实标签 (1表示异常, 0表示正常)
            y_pred (pd.Series): 预测分数或概率 (越高表示越可能是异常)
            k (int): Top-K的数量
            
        返回:
            float: Top-K精确率
        """
        try:
            # 获取Top-K的索引
            top_k_indices = np.argpartition(y_pred, -k)[-k:]
            
            # 获取Top-K的真实标签
            top_k_labels = y_true.iloc[top_k_indices]
            
            # 计算精确率
            precision_at_k_score = np.sum(top_k_labels) / len(top_k_labels)
            return float(precision_at_k_score)
        except Exception as e:
            print(f"计算Top-K精确率失败: {e}")
            return float('nan')
    
    @staticmethod
    def roc_auc(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算ROC曲线下面积
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测分数或概率
            
        返回:
            float: ROC AUC分数
        """
        try:
            return float(roc_auc_score(y_true, y_pred))
        except Exception as e:
            print(f"计算ROC AUC失败: {e}")
            return float('nan')
    
    @staticmethod
    def average_precision(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算平均精确率
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测分数或概率
            
        返回:
            float: 平均精确率
        """
        try:
            return float(average_precision_score(y_true, y_pred))
        except Exception as e:
            print(f"计算平均精确率失败: {e}")
            return float('nan')