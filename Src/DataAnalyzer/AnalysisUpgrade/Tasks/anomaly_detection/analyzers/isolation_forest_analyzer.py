"""
Isolation Forest 异常检测分析器
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import numpy as np


class IsolationForestAnalyzer(BaseAnalyzer):
    """
    Isolation Forest 异常检测分析器
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.config = None
        self._load_config()
    
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
    
    def load_params(self, config_path: str) -> Dict[str, Any]:
        """
        从配置文件中加载任务参数
        
        参数:
            config_path (str): 配置文件路径
            
        返回:
            Dict[str, Any]: 包含模型名称、超参数等的字典
        """
        return self.load_config(config_path)
    
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
                
                # 检查preprocessing_special_params中的异常检测相关参数
                if 'preprocessing_special_params' in self.config:
                    for param_name, param_info in self.config['preprocessing_special_params'].items():
                        if isinstance(param_info, dict) and param_name not in metadata_keys:
                            supported_params.add(param_name)
                
                # 检查ML_model_special_params中的Isolation Forest相关参数
                if 'ML_model_special_params' in self.config:
                    for model_type, params_dict in self.config['ML_model_special_params'].items():
                        if isinstance(params_dict, dict) and ('isolation_forest' in model_type.lower() or 'anomaly_detection' in model_type.lower()):
                            for param_name, param_info in params_dict.items():
                                if isinstance(param_info, dict) and param_name not in metadata_keys:
                                    supported_params.add(param_name)
                
                # 校验传入的参数是否都在支持的参数列表中
                if supported_params:
                    for param in params:
                        if param not in supported_params:
                            print(f"警告: 参数 {param} 不在配置文件定义的支持参数列表中")
            
            # 降级方案：硬编码的有效参数列表
            valid_params = {
                'n_estimators': int,
                'max_samples': (int, float, str),
                'contamination': float,
                'max_features': (int, float),
                'bootstrap': bool,
                'n_jobs': (int, type(None)),
                'random_state': (int, type(None)),
                'verbose': int,
                'warm_start': bool
            }
            
            # 参数类型和值范围校验
            for param, value in params.items():
                if param in valid_params:
                    # 检查类型
                    if not isinstance(value, valid_params[param]):
                        print(f"参数 {param} 类型错误: 期望 {valid_params[param]}, 得到 {type(value)}")
                        return False
                    
                    # 检查值范围
                    if param == 'contamination' and not (0 <= value <= 1):
                        print(f"参数 {param} 值错误: 必须在 0-1 范围内")
                        return False
                    elif param == 'max_features' and isinstance(value, (int, float)) and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0")
                        return False
            
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
        # 异常检测通常不需要目标变量
        return X, y
    
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """
        训练Isolation Forest模型
        
        参数:
            X_train (pd.DataFrame): 训练特征数据
            y_train (Optional[pd.Series]): 训练目标数据（通常不使用）
            
        返回:
            Any: 训练完成的模型对象
        """
        try:
            # 创建并训练Isolation Forest模型
            self.model = IsolationForest(random_state=42, contamination=0.1)
            self.model.fit(X_train)
            return self.model
        except Exception as e:
            raise Exception(f"Isolation Forest训练失败: {str(e)}")
    
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
        try:
            # 获取异常分数
            anomaly_scores = model.decision_function(X)
            # 获取预测标签（-1表示异常，1表示正常）
            predictions = model.predict(X)
            
            return {
                "anomaly_scores": anomaly_scores.tolist(),
                "predictions": predictions.tolist(),
                "anomaly_count": int((predictions == -1).sum()),
                "normal_count": int((predictions == 1).sum())
            }
        except Exception as e:
            raise Exception(f"后处理失败: {str(e)}")
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        获取特征重要性（Isolation Forest没有直接的特征重要性）
        
        参数:
            model (Any): 模型对象
            
        返回:
            Dict[str, float]: 特征重要性字典
        """
        return {}
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """
        保存模型
        
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
            print(f"保存Isolation Forest模型失败: {e}")
            return False
    
    def predict(self, model: Any, X: pd.DataFrame) -> pd.Series:
        """
        使用模型预测异常
        
        参数:
            model (Any): 模型对象
            X (pd.DataFrame): 输入数据
            
        返回:
            pd.Series: 预测结果（-1表示异常，1表示正常）
        """
        try:
            predictions = model.predict(X)
            return pd.Series(predictions, name='anomaly_predictions')
        except Exception as e:
            raise Exception(f"预测失败: {str(e)}")
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """
        获取默认评估指标列表
        
        参数:
            model_type (str): 模型类型
            
        返回:
            List[str]: 默认评估指标列表
        """
        # 异常检测使用的评估指标
        return ['precision', 'recall', 'f1_score', 'roc_auc']
    
    def analyzer(
        self, 
        df: pd.DataFrame, 
        learn_type: str, 
        model_type: str, 
        model: str,
        random_state: int = 42, 
        is_split: bool = False,  # 异常检测通常不分训练测试集
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
        执行完整异常检测流程的核心方法
        
        参数:
            df (pd.DataFrame): 输入数据集，不能为空
            learn_type (str): 学习类型，如 "ML"（机器学习）或 "DL"（深度学习）
            model_type (str): 模型类别，如 "classification"、"regression"、"clustering"
            model (str): 模型名称，如 "isolation_forest"、"local_outlier_factor"
            random_state (int): 随机种子，用于复现实验结果，默认为42
            is_split (bool): 是否自动划分训练/测试集，默认为False
            split_ratio (float): 测试集占比，范围 (0,1)，仅当 is_split=True 时生效，默认为0.2
            feature_cols (List[str]): 特征列名列表，不能为空
            target_col (str): 目标列名，可选
            metrics_list (List[str]): 评价指标列表，如 ["precision", "recall"]，默认使用默认指标
            is_return_model_score (bool): 是否返回模型评估得分，默认为True
            feature_cols_encoding (str): 特征列编码方式，支持 "onehot"、"label"、"ordinal"、"target"、"none"、"auto" 等，默认为"auto"
            target_col_encoding (str): 目标列编码方式，分类任务常用 "label"，回归为 "none"，默认为"auto"
            test_set (pd.DataFrame): 外部传入的测试集，仅当 is_split=False 时使用，默认为None
            model_params (Dict[str, Any]): 模型特定超参数，默认为{}
            
        返回:
            Dict[str, Any]: 包含模型、评估结果等信息的字典
        """
        try:
            # 准备数据
            if feature_cols:
                X = df[feature_cols].copy()
            else:
                X = df.copy()
                # 如果没有指定特征列且存在目标列，则移除目标列
                if target_col and target_col in X.columns:
                    X = X.drop(columns=[target_col])
            
            # 确保X是DataFrame类型
            if not isinstance(X, pd.DataFrame):
                X = pd.DataFrame(X)
            
            # 处理模型参数
            if model_params is None:
                model_params = {}
            
            # 校验参数
            self.validate_params(model_params)
            
            # 合并默认参数和用户参数
            params = {'random_state': random_state}
            params.update(model_params)
            
            # 训练模型
            self.model = IsolationForest(**params)
            self.model.fit(X)
            
            # 获取异常检测结果
            predictions = self.model.predict(X)
            anomaly_scores = self.model.decision_function(X)
            
            # 构建结果字典
            result = {
                "model": self.model,
                "predictions": predictions.tolist(),
                "anomaly_scores": anomaly_scores.tolist(),
                "anomaly_count": int((predictions == -1).sum()),
                "normal_count": int((predictions == 1).sum()),
                "message": "Isolation Forest异常检测完成"
            }
            
            # 如果有目标列，可以计算评估指标
            if target_col and target_col in df.columns:
                # 假设目标列中1表示异常，0表示正常，需要转换为-1和1
                y_true = df[target_col].replace(0, 1).replace(1, -1)  # 转换为与模型输出一致的格式
                
                # 计算评估指标
                from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
                
                # 计算ROC AUC需要使用异常分数而不是预测标签
                auc_score = roc_auc_score(y_true, -anomaly_scores)  # 注意取负号
                
                # 计算其他指标
                precision = precision_score(y_true, predictions, average='binary')
                recall = recall_score(y_true, predictions, average='binary')
                f1 = f1_score(y_true, predictions, average='binary')
                
                result["metrics"] = {
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "roc_auc": auc_score
                }
            
            return result
        except Exception as e:
            return {
                "error": str(e)
            }

