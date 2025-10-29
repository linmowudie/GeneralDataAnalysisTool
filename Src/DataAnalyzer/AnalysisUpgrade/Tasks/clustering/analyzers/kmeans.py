"""
KMeans聚类分析器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List, Tuple, Union
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import joblib
import logging

logger = logging.getLogger(__name__)


class KMeansAnalyzer(BaseAnalyzer):
    """
    KMeans聚类分析器，用于聚类任务
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
    
    def load_params(self, model_name: str) -> Dict[str, Any]:
        """加载和处理模型参数"""
        default_params = {
            "n_clusters": 3,
            "init": "k-means++",
            "n_init": 10,
            "max_iter": 300,
            "random_state": 42
        }
        return default_params
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, bool]:
        """验证模型参数的合法性"""
        # KMeans参数验证
        return {"valid": True}
    
    def replace_params(self, default_params: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """替换默认参数"""
        updated_params = default_params.copy()
        updated_params.update(params)
        return updated_params
    
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """数据预处理"""
        processed_X = X.copy()
        
        # 处理缺失值
        if processed_X.isnull().sum().sum() > 0:
            numeric_cols = processed_X.select_dtypes(include=[np.number]).columns
            processed_X[numeric_cols] = processed_X[numeric_cols].fillna(processed_X[numeric_cols].mean())
        
        return processed_X, y
    
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """训练KMeans模型"""
        try:
            # 获取模型参数
            if self._model_instance is not None:
                model_params = self._model_instance.get_params()
            else:
                model_params = {}
            
            # 创建模型实例
            self.model = KMeans(**model_params)
            
            # 拟合模型
            self.model.fit(X_train)
            
            logger.info("KMeans聚类模型训练成功")
            return self.model
        except Exception as e:
            logger.error(f"KMeans聚类模型训练失败: {e}")
            raise RuntimeError(f"KMeans聚类模型训练失败: {str(e)}") from e
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """训练后处理"""
        result = {}
        
        # 获取聚类中心
        if hasattr(model, 'cluster_centers_'):
            result['cluster_centers'] = model.cluster_centers_.tolist()
        
        # 获取每个样本的聚类标签
        if hasattr(model, 'labels_'):
            result['labels'] = model.labels_.tolist()
        
        # 获取惯性（簇内平方和）
        if hasattr(model, 'inertia_'):
            result['inertia'] = model.inertia_
        
        return result
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """获取特征重要性（聚类任务中特征重要性概念不明确）"""
        # 聚类任务中没有明确的特征重要性概念
        return {}
    
    def predict(self, model: Any, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """使用KMeans模型进行预测（聚类）"""
        if model is None:
            raise ValueError("模型未训练，请先训练模型")
        
        try:
            # 执行预测（聚类）
            predictions = model.predict(X)
            
            # 转换为Series并保持索引
            prediction_series = pd.Series(predictions, index=X.index)
            
            return prediction_series
        except Exception as e:
            logger.error(f"KMeans聚类预测失败: {e}")
            raise RuntimeError(f"KMeans聚类预测失败: {str(e)}") from e
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """保存模型产物"""
        try:
            # 确保保存目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存模型
            joblib.dump(model, filepath)
            
            logger.info(f"KMeans聚类模型已成功保存到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存KMeans聚类模型失败: {e}")
            return False
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """获取默认评估指标"""
        return ["silhouette_score", "calinski_harabasz_score", "davies_bouldin_score"]
    
    def build_result(self, 
                     model: Any,
                     model_score: Optional[Dict[str, float]],
                     feature_importance: Dict[str, float],
                     postprocess_result: Dict[str, Any]) -> Dict[str, Any]:
        """构建返回结果"""
        result = {
            "model": model,
            "model_score": model_score or {},
            "feature_importance": feature_importance,
        }
        
        # 添加后处理结果
        result.update(postprocess_result)
        
        return result