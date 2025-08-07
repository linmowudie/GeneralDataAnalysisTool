# -*- coding: utf-8 -*-
"""
通用机器学习分析封装模块 AnalyzeData
====================================
功能：
1. 支持回归 / 分类 / 聚类 / 数据变换 4 大类任务
2. 支持自动编码、训练、评估、预测
3. 支持外部测试集
4. 支持按需返回训练集、预测结果、模型参数、评估指标

使用示例：
    >>> ada = AnalyzeData(df, model='logisticregression', target_col='y')
    >>> result = ada.run()
    >>> print(result['scores'])
"""

from __future__ import annotations

# ===== 标准库 =====
import logging
import random
from typing import Any, Callable, Dict, List, Optional, Union

# ===== 第三方库 =====
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, MeanShift
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, LogisticRegression
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

# 日志配置：保持模块名，方便排查
logger = logging.getLogger(__name__)

# =========================================================
# 1. 模型注册中心：新增模型只需在此处追加即可
# =========================================================
MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
    'linearregression': {
        'class': LinearRegression,
        'type': 'regression',
        'init_params': ['fit_intercept'],
        'default_params': {'fit_intercept': True}
    },
    'logisticregression': {
        'class': LogisticRegression,
        'type': 'classification',
        'init_params': ['C', 'max_iter', 'fit_intercept'],
        'default_params': {'C': 1.0, 'max_iter': 1000, 'fit_intercept': True, 'solver': 'liblinear'}
    },
    'decisiontreeclassifier': {
        'class': DecisionTreeClassifier,
        'type': 'classification',
        'init_params': ['max_depth', 'min_samples_split', 'random_state'],
        'default_params': {'max_depth': None, 'min_samples_split': 2, 'random_state': 42}
    },
    'kneighborsclassifier': {
        'class': KNeighborsClassifier,
        'type': 'classification',
        'init_params': ['n_neighbors'],
        'default_params': {'n_neighbors': 5}
    },
    'kmeans': {
        'class': KMeans,
        'type': 'clustering',
        'init_params': ['n_clusters', 'random_state'],
        'default_params': {'n_clusters': 3, 'random_state': 42}
    },
    'meanshift': {
        'class': MeanShift,
        'type': 'clustering',
        'init_params': ['bandwidth'],
        'default_params': {'bandwidth': None}
    },
    'standardscaler': {
        'class': StandardScaler,
        'type': 'transformer',
        'init_params': [],
        'default_params': {}
    },
    'pca': {
        'class': PCA,
        'type': 'transformer',
        'init_params': ['n_components'],
        'default_params': {'n_components': 2}
    },
}

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


class AnalyzeData:
    """
    通用分析主类
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
        """

        # ===== 输入保存 =====
        self.df = df.copy()
        self.model_name = model.lower()
        self.random_state = random_state
        self.is_split = is_split
        self.split_ratio = split_ratio
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.is_return_model_param = is_return_model_param
        self.metrics_list = metrics_list or []
        self.is_return_model_score = is_return_model_score
        self.is_return_model_training_set = is_return_training_set
        self.is_return_model_predicting_set = is_return_model_predicting_set
        self.feature_cols_encoding = feature_cols_encoding
        self.target_col_encoding = target_col_encoding
        self.test_set = test_set

        # ===== 运行时变量初始化 =====
        self.X: Optional[pd.DataFrame] = None
        self.y: Optional[pd.Series] = None
        self.X_train: Optional[pd.DataFrame] = None
        self.X_test: Optional[pd.DataFrame] = None
        self.y_train: Optional[pd.Series] = None
        self.y_test: Optional[pd.Series] = None
        self.model = None
        self.trained_model = None
        self.predictions: Optional[pd.Series] = None
        self.scores: dict = {}
        self.model_params: dict = {}

        # ===== 内部状态 =====
        self.task_type: Optional[str] = None
        self.is_fitted_ = False

    # ------------------------------------------------------------
    # 3. 核心私有工具方法
    # ------------------------------------------------------------
    def _prepare_feature_and_target(self) -> None:
        """步骤1：根据 feature_cols / target_col 抽取 X, y"""
        logger.info("提取特征矩阵和目标列中...")
        if self.target_col:
            self.y = self.df[self.target_col].copy()
        else:
            # 监督任务必须指定 target_col
            if self.is_split and self.model_name not in ['kmeans', 'meanshift', 'standardscaler', 'pca']:
                raise ValueError("划分数据集需要目标列")

        # 特征矩阵
        if self.feature_cols:
            self.X = self.df[self.feature_cols].copy()
        else:
            exclude_cols = [self.target_col] if self.target_col else []
            self.X = self.df.drop(columns=exclude_cols, axis=1).copy()

    def _encode_categorical_variables(self) -> None:
        """步骤2：对类别型特征和目标列做编码"""
        logger.info("类别编码中...")

        if self.X is None:
            raise ValueError("特征矩阵为空")

        # -------- 特征编码 --------
        cat_features = self.X.select_dtypes(include=['object', 'category']).columns
        if len(cat_features) > 0:
            if self.feature_cols_encoding == 'onehot':
                # 训练集 one-hot
                self.X = pd.get_dummies(self.X, columns=cat_features.tolist(), drop_first=True)
                # 测试集对齐
                if self.test_set is not None:
                    self.test_set = pd.get_dummies(self.test_set, columns=cat_features.tolist(), drop_first=True)
                    for col in self.X.columns:
                        if col not in self.test_set.columns:
                            self.test_set[col] = 0
                    self.test_set = self.test_set[self.X.columns]

            elif self.feature_cols_encoding == 'label':
                self._label_encode_dataframe(self.X, cat_features)
                if self.test_set is not None:
                    self._label_encode_testset(self.test_set, cat_features)
            else:
                raise ValueError(f"不支持的特征编码方式: {self.feature_cols_encoding}")

        # -------- 目标列编码 --------
        if self.y is not None and (self.y.dtype == 'object' or self.y.dtype == 'category'):
            le = LabelEncoder()
            self.y = pd.Series(le.fit_transform(self.y), index=self.y.index, name=self.y.name)

    def _label_encode_dataframe(self, df: pd.DataFrame, columns: pd.Index) -> None:
        """label 编码辅助：训练集"""
        self.label_encoders_ = {}
        for col in columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.label_encoders_[col] = le

    def _label_encode_testset(self, test_df: pd.DataFrame, columns: pd.Index) -> None:
        """label 编码辅助：测试集，未知类别给 0"""
        for col in columns:
            if col in self.label_encoders_:
                le = self.label_encoders_[col]
                unknown_value = 0
                test_df[col] = test_df[col].astype(str).map(
                    lambda x: le.transform([x])[0] if x in le.classes_ else unknown_value
                )
            else:
                raise ValueError(f"测试集中出现训练未见的类别列: {col}")

    def _split_dataset(self) -> None:
        """步骤3：按任务类型进行数据集划分或复制"""
        logger.info("划分数据集中...")
        config = MODEL_CONFIG[self.model_name]
        task_type = config['type']

        # 聚类/变换器不需要监督式划分
        if not self.is_split or task_type in ['clustering', 'transformer']:
            self.X_train, self.y_train = self.X, self.y
            self.X_test = self.test_set.copy() if self.test_set is not None else None
            if self.X_test is not None and self.target_col in self.X_test.columns:
                self.y_test = self.X_test[self.target_col].copy()
                self.X_test = self.X_test.drop(columns=[self.target_col])
            else:
                self.y_test = None
            return

        # 监督任务：分层划分
        stratify = self.y if task_type == 'classification' else None
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y,
            test_size=1 - self.split_ratio,
            random_state=self.random_state,
            stratify=stratify
        )

    def _determine_task_type(self) -> None:
        """步骤4：根据模型名称确定任务类型"""
        if self.model_name not in MODEL_CONFIG:
            raise ValueError(f"不支持的模型: {self.model_name}")
        self.task_type = MODEL_CONFIG[self.model_name]['type']

    def _initialize_model(self) -> None:
        """步骤5：用默认或用户传入参数初始化模型"""
        logger.info(f"初始化模型: {self.model_name}")
        config = MODEL_CONFIG[self.model_name]
        model_class = config['class']
        params = config['default_params'].copy()

        # 允许实例属性覆盖默认参数
        for param in config['init_params']:
            if hasattr(self, param):
                val = getattr(self, param)
                if val is not None:
                    params[param] = val

        # 若模型支持 random_state，则强制注入，保证可复现
        if 'random_state' in model_class().get_params().keys():
            params['random_state'] = self.random_state

        self.model = model_class(**params)
        self.model_params = params

    def _train_model(self) -> None:
        """步骤6：训练模型"""
        logger.info("训练模型中...")
        config = MODEL_CONFIG[self.model_name]
        task_type = config['type']

        if self.model is None:
            raise ValueError("模型未初始化")

        # transformer 需对特征做变换
        if task_type == 'transformer':
            self.trained_model = self.model.fit(self.X_train)
            self.X_train = self.trained_model.transform(self.X_train)
            if self.X_test is not None:
                self.X_test = self.trained_model.transform(self.X_test)
        # 聚类：可选使用 y_train（半监督）
        elif task_type == 'clustering':
            if self.y_train is not None:
                self.trained_model = self.model.fit(self.X_train, self.y_train)
            else:
                self.trained_model = self.model.fit(self.X_train)
        # 回归 / 分类
        else:
            self.trained_model = self.model.fit(self.X_train, self.y_train)

        self.is_fitted_ = True

    def _predict(self) -> None:
        """步骤7：生成预测结果"""
        if not self.is_fitted_:
            return

        if self.trained_model is None:
            raise ValueError("模型未训练")

        config = MODEL_CONFIG[self.model_name]
        task_type = config['type']

        # 仅回归/分类/聚类需要 predict
        if task_type in ['regression', 'classification']:
            if self.X_test is not None:
                pred = self.trained_model.predict(self.X_test)
                self.predictions = pd.Series(pred, index=self.X_test.index, name=self.target_col)
        elif task_type == 'clustering':
            if self.X_test is not None:
                pred = self.trained_model.predict(self.X_test)
                self.predictions = pd.Series(pred, index=self.X_test.index, name='cluster')
        # transformer 无需预测

    def _compute_scores(self) -> None:
        """步骤8：计算评估指标"""
        if not self.is_return_model_score or not self.is_fitted_:
            return

        if self.trained_model is None:
            raise ValueError("模型未初始化")

        config = MODEL_CONFIG[self.model_name]
        task_type = config['type']
        available_metrics = METRICS_MAP.get(task_type, {})

        selected_metrics = self.metrics_list or list(available_metrics.keys())
        self.scores = {}

        # 回归
        if task_type == 'regression' and self.y_test is not None:
            y_pred = self.trained_model.predict(self.X_test)
            for metric in selected_metrics:
                if metric in available_metrics:
                    score = available_metrics[metric](self.y_test, y_pred)
                    self.scores[metric] = score

        # 分类
        elif task_type == 'classification' and self.y_test is not None:
            y_pred = self.trained_model.predict(self.X_test)
            for metric in selected_metrics:
                if metric in available_metrics:
                    score = available_metrics[metric](self.y_test, y_pred)
                    self.scores[metric] = score

        # 聚类
        elif task_type == 'clustering':
            if self.y_test is not None:
                pred = self.trained_model.predict(self.X_test)
                if 'ari' in selected_metrics:
                    self.scores['ari'] = adjusted_rand_score(self.y_test, pred)
            if 'silhouette' in selected_metrics and len(np.unique(self.trained_model.labels_)) > 1:
                try:
                    if self.X_train is None:
                        raise ValueError("测试集未提供")
                    self.scores['silhouette'] = silhouette_score(self.X_train, self.trained_model.labels_)
                except Exception:
                    self.scores['silhouette'] = None

    def _get_model_params(self) -> None:
        """步骤9：收集最终模型参数"""
        if self.is_return_model_param and self.trained_model is not None:
            self.model_params = self.trained_model.get_params()

    # ------------------------------------------------------------
    # 4. 主入口
    # ------------------------------------------------------------
    def run(self) -> Dict[str, Any]:
        """
        统一执行入口
        返回 dict，按需包含：
            - scores: 评估指标
            - model_params: 模型超参数
            - X_train, y_train, X_test, y_test: 训练/测试集
            - predictions: 预测结果
            - trained_model: 已训练模型
            - task_type: 任务类型
        """
        try:
            self._determine_task_type()
            self._prepare_feature_and_target()
            self._encode_categorical_variables()
            self._split_dataset()
            self._initialize_model()
            self._train_model()
            self._predict()
            self._compute_scores()
            if self.is_return_model_param:
                self._get_model_params()

            # 组装返回结果
            result = {}
            if self.is_return_model_score:
                result['scores'] = self.scores
            if self.is_return_model_param:
                result['model_params'] = self.model_params
            if self.is_return_model_training_set:
                result['X_train'] = self.X_train
                result['y_train'] = self.y_train
                result['X_test'] = self.X_test
                result['y_test'] = self.y_test
            if self.is_return_model_predicting_set:
                result['predictions'] = self.predictions
            result['trained_model'] = self.trained_model
            result['task_type'] = self.task_type

            logger.info("分析流程执行完成。")
            return result

        except Exception as e:
            logger.error(f"分析流程执行失败: {str(e)}")
            raise