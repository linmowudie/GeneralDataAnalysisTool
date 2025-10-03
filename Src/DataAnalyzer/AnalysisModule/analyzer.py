# -*- coding: utf-8 -*-
"""
Src/DataAnalyzer/analysis/analyzer.py
数据分析器模块

该模块提供各种数据分析功能的实现，包括描述性统计、相关性分析、
分组分析等常见的数据分析方法。
"""

from __future__ import annotations

# ===== 标准库 =====
import logging
import random
import sys
import os
from typing import Any, Callable, Dict, List, Optional, Type, Union

# ===== 第三方库 =====
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    adjusted_rand_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# 导入配置管理器
from ..Configs.config_manager import MODEL_CONFIG, MODEL_MAPPING_CONFIG

# 通过项目根路径导入性能计时装饰器
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from PythonScripts.running_timer import run_timer

# 日志配置：保持模块名，方便排查
logger = logging.getLogger(__name__)

# =========================================================
# 1. 模型注册中心：新增模型只需在此处追加--- 
# =========================================================

# 从配置中获取模型映射
_model_map = {}

# =========================================================
# 2. 评估指标映射表：不同任务类型对应不同指标
# =========================================================
METRICS_MAP: Dict[str, Dict[str, Callable[..., Union[float, np.floating]]]] = {
    'regression': {
        'mse': mean_squared_error,
        'mae': mean_absolute_error,
        'r2': r2_score,
    },
    'classification': {
        'accuracy': accuracy_score,
    },
    'clustering': {
        'ari': adjusted_rand_score,      # 需真实标签
        'silhouette': silhouette_score,  # 仅需特征矩阵
    }
}

# 动态导入模型类
def _import_model_classes():
    """动态导入模型类"""
    global _model_map
    mapping = MODEL_MAPPING_CONFIG.get("model_mapping", {})
    
    for model_name, class_path in mapping.items():
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            _model_map[model_name] = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"无法导入模型 {model_name} ({class_path}): {e}")

# 初始化模型类导入
_import_model_classes()

def _get_model_class(model_name: str) -> Type[Any]:
    """
    根据模型名称获取模型类
    
    Args:
        model_name : 模型名称(小写)，必须在 MODEL_CONFIG 中注册
        
    Returns:
        sklearn或其他库中的模型类
        
    Raises:
        ValueError: 当模型名称不在支持列表中时
    """
    model_name = model_name.lower()
    
    if model_name not in MODEL_CONFIG:
        supported = ', '.join(MODEL_CONFIG.keys())
        raise ValueError(f"不支持的模型: {model_name}。支持的模型: {supported}")
    
    config = MODEL_CONFIG[model_name]
    module_name = config['class']
    
    # 根据模型类型导入相应的模块
    task_type = MODEL_CONFIG[model_name]['type']
    if task_type in ['regression', 'classification']:
        if module_name in ['LinearRegression', 'Ridge', 'Lasso']:
            from sklearn.linear_model import LinearRegression, Ridge, Lasso
            model_map = {
                'LinearRegression': LinearRegression,
                'Ridge': Ridge,
                'Lasso': Lasso
            }
        elif module_name in ['LogisticRegression']:
            from sklearn.linear_model import LogisticRegression
            model_map = {'LogisticRegression': LogisticRegression}
        elif module_name in ['DecisionTreeClassifier']:
            from sklearn.tree import DecisionTreeClassifier
            model_map = {'DecisionTreeClassifier': DecisionTreeClassifier}
        elif module_name in ['KNeighborsClassifier']:
            from sklearn.neighbors import KNeighborsClassifier
            model_map = {'KNeighborsClassifier': KNeighborsClassifier}
        elif module_name in ['SVC']:
            from sklearn.svm import SVC
            model_map = {'SVC': SVC}
        else:
            raise ValueError(f"未知的模型类: {module_name}")
            
    elif task_type == 'clustering':
        if module_name in ['KMeans']:
            from sklearn.cluster import KMeans
            model_map = {'KMeans': KMeans}
        elif module_name in ['MeanShift']:
            from sklearn.cluster import MeanShift
            model_map = {'MeanShift': MeanShift}
        elif module_name in ['DBSCAN']:
            from sklearn.cluster import DBSCAN
            model_map = {'DBSCAN': DBSCAN}
        else:
            raise ValueError(f"未知的聚类模型类: {module_name}")
            
    elif task_type == 'transformer':
        if module_name in ['PCA']:
            from sklearn.decomposition import PCA
            model_map = {'PCA': PCA}
        elif module_name in ['StandardScaler', 'MinMaxScaler']:
            from sklearn.preprocessing import StandardScaler, MinMaxScaler
            model_map = {
                'StandardScaler': StandardScaler,
                'MinMaxScaler': MinMaxScaler
            }
        elif module_name in ['TSNE']:
            from sklearn.manifold import TSNE
            model_map = {'TSNE': TSNE}
        else:
            raise ValueError(f"未知的转换器类: {module_name}")
            
    elif task_type == 'association':
        # 关联规则学习模型
        if module_name in ['Apriori']:
            try:
                from mlxtend.frequent_patterns import apriori
                model_map = {'Apriori': apriori}
            except ImportError:
                raise ImportError("关联规则学习需要 mlxtend 库，请安装: pip install mlxtend")
        elif module_name in ['AssociationRules']:
            try:
                from mlxtend.frequent_patterns import association_rules
                model_map = {'AssociationRules': association_rules}
            except ImportError:
                raise ImportError("关联规则学习需要 mlxtend 库，请安装: pip install mlxtend")
        else:
            raise ValueError(f"未知的关联规则模型类: {module_name}")
    else:
        raise ValueError(f"未知的任务类型: {task_type}")
        
    return model_map[module_name]

@run_timer
def analyze_data(
    df: pd.DataFrame,
    model: str,
    random_state: int = 42,
    is_split: bool = True,
    split_ratio: float = 0.8,
    feature_cols: Optional[List[str]] = None,
    target_col: Optional[str] = None,
    is_return_model_param: bool = False,
    metrics_list: Optional[List[str]] = None,
    is_return_model_score: bool = True,
    is_return_training_set: bool = False,
    is_return_model_predicting_set: bool = False,
    feature_cols_encoding: str = 'onehot',
    target_col_encoding: str = 'label',
    test_set: Optional[pd.DataFrame] = None,
    model_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    通用数据分析接口函数
    
    Args:
        df: 训练数据集 DataFrame
        model: 模型名称(小写)，必须在 MODEL_CONFIG 中注册
        random_state: 随机种子，保证结果可复现
        is_split: 是否做训练/测试划分
        split_ratio: 训练集占比(0~1)
        feature_cols: 指定特征列，None 代表除 target_col 外所有列
        target_col: 目标列名称
        is_return_model_param: 是否返回模型超参数
        metrics_list: 指定评估指标，None 则使用默认指标
        is_return_model_score: 是否返回评分
        is_return_training_set: 是否返回划分后的训练/测试集
        is_return_model_predicting_set: 是否返回预测结果 Series
        feature_cols_encoding: 类别型特征编码方式，可选 'onehot' / 'label'
        target_col_encoding: 目标列编码方式，目前仅支持 'label'
        test_set: 外部测试集 DataFrame，可包含目标列
        model_params: 额外的模型参数，将覆盖默认参数
        
    Returns:
        dict: 包含分析结果的字典
        
    Raises:
        ValueError: 当参数不合法时
    """
    # 确保模型名称是小写的
    model = model.lower()
    
    # 检查模型是否支持
    if model not in MODEL_CONFIG:
        supported_models = ', '.join(MODEL_CONFIG.keys())
        raise ValueError(f"不支持的模型: {model}。支持的模型: {supported_models}")
    
    # 获取模型配置
    model_config = MODEL_CONFIG[model]
    task_type = model_config['type']
    
    # 确定特征列和目标列
    if feature_cols is None:
        if target_col is None:
            feature_cols = list(df.columns)
        else:
            feature_cols = [col for col in df.columns if col != target_col]
    
    # 准备数据
    X = df[feature_cols]
    y = df[target_col] if target_col else None
    
    # 数据划分
    X_train, X_test, y_train, y_test = None, None, None, None
    if is_split and y is not None:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=1-split_ratio, random_state=random_state
        )
    else:
        X_train, y_train = X, y
    
    # 获取模型类并创建实例
    ModelClass = _get_model_class(model)
    
    # 处理模型参数
    params = model_config.get('default_params', {}).copy()
    if model_params:
        params.update(model_params)
    
    # 特殊处理某些参数
    if 'random_state' in model_config.get('init_params', []) and 'random_state' not in params:
        params['random_state'] = random_state
    
    # 创建模型实例
    model_instance = ModelClass(**params)
    
    # 训练模型
    if y_train is not None:
        model_instance.fit(X_train, y_train)
    else:
        model_instance.fit(X_train)
    
    # 预测
    predictions = None
    if is_return_model_predicting_set and X_test is not None:
        predictions = model_instance.predict(X_test)
    
    # 评估模型
    model_score = {}
    if is_return_model_score and y_test is not None and predictions is not None:
        # 根据任务类型选择合适的评估指标
        if task_type in METRICS_MAP:
            for metric_name, metric_func in METRICS_MAP[task_type].items():
                try:
                    if metric_name in ['r2', 'mse', 'mae']:  # 回归指标
                        model_score[metric_name] = float(metric_func(y_test, predictions))
                    elif metric_name in ['accuracy']:  # 分类指标
                        model_score[metric_name] = float(metric_func(y_test, predictions))
                    elif metric_name in ['ari', 'silhouette']:  # 聚类指标
                        model_score[metric_name] = float(metric_func(y_test, predictions))
                except Exception as e:
                    logger.warning(f"计算指标 {metric_name} 时出错: {e}")
    
    # 构建返回结果
    result = {
        'trained_model': model_instance,
        'task_type': task_type,
        'model_params': params if is_return_model_param else None,
        'model_score': model_score if is_return_model_score else None,
        'X_train': X_train if is_return_training_set else None,
        'X_test': X_test if is_return_training_set else None,
        'y_train': y_train if is_return_training_set else None,
        'y_test': y_test if is_return_training_set else None,
        'predictions': predictions if is_return_model_predicting_set else None,
    }
    
    return result


# 保持向后兼容性，保留旧的类接口
class AnalyzeData:
    """
    通用分析主类（向后兼容）
    通过 run() 方法串联完整流程
    """

    # 对外暴露支持的模型列表
    model_type: List[str] = list(MODEL_CONFIG.keys())

    def __init__(
        self,
        df: pd.DataFrame,
        model: str,
        random_state: int = 42,
        is_split: bool = True,
        split_ratio: float = 0.8,
        feature_cols: Optional[List[str]] = None,
        target_col: Optional[str] = None,
        is_return_model_param: bool = False,
        metrics_list: Optional[List[str]] = None,
        is_return_model_score: bool = True,
        is_return_training_set: bool = False,
        is_return_model_predicting_set: bool = False,
        feature_cols_encoding: str = 'onehot',
        target_col_encoding: str = 'label',
        test_set: Optional[pd.DataFrame] = None,
        model_params: Optional[Dict[str, Any]] = None,  # 新增参数，用于传入额外的模型参数
    ):
        """
        参数说明
        ----------
        df : 训练数据集 DataFrame
        model : 模型名称(小写)，必须在 MODEL_CONFIG 中注册
        random_state : 随机种子，保证结果可复现
        is_split : 是否做训练/测试划分
        split_ratio : 训练集占比(0~1)
        feature_cols : 指定特征列，None 代表除 target_col 外所有列
        target_col : 目标列名称
        is_return_model_param : 是否返回模型超参数
        metrics_list : 指定评估指标，None 则使用默认指标
        is_return_model_score : 是否返回评分
        is_return_training_set : 是否返回划分后的训练/测试集
        is_return_model_predicting_set : 是否返回预测结果 Series
        feature_cols_encoding : 类别型特征编码方式，可选 'onehot' / 'label'
        target_col_encoding : 目标列编码方式，目前仅支持 'label'
        test_set : 外部测试集 DataFrame，可包含目标列
        model_params : 额外的模型参数，将覆盖默认参数
        """
        self.kwargs = {
            'df': df,
            'model': model,
            'random_state': random_state,
            'is_split': is_split,
            'split_ratio': split_ratio,
            'feature_cols': feature_cols,
            'target_col': target_col,
            'is_return_model_param': is_return_model_param,
            'metrics_list': metrics_list,
            'is_return_model_score': is_return_model_score,
            'is_return_training_set': is_return_training_set,
            'is_return_model_predicting_set': is_return_model_predicting_set,
            'feature_cols_encoding': feature_cols_encoding,
            'target_col_encoding': target_col_encoding,
            'test_set': test_set,
            'model_params': model_params,
        }

    def run(self) -> Dict[str, Any]:
        """
        统一执行入口
        """
        # 直接执行分析而不是调用analyze_data函数，避免递归
        return analyze_data(**self.kwargs)

    def get_supported_models(self) -> List[str]:
        """
        获取支持的模型列表
        
        Returns:
            List[str]: 支持的模型名称列表
        """
        # 从配置管理器获取模型列表
        model_type: List[str] = list(MODEL_CONFIG.keys())
        return model_type

    def _get_model_class(self, model_name: str) -> Type[Any]:
        """
        根据模型名称获取模型类
        
        Args:
            model : 模型名称(小写)，必须在 MODEL_CONFIG 中注册
            
        Returns:
            sklearn或其他库中的模型类
            
        Raises:
            ValueError: 当模型名称不在支持列表中时
        """
        return _get_model_class(model_name)