"""
编码器分析器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List, Tuple, Union
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import joblib
import logging

logger = logging.getLogger(__name__)


class EncoderAnalyzer(BaseAnalyzer):
    """
    编码器分析器，用于对分类特征进行编码处理
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.encoding_type = "onehot"  # 默认编码方式
    
    def load_params(self, model_name: str) -> Dict[str, Any]:
        """加载和处理模型参数"""
        # 对于encoder，我们不需要从配置文件加载参数，直接返回空字典
        return {}
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, bool]:
        """验证模型参数的合法性"""
        # Encoder不需要特殊参数验证
        return {"valid": True}
    
    def replace_params(self, default_params: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """替换默认参数"""
        # Encoder不需要参数替换
        return default_params
    
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """数据预处理"""
        processed_X = X.copy()
        
        # 处理缺失值
        # 使用sum().sum()代替any().any()避免类型检查错误
        if processed_X.isnull().sum().sum() > 0:
            categorical_cols = processed_X.select_dtypes(include=['object', 'category']).columns
            for col in categorical_cols:
                processed_X[col] = processed_X[col].fillna('Missing')
            
            numeric_cols = processed_X.select_dtypes(include=[np.number]).columns
            processed_X[numeric_cols] = processed_X[numeric_cols].fillna(processed_X[numeric_cols].mean())
        
        return processed_X, y
    
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """训练编码器模型"""
        try:
            # 确定要编码的列
            categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not categorical_cols:
                logger.info("没有分类列需要编码")
                self.model = None
                return None
            
            # 根据编码类型创建模型
            if self.encoding_type == "onehot":
                self.model = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                self.model.fit(X_train[categorical_cols])
            elif self.encoding_type == "label":
                self.model = {}
                for col in categorical_cols:
                    le = LabelEncoder()
                    self.model[col] = le.fit(X_train[col])
            else:
                raise ValueError(f"不支持的编码类型: {self.encoding_type}")
            
            logger.info(f"编码器模型训练成功，编码类型: {self.encoding_type}")
            return self.model
        except Exception as e:
            logger.error(f"编码器模型训练失败: {e}")
            raise RuntimeError(f"编码器模型训练失败: {str(e)}") from e
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """训练后处理"""
        result = {}
        
        # 可以添加编码映射信息
        if self.encoding_type == "onehot" and hasattr(model, 'get_feature_names_out'):
            try:
                categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
                feature_names = model.get_feature_names_out(categorical_cols)
                result['encoded_feature_names'] = feature_names.tolist()
            except Exception as e:
                logger.warning(f"获取编码后特征名失败: {e}")
        elif self.encoding_type == "label" and isinstance(model, dict):
            result['label_encoders'] = list(model.keys())
        
        return result
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """获取特征重要性（编码器没有特征重要性概念）"""
        # 编码器不涉及特征选择，所有特征权重相同
        return {}
    
    def predict(self, model: Any, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """使用编码器模型进行转换"""
        if model is None:
            # 没有需要编码的列，直接返回原数据
            return X.copy()
        
        try:
            X_copy = X.copy()
            categorical_cols = X_copy.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not categorical_cols:
                return X_copy
            
            if self.encoding_type == "onehot":
                # 执行one-hot编码
                encoded_data = model.transform(X_copy[categorical_cols])
                feature_names = model.get_feature_names_out(categorical_cols)
                
                # 创建编码后的DataFrame
                encoded_df = pd.DataFrame(encoded_data, columns=feature_names, index=X_copy.index)
                
                # 合并编码后的特征和原始数值特征
                numeric_cols = X_copy.select_dtypes(exclude=['object', 'category']).columns
                if len(numeric_cols) > 0:
                    result_df = pd.concat([X_copy[numeric_cols], encoded_df], axis=1)
                else:
                    result_df = encoded_df
                    
            elif self.encoding_type == "label" and isinstance(model, dict):
                # 执行标签编码
                X_copy_encoded = X_copy.copy()
                for col in categorical_cols:
                    if col in model:
                        try:
                            X_copy_encoded[col] = model[col].transform(X_copy[col])
                        except ValueError as e:
                            # 处理未见过的标签
                            logger.warning(f"处理列 {col} 时遇到未见过的标签: {e}")
                            # 使用最常见的标签替代
                            most_frequent = model[col].classes_[0]
                            X_copy_encoded[col] = X_copy[col].apply(
                                lambda x: most_frequent if x not in model[col].classes_ else x
                            )
                            X_copy_encoded[col] = model[col].transform(X_copy_encoded[col])
                
                result_df = X_copy_encoded
            else:
                raise ValueError(f"不支持的编码类型或模型格式: {self.encoding_type}")
            
            return result_df
        except Exception as e:
            logger.error(f"编码器转换失败: {e}")
            raise RuntimeError(f"编码器转换失败: {str(e)}") from e
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """保存模型产物"""
        try:
            # 确保保存目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存模型
            joblib.dump(model, filepath)
            
            logger.info(f"编码器模型已成功保存到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存编码器模型失败: {e}")
            return False
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """获取默认评估指标"""
        # 编码器本身不需要评估指标
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
            "encoding_type": self.encoding_type
        }
        
        # 添加后处理结果
        result.update(postprocess_result)
        
        return result