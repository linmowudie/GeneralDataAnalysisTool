"""
silhouette, calinski_harabasz
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class ClusteringMetrics:
    """
    聚类任务评估指标类
    """
    
    @staticmethod
    def silhouette_score(X: pd.DataFrame, labels: pd.Series) -> float:
        """
        计算轮廓系数
        
        参数:
            X (pd.DataFrame): 特征数据
            labels (pd.Series): 聚类标签
            
        返回:
            float: 轮廓系数
        """
        from sklearn.metrics import silhouette_score
        try:
            return float(silhouette_score(X, labels))
        except Exception as e:
            print(f"计算轮廓系数失败: {e}")
            return float('nan')
        
    @staticmethod
    def calinski_harabasz_score(X: pd.DataFrame, labels: pd.Series) -> float:
        """
        计算Calinski-Harabasz指数
        
        参数:
            X (pd.DataFrame): 特征数据
            labels (pd.Series): 聚类标签
            
        返回:
            float: Calinski-Harabasz指数
        """
        from sklearn.metrics import calinski_harabasz_score
        try:
            return float(calinski_harabasz_score(X, labels))
        except Exception as e:
            print(f"计算Calinski-Harabasz指数失败: {e}")
            return float('nan')