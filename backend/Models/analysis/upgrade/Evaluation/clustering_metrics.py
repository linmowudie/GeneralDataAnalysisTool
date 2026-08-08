"""
silhouette, calinski_harabasz, davies_bouldin, adjusted_rand, homogeneity_completeness_v_measure
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
            
    @staticmethod
    def davies_bouldin_score(X: pd.DataFrame, labels: pd.Series) -> float:
        """
        计算Davies-Bouldin指数
        
        参数:
            X (pd.DataFrame): 特征数据
            labels (pd.Series): 聚类标签
            
        返回:
            float: Davies-Bouldin指数
        """
        from sklearn.metrics import davies_bouldin_score
        try:
            return float(davies_bouldin_score(X, labels))
        except Exception as e:
            print(f"计算Davies-Bouldin指数失败: {e}")
            return float('nan')
            
    @staticmethod
    def adjusted_rand_score(y_true: pd.Series, y_pred: pd.Series) -> float:
        """
        计算调整兰德指数
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测标签
            
        返回:
            float: 调整兰德指数
        """
        from sklearn.metrics import adjusted_rand_score
        try:
            return float(adjusted_rand_score(y_true, y_pred))
        except Exception as e:
            print(f"计算调整兰德指数失败: {e}")
            return float('nan')
            
    @staticmethod
    def homogeneity_completeness_v_measure(y_true: pd.Series, y_pred: pd.Series) -> dict:
        """
        计算同质性、完整性和V-measure分数
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测标签
            
        返回:
            dict: 包含同质性、完整性和V-measure分数的字典
        """
        from sklearn.metrics import homogeneity_score, completeness_score, v_measure_score
        try:
            homogeneity = float(homogeneity_score(y_true, y_pred))
            completeness = float(completeness_score(y_true, y_pred))
            v_measure = float(v_measure_score(y_true, y_pred))
            return {
                'homogeneity': homogeneity,
                'completeness': completeness,
                'v_measure': v_measure
            }
        except Exception as e:
            print(f"计算同质性、完整性和V-measure分数失败: {e}")
            return {
                'homogeneity': float('nan'),
                'completeness': float('nan'),
                'v_measure': float('nan')
            }