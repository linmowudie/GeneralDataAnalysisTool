"""
Gradient Boosting Regressor
这里将实现梯度提升回归的具体分析逻辑
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np


class GradientBoostingRegressorAnalyzer(BaseAnalyzer):
    """
    梯度提升回归分析器
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
                
                # 检查preprocessing_special_params中的回归相关参数
                if 'preprocessing_special_params' in self.config:
                    for param_name, param_info in self.config['preprocessing_special_params'].items():
                        if isinstance(param_info, dict) and param_name not in metadata_keys:
                            supported_params.add(param_name)
                
                # 检查ML_model_special_params中的梯度提升回归相关参数
                if 'ML_model_special_params' in self.config:
                    for model_type, params_dict in self.config['ML_model_special_params'].items():
                        if isinstance(params_dict, dict) and ('gradient_boosting' in model_type.lower() or 'boosting' in model_type.lower() or 'regressor' in model_type.lower()):
                            for param_name, param_info in params_dict.items():
                                if isinstance(param_info, dict) and param_name not in metadata_keys:
                                    supported_params.add(param_name)
                
                # 校验传入的参数是否都在支持的参数列表中
                if supported_params:
                    for param in params:
                        if param not in supported_params:
                            print(f"警告: 参数 {param} 不在配置文件定义的支持参数列表中")
            
            # 降级方案：硬编码的有效参数列表（GradientBoostingRegressor）
            valid_params = {
                'loss': str,
                'learning_rate': float,
                'n_estimators': int,
                'subsample': float,
                'criterion': str,
                'min_samples_split': (int, float),
                'min_samples_leaf': (int, float),
                'min_weight_fraction_leaf': float,
                'max_depth': int,
                'min_impurity_decrease': float,
                'init': (str, object, type(None)),
                'random_state': (int, type(None)),
                'max_features': (str, int, float, type(None)),
                'alpha': float,
                'verbose': int,
                'max_leaf_nodes': (int, type(None)),
                'warm_start': bool,
                'presort': (str, bool, type(None)),
                'validation_fraction': float,
                'n_iter_no_change': (int, type(None)),
                'tol': float,
                'ccp_alpha': float
            }
            
            # 支持的损失函数
            valid_losses = ['squared_error', 'absolute_error', 'huber', 'quantile']
            
            # 支持的评估标准
            valid_criteria = ['friedman_mse', 'mse', 'mae']
            
            # 支持的max_features值
            valid_max_features = ['sqrt', 'log2', 'auto', None]
            
            # 参数类型和值范围校验
            for param, value in params.items():
                if param in valid_params:
                    # 检查类型
                    if isinstance(valid_params[param], tuple):
                        valid_types = valid_params[param]
                        if not any(isinstance(value, t) for t in valid_types):
                            print(f"参数 {param} 类型错误: 期望 {valid_types}, 得到 {type(value)}")
                            return False
                    elif not isinstance(value, valid_params[param]):
                        print(f"参数 {param} 类型错误: 期望 {valid_params[param]}, 得到 {type(value)}")
                        return False
                    
                    # 检查值范围和有效值
                    if param == 'loss' and value not in valid_losses:
                        print(f"参数 {param} 值错误: 必须是 {valid_losses} 之一")
                        return False
                    elif param == 'learning_rate' and (value <= 0 or value > 1):
                        print(f"参数 {param} 值错误: 必须在 (0, 1] 范围内")
                        return False
                    elif param == 'n_estimators' and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0")
                        return False
                    elif param == 'subsample' and (value <= 0 or value > 1):
                        print(f"参数 {param} 值错误: 必须在 (0, 1] 范围内")
                        return False
                    elif param == 'criterion' and value not in valid_criteria:
                        print(f"参数 {param} 值错误: 必须是 {valid_criteria} 之一")
                        return False
                    elif param == 'min_samples_split':
                        if isinstance(value, int) and value <= 1:
                            print(f"参数 {param} 值错误: 整数类型必须大于 1")
                            return False
                        elif isinstance(value, float) and (value <= 0 or value >= 1):
                            print(f"参数 {param} 值错误: 浮点类型必须在 (0, 1) 范围内")
                            return False
                    elif param == 'min_samples_leaf':
                        if isinstance(value, int) and value <= 0:
                            print(f"参数 {param} 值错误: 整数类型必须大于 0")
                            return False
                        elif isinstance(value, float) and (value <= 0 or value >= 0.5):
                            print(f"参数 {param} 值错误: 浮点类型必须在 (0, 0.5) 范围内")
                            return False
                    elif param == 'min_weight_fraction_leaf' and (value < 0 or value > 0.5):
                        print(f"参数 {param} 值错误: 必须在 [0, 0.5] 范围内")
                        return False
                    elif param == 'max_depth' and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0")
                        return False
                    elif param == 'min_impurity_decrease' and value < 0:
                        print(f"参数 {param} 值错误: 必须大于等于 0")
                        return False
                    elif param == 'max_features':
                        if value not in valid_max_features and not isinstance(value, (int, float)):
                            print(f"参数 {param} 值错误: 必须是 {valid_max_features} 之一或数值类型")
                            return False
                        if isinstance(value, float) and (value <= 0 or value > 1):
                            print(f"参数 {param} 值错误: 浮点类型必须在 (0, 1] 范围内")
                            return False
                    elif param == 'alpha' and (value < 0 or value > 1):
                        print(f"参数 {param} 值错误: 必须在 [0, 1] 范围内")
                        return False
                    elif param == 'max_leaf_nodes' and value is not None and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0 或为 None")
                        return False
                    elif param == 'validation_fraction' and (value <= 0 or value >= 1):
                        print(f"参数 {param} 值错误: 必须在 (0, 1) 范围内")
                        return False
                    elif param == 'n_iter_no_change' and value is not None and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0 或为 None")
                        return False
                    elif param == 'tol' and value < 0:
                        print(f"参数 {param} 值错误: 必须大于等于 0")
                        return False
                    elif param == 'ccp_alpha' and value < 0:
                        print(f"参数 {param} 值错误: 必须大于等于 0")
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
        
        # 梯度提升对特征缩放有一定敏感性，可以添加标准化
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
            X = pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
        
        # 处理目标变量
        if y is not None and y.isnull().any():
            y = y.fillna(y.mean())
        
        return X, y
    
    def train(self, X_train: pd.DataFrame, y: Optional[pd.Series] = None) -> Any:
        """
        训练梯度提升回归模型
        
        参数:
            X_train (pd.DataFrame): 训练特征数据
            y (Optional[pd.Series]): 训练目标数据
            
        返回:
            Any: 训练完成的模型对象
        """
        try:
            # 确保有目标变量
            if y is None:
                raise ValueError("梯度提升回归需要目标变量")
            
            # 创建并训练梯度提升回归模型
            self.model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
            self.model.fit(X_train, y)
            return self.model
        except Exception as e:
            raise Exception(f"梯度提升回归训练失败: {str(e)}")
    
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
            result = {}
            
            # 获取特征重要性
            if hasattr(model, 'feature_importances_'):
                result["feature_importances"] = model.feature_importances_.tolist()
            
            # 获取迭代次数
            if hasattr(model, 'n_estimators_'):
                result["n_estimators"] = model.n_estimators_
            
            # 学习率
            if hasattr(model, 'learning_rate'):
                result["learning_rate"] = model.learning_rate
            
            # 如果有目标变量，计算预测值和评估指标
            if y is not None:
                y_pred = model.predict(X)
                result["predictions"] = y_pred.tolist()
                
                # 计算评估指标
                try:
                    result["mse"] = float(mean_squared_error(y, y_pred))
                    result["mae"] = float(mean_absolute_error(y, y_pred))
                    result["r2"] = float(r2_score(y, y_pred))
                    result["rmse"] = float(np.sqrt(result["mse"]))
                except Exception as e:
                    print(f"计算评估指标失败: {e}")
            
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
            if hasattr(model, 'feature_importances_'):
                # 返回特征重要性
                importances = model.feature_importances_
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
            print(f"保存梯度提升回归模型失败: {e}")
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
            # 确保使用相同的预处理步骤
            if self.scaler is not None:
                X_scaled = self.scaler.transform(X)
                X_scaled_df = pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
                predictions = model.predict(X_scaled_df)
            else:
                predictions = model.predict(X)
            
            return pd.Series(predictions, name='prediction')
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
        return ['mse', 'rmse', 'mae', 'r2']
    
    def analyzer(
        self, 
        df: pd.DataFrame, 
        learn_type: str, 
        model_type: str, 
        model: str,
        random_state: int = 42, 
        is_split: bool = True,  # 回归任务默认划分训练/测试集
        split_ratio: float = 0.2,
        feature_cols: Optional[List[str]] = None, 
        target_col: Optional[str] = None,  # 回归任务需要目标列
        metrics_list: Optional[List[str]] = None, 
        is_return_model_score: bool = True,
        feature_cols_encoding: str = "auto", 
        target_col_encoding: str = "auto",
        test_set: Optional[pd.DataFrame] = None, 
        model_params: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
        """
        执行完整梯度提升回归流程的核心方法
        
        参数:
            df (pd.DataFrame): 输入数据集，不能为空
            learn_type (str): 学习类型，如 "ML"（机器学习）
            model_type (str): 模型类别，如 "regression"
            model (str): 模型名称，如 "gradient_boosting_regressor"
            random_state (int): 随机种子，用于复现实验结果，默认为42
            is_split (bool): 是否自动划分训练/测试集，默认为True
            split_ratio (float): 测试集占比，范围 (0,1)，仅当 is_split=True 时生效，默认为0.2
            feature_cols (List[str]): 特征列名列表，不能为空
            target_col (str): 目标列名，回归任务必须提供
            metrics_list (List[str]): 评价指标列表，如 ["mse", "r2"]，默认使用默认指标
            is_return_model_score (bool): 是否返回模型评估得分，默认为True
            feature_cols_encoding (str): 特征列编码方式，支持 "onehot"、"label"、"ordinal"、"none"、"auto" 等，默认为"auto"
            target_col_encoding (str): 目标列编码方式，回归任务通常为 "none"
            test_set (pd.DataFrame): 外部传入的测试集，仅当 is_split=False 时使用，默认为None
            model_params (Dict[str, Any]): 模型特定超参数，默认为{}
            
        返回:
            Dict[str, Any]: 包含模型、评估结果等信息的字典
        """
        try:
            # 验证必要参数
            if not target_col:
                raise ValueError("回归任务必须提供目标列")
            
            # 准备数据
            if feature_cols:
                X = df[feature_cols].copy()
            else:
                # 如果未指定特征列，使用除目标列外的所有列
                X = df.drop(columns=[target_col]).copy()
            
            # 获取目标变量
            y = df[target_col].copy()
            
            # 确保X是DataFrame类型，y是Series类型
            if not isinstance(X, pd.DataFrame):
                X = pd.DataFrame(X)
            if not isinstance(y, pd.Series):
                y = pd.Series(y)
            
            # 检查特征数量
            if X.shape[1] == 0:
                raise ValueError("数据集至少需要包含一个特征列")
            
            # 处理模型参数
            if model_params is None:
                model_params = {}
            
            # 校验参数
            self.validate_params(model_params)
            
            # 设置默认参数
            params = {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'random_state': random_state
            }
            params.update(model_params)
            
            # 处理是否使用标准化
            use_scaling = model_params.pop('use_scaling', True)  # 梯度提升对标准化较敏感，默认开启
            if use_scaling:
                self.scaler = StandardScaler()
            
            # 划分训练/测试集
            if is_split and test_set is None:
                from sklearn.model_selection import train_test_split
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=split_ratio, random_state=random_state
                )
            else:
                X_train, y_train = X, y
                if test_set is not None:
                    X_test = test_set[feature_cols].copy() if feature_cols else test_set.drop(columns=[target_col]).copy()
                    y_test = test_set[target_col].copy()
                else:
                    X_test, y_test = None, None
            
            # 数据预处理
            # 处理缺失值
            if X_train.isnull().any().any():
                X_train = X_train.fillna(X_train.mean())
            
            if y_train.isnull().any():
                y_train = y_train.fillna(y_train.mean())
            
            # 特征标准化（如果启用）
            if self.scaler is not None:
                X_train_scaled = pd.DataFrame(
                    self.scaler.fit_transform(X_train), 
                    index=X_train.index, 
                    columns=X_train.columns
                )
            else:
                X_train_scaled = X_train.copy()
            
            # 创建并训练梯度提升回归模型
            self.model = GradientBoostingRegressor(**params)
            self.model.fit(X_train_scaled, y_train)
            
            # 计算训练集评估指标
            train_metrics = {}
            if X_train_scaled.shape[0] > 0:
                y_train_pred = self.model.predict(X_train_scaled)
                train_metrics["mse"] = float(mean_squared_error(y_train, y_train_pred))
                train_metrics["mae"] = float(mean_absolute_error(y_train, y_train_pred))
                train_metrics["r2"] = float(r2_score(y_train, y_train_pred))
                train_metrics["rmse"] = float(np.sqrt(train_metrics["mse"]))
            
            # 计算测试集评估指标（如果有）
            test_metrics = {}
            test_predictions = None
            if X_test is not None and y_test is not None:
                # 处理测试集缺失值
                if X_test.isnull().any().any():
                    X_test = X_test.fillna(X_train.mean())  # 使用训练集的均值填充
                
                # 特征标准化（如果启用）
                if self.scaler is not None:
                    X_test_scaled = pd.DataFrame(
                        self.scaler.transform(X_test),
                        index=X_test.index,
                        columns=X_test.columns
                    )
                else:
                    X_test_scaled = X_test.copy()
                
                test_predictions = self.model.predict(X_test_scaled)
                test_metrics["mse"] = float(mean_squared_error(y_test, test_predictions))
                test_metrics["mae"] = float(mean_absolute_error(y_test, test_predictions))
                test_metrics["r2"] = float(r2_score(y_test, test_predictions))
                test_metrics["rmse"] = float(np.sqrt(test_metrics["mse"]))
            
            # 获取特征重要性
            feature_importance = {}
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                feature_importance = {X.columns[i]: float(imp) for i, imp in enumerate(importances)}
            
            # 构建结果字典
            result = {
                "model": self.model,
                "scaler": self.scaler if use_scaling else None,
                "train_metrics": train_metrics,
                "test_metrics": test_metrics if test_metrics else None,
                "feature_importance": feature_importance,
                "message": "梯度提升回归训练完成"
            }
            
            # 添加模型配置信息
            result["model_config"] = params
            result["n_estimators"] = params.get('n_estimators', 100)
            result["learning_rate"] = params.get('learning_rate', 0.1)
            result["max_depth"] = params.get('max_depth', 'None')
            
            # 如果有最佳迭代次数信息（用于早停）
            if hasattr(self.model, 'n_estimators_'):
                result["best_n_estimators"] = self.model.n_estimators_
            
            # 获取训练过程中的损失历史
            if hasattr(self.model, 'train_score_'):
                result["train_score_history"] = self.model.train_score_.tolist()
            
            # 如果有验证分数历史
            if hasattr(self.model, 'loss_') and hasattr(self.model, 'validation_score_'):
                result["validation_score_history"] = self.model.validation_score_.tolist()
            
            # 如果需要返回预测值
            if is_return_model_score:
                result["train_predictions"] = y_train_pred.tolist() if 'y_train_pred' in locals() else None
                if test_predictions is not None:
                    result["test_predictions"] = test_predictions.tolist()
            
            return result
        except Exception as e:
            return {
                "error": str(e)
            }