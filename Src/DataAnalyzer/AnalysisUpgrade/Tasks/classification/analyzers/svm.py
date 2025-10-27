"""
SVMClassifier
这里将实现支持向量机分类器的具体分析逻辑
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List
import pandas as pd
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np


class SVMAnalyzer(BaseAnalyzer):
    """
    支持向量机分类器分析器
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.scaler = None
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
                
                # 检查preprocessing_special_params中的分类相关参数
                if 'preprocessing_special_params' in self.config:
                    for param_name, param_info in self.config['preprocessing_special_params'].items():
                        if isinstance(param_info, dict) and param_name not in metadata_keys:
                            supported_params.add(param_name)
                
                # 检查ML_model_special_params中的SVM相关参数
                if 'ML_model_special_params' in self.config:
                    for model_type, params_dict in self.config['ML_model_special_params'].items():
                        if isinstance(params_dict, dict) and ('svm' in model_type.lower() or 'classification' in model_type.lower()):
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
                'C': (float, int),
                'kernel': str,
                'degree': int,
                'gamma': (float, str),
                'coef0': float,
                'shrinking': bool,
                'probability': bool,
                'tol': float,
                'cache_size': float,
                'class_weight': (dict, list, str, type(None)),
                'verbose': bool,
                'max_iter': int,
                'decision_function_shape': str,
                'break_ties': bool,
                'random_state': (int, type(None))
            }
            
            # 支持的核函数类型
            valid_kernels = ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed']
            
            # 支持的决策函数形状
            valid_decision_shapes = ['ovr', 'ovo']
            
            # 参数类型和值范围校验
            for param, value in params.items():
                if param in valid_params:
                    # 检查类型
                    if not isinstance(value, valid_params[param]):
                        print(f"参数 {param} 类型错误: 期望 {valid_params[param]}, 得到 {type(value)}")
                        return False
                    
                    # 检查值范围
                    if param == 'C' and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0")
                        return False
                    elif param == 'degree' and value < 1:
                        print(f"参数 {param} 值错误: 必须大于等于 1")
                        return False
                    elif param == 'tol' and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0")
                        return False
                    elif param == 'cache_size' and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0")
                        return False
                    elif param == 'max_iter' and value < -1:
                        print(f"参数 {param} 值错误: 必须大于等于 -1")
                        return False
                    elif param == 'kernel' and value not in valid_kernels:
                        print(f"参数 {param} 值错误: 必须是 {valid_kernels} 之一")
                        return False
                    elif param == 'decision_function_shape' and value not in valid_decision_shapes:
                        print(f"参数 {param} 值错误: 必须是 {valid_decision_shapes} 之一")
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
        # 基本预处理，确保数据类型正确
        if X.isnull().any().any():
            X = X.fillna(X.mean())
        
        # SVM对特征缩放敏感，添加标准化步骤
        if self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        # 转换回DataFrame以保持特征名称
        X_scaled_df = pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
        
        return X_scaled_df, y
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """
        训练SVM分类器
        
        参数:
            X_train (pd.DataFrame): 训练特征数据
            y_train (pd.Series): 训练目标数据
            
        返回:
            Any: 训练完成的模型对象
        """
        try:
            # 创建并训练SVM模型
            self.model = SVC(kernel='rbf', C=1.0, random_state=42, probability=True)
            self.model.fit(X_train, y_train)
            return self.model
        except Exception as e:
            raise Exception(f"SVM训练失败: {str(e)}")
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Dict[str, Any]:
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
            # 获取预测结果
            predictions = model.predict(X)
            
            result = {
                "predictions": predictions.tolist()
            }
            
            # 获取预测概率（如果支持）
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(X)
                result["probabilities"] = probabilities.tolist()
            
            # 如果有目标数据，可以计算评估指标
            if y is not None:
                result.update({
                    "accuracy": accuracy_score(y, predictions),
                    "precision": precision_score(y, predictions, average='macro'),
                    "recall": recall_score(y, predictions, average='macro'),
                    "f1_score": f1_score(y, predictions, average='macro')
                })
            
            return result
        except Exception as e:
            raise Exception(f"后处理失败: {str(e)}")
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        获取特征重要性
        
        参数:
            model (Any): 模型对象
            
        返回:
            Dict[str, float]: 特征重要性字典
        """
        try:
            # 对于线性核，可以使用系数作为重要性
            if hasattr(model, 'coef_'):
                # 如果是多分类问题，coef_的shape是(n_classes, n_features)
                if len(model.coef_.shape) > 1:
                    # 计算每个特征的平均绝对系数
                    importances = np.abs(model.coef_).mean(axis=0)
                else:
                    importances = np.abs(model.coef_)
                
                return {f"feature_{i}": float(importance) for i, importance in enumerate(importances)}
            return {}
        except Exception:
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
            # 保存模型和缩放器
            artifacts = {
                'model': model,
                'scaler': self.scaler
            }
            joblib.dump(artifacts, filepath)
            return True
        except Exception as e:
            print(f"保存SVM模型失败: {e}")
            return False
    
    def predict(self, model: Any, X: pd.DataFrame) -> pd.Series:
        """
        使用模型进行预测
        
        参数:
            model (Any): 模型对象
            X (pd.DataFrame): 输入数据
            
        返回:
            pd.Series: 预测结果
        """
        try:
            # 确保使用相同的缩放器
            if self.scaler is not None:
                X_scaled = self.scaler.transform(X)
                X_scaled_df = pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
                predictions = model.predict(X_scaled_df)
            else:
                predictions = model.predict(X)
            
            return pd.Series(predictions, name='predictions')
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
        return ['accuracy', 'precision', 'recall', 'f1_score']
    
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
        执行完整分类流程的核心方法
        
        参数:
            df (pd.DataFrame): 输入数据集，不能为空
            learn_type (str): 学习类型，如 "ML"（机器学习）或 "DL"（深度学习）
            model_type (str): 模型类别，如 "classification"、"regression"、"clustering"
            model (str): 模型名称，如 "svm"、"decision_tree"
            random_state (int): 随机种子，用于复现实验结果，默认为42
            is_split (bool): 是否自动划分训练/测试集，默认为True
            split_ratio (float): 测试集占比，范围 (0,1)，仅当 is_split=True 时生效，默认为0.2
            feature_cols (List[str]): 特征列名列表，不能为空
            target_col (str): 目标列名，不能为空
            metrics_list (List[str]): 评价指标列表，如 ["accuracy", "precision"]，默认使用默认指标
            is_return_model_score (bool): 是否返回模型评估得分，默认为True
            feature_cols_encoding (str): 特征列编码方式，支持 "onehot"、"label"、"ordinal"、"target"、"none"、"auto" 等，默认为"auto"
            target_col_encoding (str): 目标列编码方式，分类任务常用 "label"，回归为 "none"，默认为"auto"
            test_set (pd.DataFrame): 外部传入的测试集，仅当 is_split=False 时使用，默认为None
            model_params (Dict[str, Any]): 模型特定超参数，默认为{}
            
        返回:
            Dict[str, Any]: 包含模型、评估结果等信息的字典
        """
        try:
            # 检查必要参数
            if target_col is None or target_col not in df.columns:
                raise ValueError("必须指定有效的目标列")
            
            # 准备数据
            if feature_cols:
                X = df[feature_cols].copy()
            else:
                X = df.drop(columns=[target_col]).copy()
            y = df[target_col].copy()
            
            # 确保X是DataFrame类型
            if not isinstance(X, pd.DataFrame):
                X = pd.DataFrame(X)
            
            # 处理模型参数
            if model_params is None:
                model_params = {}
            
            # 校验参数
            self.validate_params(model_params)
            
            # 合并默认参数和用户参数
            params = {'random_state': random_state, 'probability': True}
            params.update(model_params)
            
            # 训练测试集划分
            if is_split:
                from sklearn.model_selection import train_test_split
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=split_ratio, random_state=random_state, stratify=y if len(y.unique()) > 1 else None
                )
            else:
                X_train, y_train = X, y
                if test_set is not None:
                    if feature_cols:
                        X_test = test_set[feature_cols].copy()
                        y_test = test_set[target_col].copy()
                    else:
                        X_test = test_set.drop(columns=[target_col]).copy()
                        y_test = test_set[target_col].copy()
                else:
                    X_test, y_test = X, y
            
            # 数据预处理（包括标准化）
            # 初始化缩放器
            self.scaler = StandardScaler()
            X_train_scaled = pd.DataFrame(
                self.scaler.fit_transform(X_train), 
                index=X_train.index, 
                columns=X_train.columns
            )
            X_test_scaled = pd.DataFrame(
                self.scaler.transform(X_test), 
                index=X_test.index, 
                columns=X_test.columns
            )
            
            # 训练模型
            self.model = SVC(**params)
            self.model.fit(X_train_scaled, y_train)
            
            # 预测和评估
            train_predictions = self.model.predict(X_train_scaled)
            test_predictions = self.model.predict(X_test_scaled)
            
            # 获取预测概率（如果支持）
            train_probabilities = None
            test_probabilities = None
            if hasattr(self.model, 'predict_proba'):
                train_probabilities = self.model.predict_proba(X_train_scaled)
                test_probabilities = self.model.predict_proba(X_test_scaled)
            
            # 计算评估指标
            metrics = {
                "train": {
                    "accuracy": accuracy_score(y_train, train_predictions),
                    "precision": precision_score(y_train, train_predictions, average='macro', zero_division=0),
                    "recall": recall_score(y_train, train_predictions, average='macro', zero_division=0),
                    "f1_score": f1_score(y_train, train_predictions, average='macro', zero_division=0)
                },
                "test": {
                    "accuracy": accuracy_score(y_test, test_predictions),
                    "precision": precision_score(y_test, test_predictions, average='macro', zero_division=0),
                    "recall": recall_score(y_test, test_predictions, average='macro', zero_division=0),
                    "f1_score": f1_score(y_test, test_predictions, average='macro', zero_division=0)
                }
            }
            
            # 获取特征重要性（仅对线性核有效）
            feature_importance = {}
            if hasattr(self.model, 'coef_'):
                if len(self.model.coef_.shape) > 1:
                    importances = np.abs(self.model.coef_).mean(axis=0)
                else:
                    importances = np.abs(self.model.coef_)
                feature_importance = {X.columns[i]: float(importance) for i, importance in enumerate(importances)}
            
            # 构建结果字典
            result = {
                "model": self.model,
                "scaler": self.scaler,
                "metrics": metrics,
                "feature_importance": feature_importance,
                "message": "SVM分类完成"
            }
            
            # 如果需要返回模型得分
            if is_return_model_score:
                result["train_predictions"] = train_predictions.tolist()
                result["test_predictions"] = test_predictions.tolist()
                if train_probabilities is not None:
                    result["train_probabilities"] = train_probabilities.tolist()
                    result["test_probabilities"] = test_probabilities.tolist()
            
            return result
        except Exception as e:
            return {
                "error": str(e)
            }