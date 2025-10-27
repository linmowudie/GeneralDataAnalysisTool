"""
UMAP
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List
import pandas as pd
import joblib
import numpy as np
import json

# 可能需要安装umap-learn库: pip install umap-learn
UMAP_AVAILABLE = False
try:
    from umap import UMAP as UMAPModel
    UMAP_AVAILABLE = True
except ImportError:
    UMAPModel = None


class UMAPAnalyzer(BaseAnalyzer):
    """
    UMAP降维分析器
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        # 加载配置文件
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        从配置文件加载模型参数配置
        
        返回:
            Dict[str, Any]: 配置字典
        """
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Configs', 'model_analysis.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return {}
        if not UMAP_AVAILABLE:
            raise ImportError("umap-learn库未安装，请使用'pip install umap-learn'安装")
    
    def load_params(self, model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        加载和处理模型参数
        
        参数:
            model_params (Dict[str, Any]): 模型参数字典，如果为None则返回空字典
            
        返回:
            Dict[str, Any]: 处理后的参数字典
        """
        # 如果传入的是字典，直接返回；如果是None，返回空字典
        if isinstance(model_params, dict):
            return model_params.copy()  # 返回副本避免修改原始数据
        elif model_params is None:
            return {}
        else:
            # 如果既不是字典也不是None，尝试转换或返回空字典
            try:
                return dict(model_params)
            except:
                return {}
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        参数校验方法
        
        参数:
            params (Dict[str, Any]): 待校验的参数字典
            
        返回:
            bool: 校验是否通过
        """
        try:
            # 从配置文件中读取支持的参数列表（推荐方式）
            valid_params = set()
            
            if self.config:
                # 从预处理方法参数中获取
                if 'preprocessing_special_params' in self.config and 'umap' in self.config['preprocessing_special_params']:
                    preprocess_config = self.config['preprocessing_special_params']['umap']
                    # 提取所有参数名，排除key_description等元数据键
                    valid_params.update({p for p in preprocess_config.keys() if not p.startswith('key_')})
                
                # 从ML模型参数中获取
                if 'ML_model_special_params' in self.config:
                    # 检查所有任务类型中的UMAP配置
                    for task_type in self.config['ML_model_special_params'].values():
                        if isinstance(task_type, dict) and 'umap' in task_type:
                            umap_config = task_type['umap']
                            valid_params.update({p for p in umap_config.keys() if not p.startswith('key_')})
            
            # 如果配置未加载或没有找到参数，使用硬编码的默认参数列表作为降级方案
            if not valid_params:
                valid_params = {
                    'n_neighbors', 'n_components', 'min_dist', 'metric', 
                    'random_state', 'n_epochs', 'learning_rate', 'init', 
                    'spread', 'low_memory', 'set_op_mix_ratio', 'local_connectivity',
                    'repulsion_strength', 'negative_sample_rate', 'transform_queue_size',
                    'a', 'b', 'angular_rp_forest', 'target_n_neighbors',
                    'target_metric', 'target_weight', 'transform_seed', 'force_approximation_algorithm',
                    'verbose', 'unique', 'densmap', 'dens_lambda',
                    'dens_frac', 'dens_var_shift', 'output_metric', 'output_dens',
                    'pcg_rand', 'tqdm_kwds', 'euclidean_output', 'parallel',
                    'callbacks', 'callbacks_kwargs'
                }
            
            # 检查所有参数名是否在有效列表中
            for param_name in params:
                if param_name not in valid_params:
                    print(f"警告: UMAP不支持的参数 '{param_name}'")
                    # 不抛出异常，允许用户尝试使用未知参数，但发出警告
            
            # 参数范围校验
            if 'n_neighbors' in params:
                if not isinstance(params['n_neighbors'], int):
                    raise ValueError("n_neighbors必须是整数")
                if params['n_neighbors'] <= 0:
                    raise ValueError("n_neighbors必须大于0")
            
            if 'n_components' in params:
                if not isinstance(params['n_components'], int):
                    raise ValueError("n_components必须是整数")
                if params['n_components'] <= 0:
                    raise ValueError("n_components必须大于0")
            
            if 'min_dist' in params:
                if not isinstance(params['min_dist'], (int, float)):
                    raise ValueError("min_dist必须是数字")
                if not (0 <= params['min_dist'] <= 1):
                    raise ValueError("min_dist必须在[0, 1]范围内")
            
            if 'spread' in params:
                if not isinstance(params['spread'], (int, float)):
                    raise ValueError("spread必须是数字")
                if params['spread'] <= 0:
                    raise ValueError("spread必须大于0")
            
            if 'learning_rate' in params:
                if not isinstance(params['learning_rate'], (int, float)):
                    raise ValueError("learning_rate必须是数字")
                if params['learning_rate'] <= 0:
                    raise ValueError("learning_rate必须大于0")
            
            return True
        except Exception as e:
            print(f"参数校验失败: {str(e)}")
            return False
    
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> tuple:
        """
        数据预处理方法
        
        参数:
            X (pd.DataFrame): 特征数据
            y (Optional[pd.Series]): 目标数据
            
        返回:
            tuple: 预处理后的(X, y)数据
        """
        # UMAP不需要特殊预处理
        return X, y
    
    def train(self, X_train: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        训练UMAP模型
        
        参数:
            X_train (pd.DataFrame): 训练特征数据
            params (Dict[str, Any]): 模型参数
            
        返回:
            Any: 训练完成的模型对象
        """
        try:
            if UMAPModel is None:
                raise ImportError("umap-learn库未安装，请使用'pip install umap-learn'安装")
            
            # 使用传入的参数初始化模型，如果没有则使用默认值
            if params is None:
                params = {}
            self.model = UMAPModel(**params)
            self.model.fit(X_train)
            return self.model
        except Exception as e:
            raise Exception(f"UMAP训练失败: {str(e)}")
    
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
        return {"message": "UMAP无需后处理"}
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        获取特征重要性（UMAP无特征重要性概念）
        
        参数:
            model (Any): 模型对象
            
        返回:
            Dict[str, float]: 特征重要性字典
        """
        return {}
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """
        保存UMAP模型
        
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
            print(f"保存UMAP模型失败: {e}")
            return False
    
    def predict(self, model: Any, X: pd.DataFrame) -> pd.Series:
        """
        使用UMAP转换数据
        
        参数:
            model (Any): UMAP模型
            X (pd.DataFrame): 输入数据
            
        返回:
            pd.Series: 降维后的数据
        """
        try:
            X_reduced = model.transform(X)
            # 返回降维后的数组作为Series
            return pd.Series(X_reduced.flatten())
        except Exception as e:
            raise Exception(f"UMAP预测失败: {str(e)}")
    
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
        try:
            # 准备数据
            if feature_cols:
                X = df[feature_cols]
            else:
                X = df
            
            # 确保X是DataFrame类型
            if not isinstance(X, pd.DataFrame):
                X = pd.DataFrame(X)
            
            # 加载模型参数
            params = self.load_params(model_params)
            # 添加随机种子
            params['random_state'] = random_state
            
            # 训练UMAP
            trained_model = self.train(X, params)
            
            # 降维数据
            reduced_data = self.predict(trained_model, X)
            
            # 准备返回结果
            result = {
                "model": trained_model,
                "reduced_data": reduced_data,
                "message": "UMAP训练和应用成功"
            }
            
            # 如果提供了metrics_list或需要返回模型分数，计算额外指标
            if metrics_list or is_return_model_score:
                # 获取需要计算的指标列表
                calculate_metrics = metrics_list if metrics_list else self.get_default_metrics(model_type)
                
                # 对于UMAP，可以计算trustworthiness或continuity等指标
                # 注意：scikit-learn提供了计算这些指标的函数，但需要额外导入
                if any(metric in calculate_metrics for metric in ["trustworthiness", "continuity"]):
                    try:
                        from sklearn.manifold import trustworthiness
                        if "trustworthiness" in calculate_metrics:
                            # 计算trustworthiness
                            X_reduced_array = trained_model.transform(X)
                            trust_score = trustworthiness(X, X_reduced_array)
                            result["trustworthiness"] = trust_score
                    except Exception as metric_error:
                        result["metric_calculation_warning"] = f"无法计算额外指标: {str(metric_error)}"
            
            return result
        except Exception as e:
            return {
                "error": str(e)
            }