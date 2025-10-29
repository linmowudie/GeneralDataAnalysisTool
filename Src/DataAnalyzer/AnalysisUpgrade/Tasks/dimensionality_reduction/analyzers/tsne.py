"""
t-SNE降维分析器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List, Tuple, Union
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
import joblib
import logging

logger = logging.getLogger(__name__)


class TSNEAnalyzer(BaseAnalyzer):
    """
    t-SNE降维分析器，用于降维和可视化任务
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
    
    def load_params(self, model_name: str) -> Dict[str, Any]:
        """加载和处理模型参数"""
        default_params = {
            "n_components": 2,
            "perplexity": 30,
            "learning_rate": "auto",
            "n_iter": 1000,
            "random_state": 42
        }
        return default_params
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, bool]:
        """验证模型参数的合法性"""
        # t-SNE参数验证
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
        """训练t-SNE模型"""
        try:
            # 获取模型参数
            if self._model_instance is not None:
                model_params = self._model_instance.get_params()
            else:
                model_params = {}
            
            # 创建模型实例
            self.model = TSNE(**model_params)
            
            logger.info("t-SNE降维模型训练成功")
            return self.model
        except Exception as e:
            logger.error(f"t-SNE降维模型训练失败: {e}")
            raise RuntimeError(f"t-SNE降维模型训练失败: {str(e)}") from e
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """训练后处理"""
        result = {}
        
        # t-SNE是不可预测的模型，主要用于可视化，不提供额外的后处理结果
        return result
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """获取特征重要性（t-SNE没有特征重要性概念）"""
        # t-SNE没有特征重要性概念
        return {}
    
    def predict(self, model: Any, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """使用t-SNE模型进行降维转换"""
        if model is None:
            raise ValueError("模型未训练，请先训练模型")
        
        try:
            # 执行降维转换
            # 注意：t-SNE没有独立的预测方法，需要重新拟合
            # 这里我们创建一个新的t-SNE实例来进行转换
            if self._model_instance is not None:
                model_params = self._model_instance.get_params()
            else:
                model_params = {}
            
            new_tsne = TSNE(**model_params)
            transformed_data = new_tsne.fit_transform(X)
            
            # 创建有意义的列名
            n_components = transformed_data.shape[1]
            columns = [f'tSNE{i+1}' for i in range(n_components)]
            
            # 转换为DataFrame并保持索引
            transformed_df = pd.DataFrame(transformed_data, columns=columns, index=X.index)
            
            return transformed_df
        except Exception as e:
            logger.error(f"t-SNE降维转换失败: {e}")
            raise RuntimeError(f"t-SNE降维转换失败: {str(e)}") from e
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """保存模型产物"""
        try:
            # 确保保存目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存模型
            joblib.dump(model, filepath)
            
            logger.info(f"t-SNE降维模型已成功保存到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存t-SNE降维模型失败: {e}")
            return False
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """获取默认评估指标"""
        # t-SNE主要用于可视化，通常不进行量化评估
        return ["trustworthiness"]
    
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