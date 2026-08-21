"""
通用评估适配器，根据不同模型类型自动选择合适的评估指标
"""

from typing import Dict, Any, List, Union, Optional
import pandas as pd
import numpy as np

from .classification_metrics import ClassificationMetrics
from .regression_metrics import RegressionMetrics
from .clustering_metrics import ClusteringMetrics
from .dimensionality_reduction_metrics import DimensionalityReductionMetrics
from .anomaly_detection_metrics import AnomalyDetectionMetrics


class EvaluationAdapter:
    """
    评估适配器类，根据不同任务类型和模型自动选择合适的评估指标
    """
    
    # 模型到任务类型的映射
    MODEL_TASK_MAPPING = {
        # 分类模型
        'logisticregression': 'classification',
        'decisiontreeclassifier': 'classification',
        'kneighborsclassifier': 'classification',
        'randomforestclassifier': 'classification',
        'xgboostclassifier': 'classification',
        'svc': 'classification',
        
        # 回归模型
        'linearregression': 'regression',
        'decisiontreeregressor': 'regression',
        'randomforestregressor': 'regression',
        
        # 聚类模型
        'kmeans': 'clustering',
        'meanshift': 'clustering',
        'agglomerativeclustering': 'clustering',
        
        # 降维模型
        'pca': 'dimensionality_reduction',
        'tsne': 'dimensionality_reduction',
        'umap': 'dimensionality_reduction',
        
        # 异常检测模型
        'isolationforest': 'anomaly_detection',
        'localoutlierfactor': 'anomaly_detection',
    }
    
    # 任务类型对应的推荐评估指标
    RECOMMENDED_METRICS = {
        'classification': ['accuracy', 'precision', 'recall', 'f1_score'],
        'regression': ['mse', 'rmse', 'mae', 'r2'],
        'clustering': ['silhouette_score', 'calinski_harabasz_score'],
        'dimensionality_reduction': ['explained_variance_ratio', 'reconstruction_error'],
        'anomaly_detection': ['roc_auc', 'average_precision'],
    }
    
    @classmethod
    def evaluate_model(cls, 
                      model_type: str, 
                      y_true: Union[pd.Series, np.ndarray], 
                      y_pred: Union[pd.Series, np.ndarray],
                      y_pred_proba: Optional[Union[pd.Series, np.ndarray]] = None,
                      X: Optional[pd.DataFrame] = None,
                      X_reduced: Optional[pd.DataFrame] = None,
                      model_instance = None) -> Dict[str, Any]:
        """
        根据模型类型自动评估模型性能
        
        参数:
            model_type (str): 模型类型
            y_true (Union[pd.Series, np.ndarray]): 真实值
            y_pred (Union[pd.Series, np.ndarray]): 预测值
            y_pred_proba (Optional[Union[pd.Series, np.ndarray]], optional): 预测概率
            X (Optional[pd.DataFrame], optional): 原始特征数据
            X_reduced (Optional[pd.DataFrame], optional): 降维后的数据
            model_instance (optional): 模型实例
            
        返回:
            Dict[str, Any]: 评估结果字典
        """
        # 确保输入是pandas Series格式
        if isinstance(y_true, np.ndarray):
            y_true = pd.Series(y_true)
        if isinstance(y_pred, np.ndarray):
            y_pred = pd.Series(y_pred)
        if isinstance(y_pred_proba, np.ndarray):
            y_pred_proba = pd.Series(y_pred_proba)
            
        task_type = cls.MODEL_TASK_MAPPING.get(model_type.lower(), 'others')
        
        if task_type == 'classification':
            return cls._evaluate_classification(y_true, y_pred, y_pred_proba)
        elif task_type == 'regression':
            return cls._evaluate_regression(y_true, y_pred)
        elif task_type == 'clustering':
            return cls._evaluate_clustering(X, y_pred, y_true)
        elif task_type == 'dimensionality_reduction':
            return cls._evaluate_dimensionality_reduction(X, X_reduced, model_instance)
        elif task_type == 'anomaly_detection':
            return cls._evaluate_anomaly_detection(y_true, y_pred, y_pred_proba)
        else:
            return {'error': f'Unsupported model type: {model_type}'}
    
    @classmethod
    def _evaluate_classification(cls, 
                                y_true: pd.Series, 
                                y_pred: pd.Series, 
                                y_pred_proba: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        评估分类模型
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测标签
            y_pred_proba (Optional[pd.Series], optional): 预测概率
            
        返回:
            Dict[str, Any]: 分类评估结果
        """
        results = {}
        
        # 基本指标
        results['accuracy'] = ClassificationMetrics.accuracy(y_true, y_pred)
        results['precision'] = ClassificationMetrics.precision(y_true, y_pred)
        results['recall'] = ClassificationMetrics.recall(y_true, y_pred)
        results['f1_score'] = ClassificationMetrics.f1_score(y_true, y_pred)
        results['confusion_matrix'] = ClassificationMetrics.confusion_matrix(y_true, y_pred).tolist()
        
        # 概率相关指标（如果有预测概率）
        if y_pred_proba is not None:
            results['roc_auc'] = ClassificationMetrics.roc_auc(y_true, y_pred_proba)
            results['log_loss'] = ClassificationMetrics.log_loss(y_true, y_pred_proba)
            
        return results
    
    @classmethod
    def _evaluate_regression(cls, 
                            y_true: pd.Series, 
                            y_pred: pd.Series) -> Dict[str, Any]:
        """
        评估回归模型
        
        参数:
            y_true (pd.Series): 真实值
            y_pred (pd.Series): 预测值
            
        返回:
            Dict[str, Any]: 回归评估结果
        """
        results = {}
        
        results['mse'] = RegressionMetrics.mse(y_true, y_pred)
        results['rmse'] = RegressionMetrics.rmse(y_true, y_pred)
        results['mae'] = RegressionMetrics.mae(y_true, y_pred)
        results['r2'] = RegressionMetrics.r2(y_true, y_pred)
        results['explained_variance_score'] = RegressionMetrics.explained_variance_score(y_true, y_pred)
        
        return results
    
    @classmethod
    def _evaluate_clustering(cls, 
                            X: Optional[pd.DataFrame], 
                            labels: pd.Series, 
                            y_true: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        评估聚类模型
        
        参数:
            X (Optional[pd.DataFrame]): 特征数据
            labels (pd.Series): 聚类标签
            y_true (Optional[pd.Series], optional): 真实标签（如果有）
            
        返回:
            Dict[str, Any]: 聚类评估结果
        """
        results = {}
        
        # 无监督指标（需要特征数据）
        if X is not None:
            results['silhouette_score'] = ClusteringMetrics.silhouette_score(X, labels)
            results['calinski_harabasz_score'] = ClusteringMetrics.calinski_harabasz_score(X, labels)
            results['davies_bouldin_score'] = ClusteringMetrics.davies_bouldin_score(X, labels)
        
        # 有真实标签时的指标
        if y_true is not None:
            results['adjusted_rand_score'] = ClusteringMetrics.adjusted_rand_score(y_true, labels)
            hcv_results = ClusteringMetrics.homogeneity_completeness_v_measure(y_true, labels)
            results.update(hcv_results)
            
        return results
    
    @classmethod
    def _evaluate_dimensionality_reduction(cls,
                                         X_original: Optional[pd.DataFrame],
                                         X_reduced: Optional[pd.DataFrame],
                                         model_instance = None) -> Dict[str, Any]:
        """
        评估降维模型
        
        参数:
            X_original (Optional[pd.DataFrame]): 原始数据
            X_reduced (Optional[pd.DataFrame]): 降维后的数据
            model_instance (optional): 降维模型实例
            
        返回:
            Dict[str, Any]: 降维评估结果
        """
        results = {}
        
        if X_original is not None and X_reduced is not None:
            # 计算解释方差比例
            results['explained_variance_ratio'] = DimensionalityReductionMetrics.explained_variance_ratio(
                X_original, X_reduced, model_instance)
            
            # 如果模型有逆变换能力，计算重构误差
            if model_instance is not None:
                results['reconstruction_error'] = DimensionalityReductionMetrics.reconstruction_error(
                    X_original, X_reduced, model_instance)
            
            # 计算可信度和连续性
            results['trustworthiness'] = DimensionalityReductionMetrics.trustworthiness(
                X_original, X_reduced)
            results['continuity'] = DimensionalityReductionMetrics.continuity(
                X_original, X_reduced)
        
        return results
    
    @classmethod
    def _evaluate_anomaly_detection(cls,
                                  y_true: pd.Series,
                                  y_pred: pd.Series,
                                  y_pred_proba: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        评估异常检测模型
        
        参数:
            y_true (pd.Series): 真实标签
            y_pred (pd.Series): 预测分数
            y_pred_proba (Optional[pd.Series], optional): 预测概率
            
        返回:
            Dict[str, Any]: 异常检测评估结果
        """
        results = {}
        
        # 使用预测分数计算评估指标
        results['roc_auc'] = AnomalyDetectionMetrics.roc_auc(y_true, y_pred)
        results['average_precision'] = AnomalyDetectionMetrics.average_precision(y_true, y_pred)
        
        # 计算Top-K精确率
        results['precision_at_k'] = AnomalyDetectionMetrics.precision_at_k(y_true, y_pred)
        
        return results
    
    @classmethod
    def get_recommended_metrics(cls, model_type: str) -> List[str]:
        """
        获取指定模型类型的推荐评估指标
        
        参数:
            model_type (str): 模型类型
            
        返回:
            List[str]: 推荐的评估指标列表
        """
        task_type = cls.MODEL_TASK_MAPPING.get(model_type.lower(), 'others')
        return cls.RECOMMENDED_METRICS.get(task_type, [])