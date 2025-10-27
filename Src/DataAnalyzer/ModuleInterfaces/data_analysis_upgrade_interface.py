#数据分析接口升级版

import pandas as pd
import logging

from typing import Dict, List, Optional, Union, Any
from ..AnalysisUpgrade.Cores.base_analyzer import BaseAnalyzer
from ..AnalysisUpgrade.Cores.base_factory import BaseFactory

logger = logging.getLogger(__name__)

class DataAnalysisUpgrade():
    """
    新版数据模块接口，负责传入参数、模糊参数检测和调用新版数据模块
    """

    def __init__(
        self,
        df: pd.DataFrame,
        learn_type: str,
        model_type: str,
        model: str,
        random_state: int = 42,
        is_split: bool = True,
        split_ratio: float = 0.8,
        feature_cols: Optional[List[str]] = None,
        target_col: Optional[str] = None,
        metrics_list: Optional[List[str]] = None,
        is_return_model_score: bool = True,
        is_return_training_set: bool = False,
        feature_cols_encoding: str = 'onehot',
        target_col_encoding: str = 'label',
        test_set: Optional[pd.DataFrame] = None,
        model_params: Optional[Dict[str, Any]] = None
    ):
        """
        初始化数据分析模块

        :param df: 待分析的数据集
        :param learn_type: 学习类型，如 'ML'（机器学习）或 'DL'（深度学习）
        :param model_type: 模型类别，如 'classification'、'regression'、'clustering'
        :param model: 模型名称（如 'lr', 'rf', 'xgb', 'svm' 等）
        :param random_state: 随机种子，用于保证结果可复现
        :param is_split: 是否进行数据集分割（训练/测试）
        :param split_ratio: 数据集分割比例（如 0.8 表示 80% 训练，20% 测试）
        :param feature_cols: 特征列名称列表，若为 None 则自动排除目标列后所有列
        :param target_col: 目标列名称
        :param metrics_list: 评价指标列表（如 ['accuracy', 'precision', 'f1']）
        :param is_return_model_score: 是否返回模型得分（评估指标结果）
        :param is_return_training_set: 是否返回训练集
        :param feature_cols_encoding: 特征列中类别变量的编码方式（如 'onehot', 'label'）
        :param target_col_encoding: 目标列编码方式（分类任务中使用，如 'label'）
        :param test_set: 测试集数据集，默认为 None
        :param model_params: 模型参数字典，用于覆盖默认参数
        """
        self.df = df.copy()
        self.learn_type = learn_type.lower()
        self.model_type = model_type.lower()
        self.model_name = model.lower()
        self.random_state = random_state
        self.is_split = is_split
        self.split_ratio = split_ratio
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.metrics_list = metrics_list or []
        self.is_return_model_score = is_return_model_score
        self.is_return_model_training_set = is_return_training_set
        self.feature_cols_encoding = feature_cols_encoding
        self.target_col_encoding = target_col_encoding
        self.test_set = test_set  
        self.model_params = model_params or {}
        self.result = None

    def _validate_params(self):
        """
        验证初始化参数的合法性，检查是否为空、类型错误或逻辑矛盾。
        若检测到问题，记录日志并抛出 ValueError。
        """
        logger.info("开始验证输入参数...")

        # 1. 检查数据集 df
        if self.df is None:
            logger.error("数据集 (df) 不能为 None")
            raise ValueError("数据集 (df) 不能为 None")
        if not isinstance(self.df, pd.DataFrame):
            logger.error(f"数据集 (df) 必须是 pandas.DataFrame 类型，当前类型为 {type(self.df)}")
            raise ValueError(f"数据集 (df) 必须是 pandas.DataFrame 类型，当前类型为 {type(self.df)}")
        if self.df.empty:
            logger.error("数据集 (df) 不能为空（无行数据）")
            raise ValueError("数据集 (df) 不能为空")

        # 2. 检查 learn_type
        valid_learn_types = ['ml', 'dl']
        if not self.learn_type:
            logger.error("学习类型 (learn_type) 不能为空")
            raise ValueError("学习类型 (learn_type) 不能为空")
        if not isinstance(self.learn_type, str):
            logger.error(f"学习类型 (learn_type) 必须是字符串类型，当前类型为 {type(self.learn_type)}")
            raise ValueError(f"学习类型 (learn_type) 必须是字符串类型，当前类型为 {type(self.learn_type)}")
        if self.learn_type not in valid_learn_types:
            logger.error(f"学习类型 (learn_type) 不支持 '{self.learn_type}'，支持: {valid_learn_types}")
            raise ValueError(f"学习类型 (learn_type) 不支持 '{self.learn_type}'，支持: {valid_learn_types}")
        
        # 3. 检查 model_type
        valid_model_types = ['classification', 'regression', 'clustering', 'dimensionality_reduction']
        if not self.model_type:
            logger.error("模型类别 (model_type) 不能为空")
            raise ValueError("模型类别 (model_type) 不能为空")
        if not isinstance(self.model_type, str):
            logger.error(f"模型类别 (model_type) 必须是字符串类型，当前类型为 {type(self.model_type)}")
            raise ValueError(f"模型类别 (model_type) 必须是字符串类型，当前类型为 {type(self.model_type)}")
        if self.model_type not in valid_model_types:
            logger.error(f"模型类别 (model_type) 不支持 '{self.model_type}'，支持: {valid_model_types}")
            raise ValueError(f"模型类别 (model_type) 不支持 '{self.model_type}'，支持: {valid_model_types}")
        
        # 4. 检查模型名称 model_name
        if not self.model_name:
            logger.error("模型名称 (model) 不能为空")
            raise ValueError("模型名称 (model) 不能为空")
        if not isinstance(self.model_name, str):
            logger.error(f"模型名称 (model) 必须是字符串类型，当前类型为 {type(self.model_name)}")
            raise ValueError(f"模型名称 (model) 必须是字符串类型，当前类型为 {type(self.model_name)}")

        # 3. 检查 random_state
        if not isinstance(self.random_state, int):
            logger.warning("random_state 应为整数，尝试转换...")
            try:
                self.random_state = int(self.random_state)
                logger.info(f"random_state 已转换为整数: {self.random_state}")
            except (ValueError, TypeError):
                logger.error("random_state 无法转换为整数")
                raise ValueError("random_state 必须是一个整数或可转为整数的值")

        # 4. 检查 is_split
        if not isinstance(self.is_split, bool):
            logger.warning("is_split 应为布尔值，尝试转换...")
            self.is_split = bool(self.is_split)

        # 5. 检查 split_ratio（仅在 is_split=True 时需要）
        if self.is_split:
            if not isinstance(self.split_ratio, (float, int)) or not (0.0 < self.split_ratio < 1.0):
                logger.error(f"split_ratio 必须是 (0, 1) 范围内的浮点数，当前值为 {self.split_ratio}")
                raise ValueError("split_ratio 必须是 (0, 1) 范围内的浮点数，表示训练集占比")
        else:
            if self.test_set is None:
                logger.warning("is_split=False 且 test_set 未提供，将使用 df 作为测试集进行预测")

        # 6. 检查 target_col（关键列）
        if not self.target_col:
            logger.error("目标列 (target_col) 不能为空")
            raise ValueError("目标列 (target_col) 不能为空")
        if self.target_col not in self.df.columns:
            logger.error(f"目标列 '{self.target_col}' 不存在于数据集中")
            raise ValueError(f"目标列 '{self.target_col}' 不存在于数据集中")

        # 7. 检查 feature_cols
        if self.feature_cols is None:
            # 自动排除 target_col
            self.feature_cols = [col for col in self.df.columns if col != self.target_col]
            logger.info(f"未指定 feature_cols，自动使用除 '{self.target_col}' 外的所有列，共 {len(self.feature_cols)} 列")
        else:
            if not isinstance(self.feature_cols, list):
                logger.error(f"feature_cols 必须是字符串列表，当前类型为 {type(self.feature_cols)}")
                raise ValueError("feature_cols 必须是字符串列表")
            invalid_cols = [col for col in self.feature_cols if col not in self.df.columns]
            if invalid_cols:
                logger.error(f"以下特征列不存在于数据集中: {invalid_cols}")
                raise ValueError(f"以下特征列不存在于数据集中: {invalid_cols}")

        # 8. 检查 metrics_list
        if self.metrics_list is not None and not isinstance(self.metrics_list, list):
            logger.error(f"metrics_list 必须是列表类型，当前类型为 {type(self.metrics_list)}")
            raise ValueError("metrics_list 必须是列表类型")

        # 9. 检查 test_set
        if self.test_set is not None:
            if not isinstance(self.test_set, pd.DataFrame):
                logger.error(f"test_set 必须是 pandas.DataFrame 类型，当前类型为 {type(self.test_set)}")
                raise ValueError("test_set 必须是 pandas.DataFrame 类型")
            if self.test_set.empty:
                logger.error("提供的 test_set 为空")
                raise ValueError("test_set 不能为空")

        # 10. 检查 model_params
        if self.model_params is not None and not isinstance(self.model_params, dict):
            logger.error(f"model_params 必须是字典类型，当前类型为 {type(self.model_params)}")
            raise ValueError("model_params 必须是字典类型")

        # 11. 检查编码方式
        valid_feature_encodings = ['onehot', 'label', 'ordinal']
        if self.feature_cols_encoding not in valid_feature_encodings:
            logger.error(f"feature_cols_encoding 不支持 '{self.feature_cols_encoding}'，支持: {valid_feature_encodings}")
            raise ValueError(f"feature_cols_encoding 不支持 '{self.feature_cols_encoding}'，支持: {valid_feature_encodings}")

        valid_target_encodings = ['label', 'onehot', 'none']
        if self.target_col_encoding not in valid_target_encodings:
            logger.error(f"target_col_encoding 不支持 '{self.target_col_encoding}'，支持: {valid_target_encodings}")
            raise ValueError(f"target_col_encoding 不支持 '{self.target_col_encoding}'，支持: {valid_target_encodings}")

        logger.info("所有参数验证通过 ✅")


    def analyze(self):
        """
        分析数据，使用两级路由机制创建分析器实例
        """
        # 首先验证参数
        self._validate_params()

        # 使用两级路由机制创建分析器实例
        analyzer_instance = AnalyzerFactory.create_analyzer_full(
            learn_type=self.learn_type,  # 第一级路由：选择机器学习或深度学习工厂
            model_type=self.model_type,  # 第二级路由：指定模型类型（分类、回归等）
            model=self.model_name        # 模型名称
        )
        
        # 如果完整路由失败，回退到原来的方式
        if analyzer_instance is None:
            analyzer_instance = AnalyzerFactory.create_analyzer_by_task_and_model(
                task_type=self.model_type,
                model_name=self.model_name
            )
        
        if analyzer_instance is None:
            logger.error(f"无法创建分析器: {self.learn_type}.{self.model_type}.{self.model_name}")
            raise ValueError(f"不支持的模型类型: {self.learn_type}.{self.model_type}.{self.model_name}")

        # 调用分析器的analyzer方法
        self.result = analyzer_instance.analyzer(
            df=self.df,
            learn_type=self.learn_type,
            model_type=self.model_type,
            model=self.model_name,
            random_state=self.random_state,
            is_split=self.is_split,
            split_ratio=self.split_ratio,
            feature_cols=self.feature_cols,
            target_col=self.target_col,
            metrics_list=self.metrics_list,
            is_return_model_score=self.is_return_model_score,
            is_return_training_set=self.is_return_model_training_set,
            feature_cols_encoding=self.feature_cols_encoding,
            target_col_encoding=self.target_col_encoding,
            test_set=self.test_set,
            model_params=self.model_params
        )

        return self.result