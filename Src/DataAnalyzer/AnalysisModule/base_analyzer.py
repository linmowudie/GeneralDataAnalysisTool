from typing import Dict, List, Optional, Union, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import logging
import sys
import os

# 导入性能计时装饰器
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from PythonScripts.running_timer import run_timer

logger = logging.getLogger(__name__)

class BaseAnalyzer:
    """
    分析器基类
    包含所有子模块共用的方法和属性
    """

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
        model_params: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化分析器基类
        
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
        self.model_params_input = model_params or {}  # 保存传入的额外模型参数

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

    @run_timer
    def _prepare_feature_and_target(self) -> None:
        """步骤1：根据 feature_cols / target_col 抽取 X, y"""
        logger.info("提取特征矩阵和目标列中...")
        
        if self.target_col:
            self.y = self.df[self.target_col].copy()
        elif self.task_type in ['regression', 'classification']:
            # 监督任务必须指定目标列
            raise ValueError(f"{self.task_type}任务必须指定目标列")

        # 特征矩阵
        if self.feature_cols:
            self.X = self.df[self.feature_cols].copy()
        else:
            exclude_cols = [self.target_col] if self.target_col else []
            self.X = self.df.drop(columns=exclude_cols, axis=1).copy()

    @run_timer
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

    @run_timer
    def _get_model_params(self) -> None:
        """获取最终模型参数"""
        if self.is_return_model_param and self.trained_model is not None:
            try:
                self.model_params = self.trained_model.get_params()
            except:
                self.model_params = {}

    @run_timer
    def _setup_result(self) -> Dict[str, Any]:
        """
        组装返回结果
        """
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

        return result