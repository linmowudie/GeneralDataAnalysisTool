"""
OneHotEncoder
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List
import pandas as pd
from sklearn.preprocessing import OneHotEncoder as SklearnOneHotEncoder
import joblib
import numpy as np


class OneHotEncoderAnalyzer(BaseAnalyzer):
    """
    OneHot编码分析器
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.feature_names = None
        self.config = None
        self._load_config()
    
    def load_params(self, config_path: str) -> Dict[str, Any]:
        """
        从配置文件中加载任务参数
        
        参数:
            config_path (str): 配置文件路径
            
        返回:
            Dict[str, Any]: 包含模型名称、超参数等的字典
        """
        return self.load_config(config_path)
    
    def _load_config(self):
        """
        从配置文件加载参数配置
        """
        try:
            # 构建配置文件路径
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Configs')
            config_path = os.path.join(config_dir, 'model_analysis.json')
            
            # 读取配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            self.config = None
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        参数校验方法
        
        参数:
            params (Dict[str, Any]): 待校验的参数字典
            
        返回:
            bool: 校验是否通过
        """
        try:
            # 尝试从配置文件获取支持的参数列表
            if self.config and ('preprocessing_special_params' in self.config or 'ML_model_special_params' in self.config):
                # 元数据键，不视为参数
                metadata_keys = ['type', 'description', 'required', 'default']
                
                # 从配置中提取支持的参数列表
                supported_params = set()
                
                # 检查preprocessing_special_params中的encoder相关参数
                if 'preprocessing_special_params' in self.config:
                    for param_name, param_info in self.config['preprocessing_special_params'].items():
                        if isinstance(param_info, dict) and param_name not in metadata_keys:
                            supported_params.add(param_name)
                
                # 检查ML_model_special_params中的encoder相关参数
                if 'ML_model_special_params' in self.config:
                    for model_type, params_dict in self.config['ML_model_special_params'].items():
                        if isinstance(params_dict, dict) and 'encoder' in model_type.lower():
                            for param_name, param_info in params_dict.items():
                                if isinstance(param_info, dict) and param_name not in metadata_keys:
                                    supported_params.add(param_name)
                
                # 校验传入的参数是否都在支持的参数列表中
                if supported_params:
                    for param in params:
                        if param not in supported_params:
                            print(f"警告: 参数 {param} 不在配置文件定义的支持参数列表中")
            
            # OneHot编码本身不需要严格的参数校验
            return True
        except Exception:
            # 如果配置加载或参数校验失败，默认返回True以保持兼容性
            return True
    
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> tuple:
        """
        数据预处理方法
        
        参数:
            X (pd.DataFrame): 特征数据
            y (Optional[pd.Series]): 目标数据
            
        返回:
            tuple: 预处理后的(X, y)数据
        """
        # 编码器不需要特殊预处理
        return X, y
    
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """
        训练OneHot编码器
        
        参数:
            X_train (pd.DataFrame): 训练特征数据
            y_train (Optional[pd.Series]): 训练目标数据
            
        返回:
            Any: 训练完成的模型对象
        """
        try:
            self.model = SklearnOneHotEncoder(sparse_output=False, handle_unknown='ignore')
            self.model.fit(X_train)
            
            # 保存特征名
            self.feature_names = self.model.get_feature_names_out(X_train.columns)
            
            return self.model
        except Exception as e:
            raise Exception(f"OneHot编码器训练失败: {str(e)}")
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """
        训练后处理方法
        
        参数:
            model (Any): 训练完成的模型
            X (pd.DataFrame): 特征数据
            y (Optional[pd.Series]): 目标数据
            
        返回:
            Dict[str, Any]: 包含后处理结果的字典
        """
        return {"message": "编码器无需后处理"}
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        获取特征重要性（编码器无特征重要性概念）
        
        参数:
            model (Any): 模型对象
            
        返回:
            Dict[str, float]: 特征重要性字典
        """
        return {}
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """
        保存编码器模型
        
        参数:
            model (Any): 要保存的模型对象
            filepath (str): 保存路径
            
        返回:
            bool: 是否保存成功
        """
        try:
            joblib.dump(model, filepath)
            return True
        except Exception as e:
            print(f"保存OneHot编码器模型失败: {e}")
            return False
    
    def predict(self, model: Any, X: pd.DataFrame) -> pd.Series:
        """
        使用编码器转换数据
        
        参数:
            model (Any): 编码器模型
            X (pd.DataFrame): 输入数据
            
        返回:
            pd.Series: 编码后的数据
        """
        try:
            X_encoded = model.transform(X)
            # 返回编码后的数组作为Series
            return pd.Series(X_encoded.flatten())
        except Exception as e:
            raise Exception(f"OneHot编码预测失败: {str(e)}")
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """
        获取默认评估指标列表
        
        参数:
            model_type (str): 模型类型
            
        返回:
            List[str]: 默认评估指标列表
        """
        return []
    
    def analyzer(
        self, 
        df: pd.DataFrame, 
        learn_type: str, 
        model_type: str, 
        model: str,
        random_state: int = 42, 
        is_split: bool = True, 
        split_ratio: float = 0.2,
        feature_cols: Optional[List[str]] = None, 
        target_col: Optional[str] = None,
        metrics_list: Optional[List[str]] = None, 
        is_return_model_score: bool = True,
        feature_cols_encoding: str = "auto", 
        target_col_encoding: str = "auto",
        test_set: Optional[pd.DataFrame] = None, 
        model_params: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
        """
        执行完整分析流程的核心方法
        
        参数:
            df (pd.DataFrame): 输入数据集，不能为空
            learn_type (str): 学习类型，如 "ML"（机器学习）或 "DL"（深度学习）
            model_type (str): 模型类别，如 "classification"、"regression"、"clustering"
            model (str): 模型名称，如 "random_forest"、"xgboost"
            random_state (int): 随机种子，用于复现实验结果，默认为42
            is_split (bool): 是否自动划分训练/测试集，默认为True
            split_ratio (float): 测试集占比，范围 (0,1)，仅当 is_split=True 时生效，默认为0.2
            feature_cols (List[str]): 特征列名列表，不能为空
            target_col (str): 目标列名，不能为空
            metrics_list (List[str]): 评价指标列表，如 ["accuracy", "f1"]，默认使用默认指标
            is_return_model_score (bool): 是否返回模型评估得分，默认为True
            feature_cols_encoding (str): 特征列编码方式，支持 "onehot"、"label"、"ordinal"、"target"、"none"、"auto" 等，默认为"auto"
            target_col_encoding (str): 目标列编码方式，分类任务常用 "label"，回归为 "none"，默认为"auto"
            test_set (pd.DataFrame): 外部传入的测试集，仅当 is_split=False 时使用，默认为None
            model_params (Dict[str, Any]): 模型特定超参数，如 {"n_estimators": 100, "max_depth": 10}，默认为{}
            
        返回:
            Dict[str, Any]: 包含模型、评估结果等信息的字典
        """
        # 对于编码器，我们简化处理流程
        try:
            # 准备数据
            if feature_cols:
                X = df[feature_cols]
            else:
                X = df
            
            # 确保X是DataFrame类型
            if not isinstance(X, pd.DataFrame):
                X = pd.DataFrame(X)
            
            # 训练编码器
            trained_model = self.train(X, None)
            
            # 编码数据
            encoded_data = self.predict(trained_model, X)
            
            return {
                "model": trained_model,
                "encoded_data": encoded_data,
                "feature_names": self.feature_names.tolist() if self.feature_names is not None else [],
                "message": "编码器训练和应用成功"
            }
        except Exception as e:
            return {
                "error": str(e)
            }