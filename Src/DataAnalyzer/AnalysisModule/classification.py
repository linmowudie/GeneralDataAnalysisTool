from typing import Dict, List, Optional, Union, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import logging
import sys
import os

# 导入性能计时装饰器
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from PythonScripts.running_timer import run_timer

from .base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

class Classification(BaseAnalyzer):
    """
    分类分析模块
    专门处理分类任务的分析器
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
        初始化分类分析器
        
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
        super().__init__(
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

        # ===== 内部状态 =====
        self.task_type: str = 'classification'
        self.is_fitted_ = False

    def _split_dataset(self) -> None:
        """步骤3：按任务类型进行数据集划分或复制"""
        logger.info("划分数据集中...")

        # 分类任务：分层划分
        if self.is_split and self.y is not None:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                self.X, self.y,
                test_size=1 - self.split_ratio,
                random_state=self.random_state,
                stratify=self.y
            )
        else:
            # 不划分数据集时，训练集和测试集都使用完整数据
            self.X_train, self.y_train = self.X, self.y
            self.X_test, self.y_test = self.X, self.y

    def _initialize_model(self) -> None:
        """步骤4：用默认或用户传入参数初始化模型"""
        logger.info(f"初始化分类模型: {self.model_name}")
        from .analyzer import MODEL_CONFIG
        
        config = MODEL_CONFIG[self.model_name]
        model_class = config['class']
        params = config['default_params'].copy()

        # 允许传入的额外参数覆盖默认参数
        for param, value in self.model_params_input.items():
            params[param] = value

        # 若模型支持 random_state，则强制注入，保证可复现
        try:
            if 'random_state' in model_class().get_params().keys():
                params['random_state'] = self.random_state
        except:
            pass  # 某些模型可能不支持 get_params()

        self.model = model_class(**params)
        self.model_params = params

    def _train_model(self) -> None:
        """步骤5：训练模型"""
        logger.info("训练分类模型中...")
        
        if self.model is None:
            raise ValueError("模型未初始化")

        self.trained_model = self.model.fit(self.X_train, self.y_train)
        self.is_fitted_ = True

    def _predict(self) -> None:
        """步骤6：生成预测结果"""
        if not self.is_fitted_:
            return

        if self.trained_model is None:
            raise ValueError("模型未训练")

        # 分类任务需要 predict
        if self.X_test is not None:
            pred = self.trained_model.predict(self.X_test)
            # 确保预测结果与测试集索引一致
            self.predictions = pd.Series(pred, index=self.X_test.index, name='predictions')

    def _compute_scores(self) -> None:
        """步骤7：计算评估指标"""
        if not self.is_return_model_score or not self.is_fitted_:
            return

        if self.trained_model is None:
            raise ValueError("模型未初始化")

        # 分类任务的评估指标
        classification_metrics = {
            'accuracy': accuracy_score,
        }

        selected_metrics = self.metrics_list or list(classification_metrics.keys())
        self.scores = {}

        # 确保在计算指标时y_test和predictions具有一致的索引
        if self.y_test is not None and self.predictions is not None:
            # 获取共同索引
            common_index = self.y_test.index.intersection(self.predictions.index)
            if len(common_index) > 0:
                y_test_aligned = self.y_test.loc[common_index]
                predictions_aligned = self.predictions.loc[common_index]
                
                for metric in selected_metrics:
                    if metric in classification_metrics:
                        score = classification_metrics[metric](y_test_aligned, predictions_aligned)
                        self.scores[metric] = score
            else:
                logger.warning("y_test和predictions没有共同索引，无法计算评估指标")

    def _get_model_params(self) -> None:
        """步骤8：收集最终模型参数"""
        if self.is_return_model_param and self.trained_model is not None:
            try:
                self.model_params = self.trained_model.get_params()
            except:
                self.model_params = {}

    def run(self) -> Dict[str, Any]:
        """
        执行分类分析
        """
        try:
            logger.info("开始执行分类分析...")
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
            result = self._setup_result()

            logger.info("分类分析执行完成。")
            return result

        except Exception as e:
            logger.error(f"分类分析执行失败: {str(e)}")
            raise