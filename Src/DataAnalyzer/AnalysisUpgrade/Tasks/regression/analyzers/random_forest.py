"""
随机森林回归器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List, Tuple, Union
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import logging

logger = logging.getLogger(__name__)


class RandomForestRegressorAnalyzer(BaseAnalyzer):
    """
    随机森林回归分析器，用于回归任务
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
    
    def load_params(self, model_name: str) -> Dict[str, Any]:
        """加载和处理模型参数"""
        default_params = {
            "n_estimators": 100,
            "max_depth": None,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "random_state": 42
        }
        return default_params
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, bool]:
        """验证模型参数的合法性"""
        # RandomForestRegressor参数验证
        return {"valid": True}
    
    def replace_params(self, default_params: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """替换默认参数"""
        updated_params = default_params.copy()
        updated_params.update(params)
        return updated_params
    
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """数据预处理"""
        processed_X = X.copy()
        processed_y = y.copy() if y is not None else None
        
        # 处理缺失值
        if processed_X.isnull().sum().sum() > 0:
            numeric_cols = processed_X.select_dtypes(include=[np.number]).columns
            processed_X[numeric_cols] = processed_X[numeric_cols].fillna(processed_X[numeric_cols].mean())
        
        # 如果y存在，处理缺失值
        if processed_y is not None and processed_y.isnull().sum() > 0:
            processed_y = processed_y.fillna(processed_y.mean())
        
        return processed_X, processed_y
    
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """训练随机森林回归模型"""
        try:
            # 获取模型参数
            if self._model_instance is not None:
                model_params = self._model_instance.get_params()
            else:
                model_params = {}
            
            # 创建模型实例
            self.model = RandomForestRegressor(**model_params)
            
            # 拟合模型
            self.model.fit(X_train, y_train)
            
            logger.info("随机森林回归模型训练成功")
            return self.model
        except Exception as e:
            logger.error(f"随机森林回归模型训练失败: {e}")
            raise RuntimeError(f"随机森林回归模型训练失败: {str(e)}") from e
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """训练后处理"""
        result = {}
        
        # 获取特征重要性
        if hasattr(model, 'feature_importances_'):
            feature_names = X.columns.tolist()
            importance_dict = dict(zip(feature_names, model.feature_importances_))
            result['feature_importance'] = importance_dict
        
        return result
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """获取特征重要性"""
        if hasattr(model, 'feature_importances_'):
            return {f"feature_{i}": importance for i, importance in enumerate(model.feature_importances_)}
        return {}
    
    def predict(self, model: Any, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """使用随机森林回归模型进行预测"""
        if model is None:
            raise ValueError("模型未训练，请先训练模型")
        
        try:
            # 执行预测
            predictions = model.predict(X)
            
            # 转换为Series并保持索引
            prediction_series = pd.Series(predictions, index=X.index)
            
            return prediction_series
        except Exception as e:
            logger.error(f"随机森林回归预测失败: {e}")
            raise RuntimeError(f"随机森林回归预测失败: {str(e)}") from e
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """保存模型产物"""
        try:
            # 确保保存目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存模型
            joblib.dump(model, filepath)
            
            logger.info(f"随机森林回归模型已成功保存到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存随机森林回归模型失败: {e}")
            return False
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """获取默认评估指标"""
        return ["mse", "rmse", "mae", "r2_score"]
    
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