"""
backend/Models/analysis/data_analyzer.py
数据分析模块统一接口（原 Engine/ModuleInterfaces/data_analysis.py 迁入）

该模块提供数据分析功能的统一接口，整合了各种分析方法，
包括描述性统计、相关性分析等。
"""

import pandas as pd
import logging
from typing import List, Optional, Union, Dict, Any

logger = logging.getLogger(__name__)


class DataAnalyzer:
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
        model_params: Optional[Dict[str, Any]] = None
    ):
        """
        初始化数据分析模块

        :param df: 待分析的数据集
        :param model: 模型名称（如 'lr', 'rf', 'xgb', 'svm' 等）
        :param random_state: 随机种子，用于保证结果可复现
        :param is_split: 是否进行数据集分割（训练/测试）
        :param split_ratio: 数据集分割比例（如 0.8 表示 80% 训练，20% 测试）
        :param feature_cols: 特征列名称列表，若为 None 则自动排除目标列后所有列
        :param target_col: 目标列名称
        :param is_return_model_param: 是否返回模型参数（如超参数）
        :param metrics_list: 评价指标列表（如 ['accuracy', 'precision', 'f1']）
        :param is_return_model_score: 是否返回模型得分（评估指标结果）
        :param is_return_training_set: 是否返回训练集
        :param is_return_model_predicting_set: 是否返回模型预测集
        :param feature_cols_encoding: 特征列中类别变量的编码方式（如 'onehot', 'label'）
        :param target_col_encoding: 目标列编码方式（分类任务中使用，如 'label'）
        :param test_set: 测试集数据集，默认为 None
        :param model_params: 模型参数字典，用于覆盖默认参数
        """
        # 执行输入验证
        self._validate_inputs(df, target_col, feature_cols)

        # 保存原始参数
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
        self.model_params = model_params or {}

        logger.info("初始化数据分析模块完成")

    @staticmethod
    def _validate_inputs(
        df: Union[pd.DataFrame, None],
        target_col: Optional[str],
        feature_cols: Optional[List[str]]
    ) -> None:
        """静态方法：验证输入参数的合法性"""
        if df is None:
            logger.error("数据集不能为空")
            raise ValueError("数据集不能为空")

        if df.empty:
            logger.warning("数据集为空")
            raise ValueError("数据集为空")

        if target_col is not None and target_col not in df.columns:
            msg = f"目标列 '{target_col}' 不存在于数据集列中，可用列：{list(df.columns)}"
            logger.error(msg)
            raise ValueError(msg)

        if feature_cols is not None:
            missing_cols = [col for col in feature_cols if col not in df.columns]
            if missing_cols:
                msg = f"以下特征列不存在于数据集中: {missing_cols}"
                logger.error(msg)
                raise ValueError(msg)

    def analyze(self) -> Dict[str, Any]:
        """执行数据分析并返回结果"""
        from .analyzer import analyze_data

        result = analyze_data(
            df=self.df,
            model=self.model_name,
            random_state=self.random_state,
            is_split=self.is_split,
            split_ratio=self.split_ratio,
            feature_cols=self.feature_cols,
            target_col=self.target_col,
            is_return_model_param=self.is_return_model_param,
            metrics_list=self.metrics_list,
            is_return_model_score=self.is_return_model_score,
            is_return_training_set=self.is_return_model_training_set,
            is_return_model_predicting_set=self.is_return_model_predicting_set,
            feature_cols_encoding=self.feature_cols_encoding,
            target_col_encoding=self.target_col_encoding,
            test_set=self.test_set,
            model_params=self.model_params
        )
        return result
