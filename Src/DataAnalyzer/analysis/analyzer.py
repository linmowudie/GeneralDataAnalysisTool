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
import json
from typing import Any, Callable, Dict, List, Optional, Union

# ===== 第三方库 =====
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, MeanShift, DBSCAN
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.metrics import (
    accuracy_score,
    adjusted_rand_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.manifold import TSNE
import os

# 导入子模块
from . import regression
from . import classification
from . import clustering
from . import dimensionality_reduction
from . import association_rule_learning

# 日志配置：保持模块名，方便排查
logger = logging.getLogger(__name__)

# =========================================================
# 1. 模型注册中心：新增模型只需在此处追加--- 
# =========================================================

# 模型映射字典
_model_map = {
    'LinearRegression': LinearRegression,
    'Ridge': Ridge,
    'Lasso': Lasso,
    'LogisticRegression': LogisticRegression,
    'DecisionTreeClassifier': DecisionTreeClassifier,
    'KNeighborsClassifier': KNeighborsClassifier,
    'SVC': SVC,
    'KMeans': KMeans,
    'MeanShift': MeanShift,
    'DBSCAN': DBSCAN,
    'StandardScaler': StandardScaler,
    'MinMaxScaler': MinMaxScaler,
    'PCA': PCA,
    'TSNE': TSNE,
}

def load_model_config():
    """从JSON文件加载模型配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'model_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 将嵌套结构扁平化，并将字符串类名替换为实际的类引用
    flat_config = {}
    for category, models in config.items():
        for model_name, model_info in models.items():
            if model_info['class'] in _model_map:
                model_info['class'] = _model_map[model_info['class']]
            flat_config[model_name] = model_info
    
    return flat_config

MODEL_CONFIG: Dict[str, Dict[str, Any]] = load_model_config()

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
    model_params: Optional[Dict[str, Any]] = None,  # 新增参数，用于传入额外的模型参数
) -> Dict[str, Any]:
    """
    数据分析统一入口函数
    根据模型类型分发到不同的子模块进行处理
    
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
    
    # 确定任务类型
    model_name = model.lower()
    if model_name not in MODEL_CONFIG:
        raise ValueError(f"不支持的模型: {model_name}")
    
    task_type = MODEL_CONFIG[model_name]['type']
    
    # 根据任务类型分发到不同的子模块
    if task_type == 'regression':
        analyzer = regression.Regression(
            df=df,
            model=model,
            random_state=random_state,
            is_split=is_split,
            split_ratio=split_ratio,
            feature_cols=feature_cols,
            target_col=target_col,
            is_return_model_param=is_return_model_param,
            metrics_list=metrics_list,
            is_return_model_score=is_return_model_score,
            is_return_training_set=is_return_training_set,
            is_return_model_predicting_set=is_return_model_predicting_set,
            feature_cols_encoding=feature_cols_encoding,
            target_col_encoding=target_col_encoding,
            test_set=test_set,
            model_params=model_params,
        )
    elif task_type == 'classification':
        analyzer = classification.Classification(
            df=df,
            model=model,
            random_state=random_state,
            is_split=is_split,
            split_ratio=split_ratio,
            feature_cols=feature_cols,
            target_col=target_col,
            is_return_model_param=is_return_model_param,
            metrics_list=metrics_list,
            is_return_model_score=is_return_model_score,
            is_return_training_set=is_return_training_set,
            is_return_model_predicting_set=is_return_model_predicting_set,
            feature_cols_encoding=feature_cols_encoding,
            target_col_encoding=target_col_encoding,
            test_set=test_set,
            model_params=model_params,
        )
    elif task_type == 'clustering':
        analyzer = clustering.Clustering(
            df=df,
            model=model,
            random_state=random_state,
            is_split=is_split,
            split_ratio=split_ratio,
            feature_cols=feature_cols,
            target_col=target_col,
            is_return_model_param=is_return_model_param,
            metrics_list=metrics_list,
            is_return_model_score=is_return_model_score,
            is_return_training_set=is_return_training_set,
            is_return_model_predicting_set=is_return_model_predicting_set,
            feature_cols_encoding=feature_cols_encoding,
            target_col_encoding=target_col_encoding,
            test_set=test_set,
            model_params=model_params,
        )
    elif task_type == 'transformer':
        analyzer = dimensionality_reduction.DimensionalityReduction(
            df=df,
            model=model,
            random_state=random_state,
            is_split=is_split,
            split_ratio=split_ratio,
            feature_cols=feature_cols,
            target_col=target_col,
            is_return_model_param=is_return_model_param,
            metrics_list=metrics_list,
            is_return_model_score=is_return_model_score,
            is_return_training_set=is_return_training_set,
            is_return_model_predicting_set=is_return_model_predicting_set,
            feature_cols_encoding=feature_cols_encoding,
            target_col_encoding=target_col_encoding,
            test_set=test_set,
            model_params=model_params,
        )
    elif task_type == 'association':
        analyzer = association_rule_learning.AssociationRuleLearning(
            df=df,
            model=model,
            random_state=random_state,
            is_split=is_split,
            split_ratio=split_ratio,
            feature_cols=feature_cols,
            target_col=target_col,
            is_return_model_param=is_return_model_param,
            metrics_list=metrics_list,
            is_return_model_score=is_return_model_score,
            is_return_training_set=is_return_training_set,
            is_return_model_predicting_set=is_return_model_predicting_set,
            feature_cols_encoding=feature_cols_encoding,
            target_col_encoding=target_col_encoding,
            test_set=test_set,
            model_params=model_params,
        )
    else:
        # 默认使用原来的通用分析器
        from .analyzer_backup import AnalyzeData
        analyzer = AnalyzeData(
            df=df,
            model=model,
            random_state=random_state,
            is_split=is_split,
            split_ratio=split_ratio,
            feature_cols=feature_cols,
            target_col=target_col,
            is_return_model_param=is_return_model_param,
            metrics_list=metrics_list,
            is_return_model_score=is_return_model_score,
            is_return_training_set=is_return_training_set,
            is_return_model_predicting_set=is_return_model_predicting_set,
            feature_cols_encoding=feature_cols_encoding,
            target_col_encoding=target_col_encoding,
            test_set=test_set,
            model_params=model_params,
        )
    
    # 执行分析并返回结果
    return analyzer.run()


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
        return analyze_data(**self.kwargs)