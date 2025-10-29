"""
StandardScaler分析器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List, Tuple, Union
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import logging

logger = logging.getLogger(__name__)


class ScalerAnalyzer(BaseAnalyzer):
    """
    标准化分析器，用于对特征进行标准化处理
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
    
    def load_params(self, model_name: str) -> Dict[str, Any]:
        """加载和处理模型参数"""
        # 对于scaler，我们不需要从配置文件加载参数，直接返回空字典
        return {}
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, bool]:
        """验证模型参数的合法性"""
        # Scaler不需要特殊参数验证
        return {"valid": True}
    
    def replace_params(self, default_params: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """替换默认参数"""
        # Scaler不需要参数替换
        return default_params
    
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """数据预处理"""
        processed_X = X.copy()
        
        # 处理缺失值
        # 使用sum().sum()代替any().any()避免类型检查错误
        if processed_X.isnull().sum().sum() > 0:  # 检查是否有任何缺失值
            numeric_cols = processed_X.select_dtypes(include=[np.number]).columns
            processed_X[numeric_cols] = processed_X[numeric_cols].fillna(processed_X[numeric_cols].mean())
        
        return processed_X, y
    
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """训练标准化模型"""
        try:
            # 创建模型实例
            self.model = StandardScaler()
            
            # 拟合模型
            self.model.fit(X_train)
            
            logger.info("StandardScaler模型训练成功")
            return self.model
        except Exception as e:
            logger.error(f"StandardScaler模型训练失败: {e}")
            raise RuntimeError(f"StandardScaler模型训练失败: {str(e)}") from e
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """训练后处理"""
        result = {}
        
        # 可以添加一些统计信息
        if hasattr(model, 'mean_'):
            result['scaler_mean'] = model.mean_.tolist()
        
        if hasattr(model, 'scale_'):
            result['scaler_scale'] = model.scale_.tolist()
        
        return result
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """获取特征重要性（标准化没有特征重要性概念）"""
        # 标准化不涉及特征选择，所有特征权重相同
        return {}
    
    def predict(self, model: Any, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """使用标准化模型进行转换"""
        if model is None:
            raise ValueError("模型未训练，请先训练模型")
        
        try:
            # 执行转换
            scaled_data = model.transform(X)
            
            # 转换为DataFrame并保持列名
            scaled_df = pd.DataFrame(scaled_data, columns=X.columns, index=X.index)
            
            # 根据需要返回DataFrame
            return scaled_df
        except Exception as e:
            logger.error(f"StandardScaler转换失败: {e}")
            raise RuntimeError(f"StandardScaler转换失败: {str(e)}") from e
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """保存模型产物"""
        try:
            # 确保保存目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存模型
            joblib.dump(model, filepath)
            
            logger.info(f"StandardScaler模型已成功保存到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存StandardScaler模型失败: {e}")
            return False
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """获取默认评估指标"""
        # 标准化本身不需要评估指标
        return []
    
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