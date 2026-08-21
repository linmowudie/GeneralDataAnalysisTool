"""
降维任务评估指标类
包括 explained_variance_ratio, reconstruction_error, trustworthiness, continuity 等指标
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.metrics import explained_variance_score, mean_squared_error
from sklearn.manifold import trustworthiness as sklearn_trustworthiness
from sklearn.neighbors import NearestNeighbors


class DimensionalityReductionMetrics:
    """
    降维任务评估指标类
    """
    
    @staticmethod
    def explained_variance_ratio(X_original: pd.DataFrame, X_reduced: pd.DataFrame, 
                                pca_model=None) -> float:
        """
        计算解释方差比例
        
        参数:
            X_original (pd.DataFrame): 原始数据
            X_reduced (pd.DataFrame): 降维后的数据
            pca_model (optional): PCA模型实例，如果有可以用来直接获取解释方差比例
            
        返回:
            float: 解释方差比例
        """
        try:
            if pca_model is not None and hasattr(pca_model, 'explained_variance_ratio_'):
                # 如果提供了PCA模型，直接返回累计解释方差比例
                return float(np.sum(pca_model.explained_variance_ratio_))
            else:
                # 否则通过计算原始数据和降维数据的方差来估算
                from sklearn.decomposition import PCA
                # 这里我们假设降维到X_reduced的维度
                n_components = X_reduced.shape[1]
                pca_temp = PCA(n_components=n_components)
                pca_temp.fit(X_original)
                return float(np.sum(pca_temp.explained_variance_ratio_))
        except Exception as e:
            print(f"计算解释方差比例失败: {e}")
            return float('nan')
    
    @staticmethod
    def reconstruction_error(X_original: pd.DataFrame, X_reduced: pd.DataFrame, 
                           transformer_model=None) -> float:
        """
        计算重构误差
        
        参数:
            X_original (pd.DataFrame): 原始数据
            X_reduced (pd.DataFrame): 降维后的数据
            transformer_model (optional): 降维模型实例，需要有inverse_transform方法
            
        返回:
            float: 重构误差 (MSE)
        """
        try:
            if transformer_model is not None and hasattr(transformer_model, 'inverse_transform'):
                # 使用模型的逆变换重构数据
                X_reconstructed = transformer_model.inverse_transform(X_reduced)
                # 计算重构误差
                return float(mean_squared_error(X_original, X_reconstructed))
            else:
                # 如果没有提供模型，返回NaN
                print("需要提供具有inverse_transform方法的模型来计算重构误差")
                return float('nan')
        except Exception as e:
            print(f"计算重构误差失败: {e}")
            return float('nan')
    
    @staticmethod
    def trustworthiness(X_original: pd.DataFrame, X_reduced: pd.DataFrame, 
                       n_neighbors: int = 5) -> float:
        """
        计算可信度（Trustworthiness）
        衡量局部邻域结构在降维后是否保持
        
        参数:
            X_original (pd.DataFrame): 原始高维数据
            X_reduced (pd.DataFrame): 降维后的低维数据
            n_neighbors (int): 邻居数量
            
        返回:
            float: 可信度得分
        """
        try:
            score = sklearn_trustworthiness(X_original, X_reduced, n_neighbors=n_neighbors)
            return float(score)
        except Exception as e:
            print(f"计算可信度失败: {e}")
            return float('nan')
    
    @staticmethod
    def continuity(X_original: pd.DataFrame, X_reduced: pd.DataFrame, 
                  n_neighbors: int = 5) -> float:
        """
        计算连续性（Continuity）
        衡量全局结构是否在映射中保持
        
        参数:
            X_original (pd.DataFrame): 原始高维数据
            X_reduced (pd.DataFrame): 降维后的低维数据
            n_neighbors (int): 邻居数量
            
        返回:
            float: 连续性得分
        """
        try:
            # sklearn没有直接提供连续性计算，我们需要自己实现
            # 这里使用一种近似方法计算连续性
            from sklearn.neighbors import NearestNeighbors
            
            # 计算原始空间中的k近邻
            nn_orig = NearestNeighbors(n_neighbors=n_neighbors + 1)
            nn_orig.fit(X_original)
            orig_kneighbors = nn_orig.kneighbors(X_original, return_distance=False)
            orig_indices = np.array([row[1:] for row in orig_kneighbors])  # 排除自己
            
            # 计算降维空间中的k近邻
            nn_reduced = NearestNeighbors(n_neighbors=n_neighbors + 1)
            nn_reduced.fit(X_reduced)
            reduced_kneighbors = nn_reduced.kneighbors(X_reduced, return_distance=False)
            reduced_indices = np.array([row[1:] for row in reduced_kneighbors])  # 排除自己
            
            n_samples = X_original.shape[0]
            continuity_score = 0.0
            
            # 计算连续性
            for i in range(n_samples):
                # 在降维空间中是邻居但在原始空间中不是邻居的点
                missing_neighbors = set(reduced_indices[i]) - set(orig_indices[i])
                for j in missing_neighbors:
                    # 找到j在原始空间中的排名
                    kneighbors_result = nn_orig.kneighbors([X_original.iloc[i]], return_distance=False)[0]
                    kneighbors_subset = kneighbors_result[1:]
                    rank_in_original = np.where(kneighbors_subset == j)[0]
                    if len(rank_in_original) > 0:
                        rank = rank_in_original[0] + 1  # +1因为索引从0开始
                        continuity_score += max(0, (rank - n_neighbors) / n_neighbors)
            
            continuity_score = 1.0 - continuity_score / (n_samples * n_neighbors)
            return float(continuity_score)
        except Exception as e:
            print(f"计算连续性失败: {e}")
            return float('nan')