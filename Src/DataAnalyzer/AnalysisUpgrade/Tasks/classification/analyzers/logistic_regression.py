"""
逻辑回归分析器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List, Tuple, Union
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import logging

logger = logging.getLogger(__name__)


class LogisticRegressionAnalyzer(BaseAnalyzer):
    """
    逻辑回归分析器，用于分类任务
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
    
    def load_params(self, model_name: str) -> Dict[str, Any]:
        """加载和处理模型参数"""
        default_params = {
            "C": 1.0,
            "penalty": "l2",
            "solver": "lbfgs",
            "max_iter": 1000,
            "random_state": 42
        }
        return default_params
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, bool]:
        """验证模型参数的合法性"""
        # LogisticRegression参数验证
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
        
        # 如果y存在，确保它是数值型的
        if processed_y is not None and processed_y.dtype == 'object':
            le = LabelEncoder()
            processed_y = pd.Series(le.fit_transform(processed_y), name=processed_y.name, index=processed_y.index)
            self._fitted_encoders["target"] = le
        
        return processed_X, processed_y
    
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """训练逻辑回归模型"""
        try:
            # 获取模型参数
            if self._model_instance is not None:
                model_params = self._model_instance.get_params()
            else:
                model_params = {}
            
            # 创建模型实例
            self.model = LogisticRegression(**model_params)
            
            # 拟合模型
            self.model.fit(X_train, y_train)
            
            logger.info("逻辑回归模型训练成功")
            return self.model
        except Exception as e:
            logger.error(f"逻辑回归模型训练失败: {e}")
            raise RuntimeError(f"逻辑回归模型训练失败: {str(e)}") from e
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """训练后处理"""
        result = {}
        
        # 获取特征重要性（系数）
        if hasattr(model, 'coef_'):
            feature_names = X.columns.tolist()
            if len(model.coef_.shape) == 1:
                # 二分类情况
                coef_dict = dict(zip(feature_names, model.coef_))
            else:
                # 多分类情况，取平均值
                coef_dict = dict(zip(feature_names, np.mean(np.abs(model.coef_), axis=0)))
            result['feature_importance'] = coef_dict
        
        return result
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """获取特征重要性"""
        if hasattr(model, 'coef_'):
            # 注意：逻辑回归的系数可能为负，这里取绝对值表示重要性
            return {f"feature_{i}": abs(coef) for i, coef in enumerate(model.coef_.flatten())}
        return {}
    
    def predict(self, model: Any, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """使用逻辑回归模型进行预测"""
        if model is None:
            raise ValueError("模型未训练，请先训练模型")
        
        try:
            # 执行预测
            predictions = model.predict(X)
            
            # 转换为Series并保持索引
            prediction_series = pd.Series(predictions, index=X.index)
            
            return prediction_series
        except Exception as e:
            logger.error(f"逻辑回归预测失败: {e}")
            raise RuntimeError(f"逻辑回归预测失败: {str(e)}") from e
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """保存模型产物"""
        try:
            # 确保保存目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存模型
            joblib.dump(model, filepath)
            
            logger.info(f"逻辑回归模型已成功保存到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存逻辑回归模型失败: {e}")
            return False
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """获取默认评估指标"""
        return ["accuracy", "precision", "recall", "f1_score"]
    
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