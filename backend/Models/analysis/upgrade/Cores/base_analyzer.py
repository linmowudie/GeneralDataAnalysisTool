from abc import ABC, abstractmethod
from pyclbr import Class
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import logging
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os
import time
from pathlib import Path

from sklearn.utils import validation

logger = logging.getLogger(__name__)

class BaseAnalyzer(ABC):
    """
    数据分析器基类（抽象基类）

    所有具体分析器（如分类、回归、聚类）必须继承此类并实现抽象方法。
    本类提供统一的模型实例化、编码、划分、评估等通用能力，并确保：
      - 模型只被实例化一次（通过 instantiate_model）
      - 子类不得在自身方法中直接导入或创建模型实例
      - 所有流程由 analyzer 驱动，保证一致性

    子类应在以下方法中实现任务特定逻辑：
        - load_params
        - validate_params
        - preprocess
        - train
        - postprocess
        - get_feature_importance
        - save_model_artifacts
        - predict
        - get_default_metrics
        - build_result

    方法职责说明：
        - postprocess: 负责模型存储和训练集/测试集存储到 TempStorage 供可视化调用
        - save_model_artifacts: 将模型保存至 ModelOutput 目录，该方法在模型后处理完后调用
    """

    def __init__(self):
        """
        初始化分析器。子类可扩展初始化逻辑，但不应在此处实例化模型。
        """
        self._model_instance = None  # 内部缓存已实例化的模型（仅供 analyzer 使用）
        self._fitted_encoders = {}   # 用于保存训练中使用的编码器（如 LabelEncoder）

    # ==========================================
    # 抽象方法 (Abstract Methods)
    # 子类必须实现这些方法
    # ==========================================


    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, bool]:
        """
        校验加载的参数是否合法（如必要字段是否存在、类型是否正确）

        ⚠️ 覆写要求：
          - 必须对关键字段（如 feature_cols, target_col）进行存在性和类型检查
          - 若校验失败，抛出 ValueError
          - 不得在此方法中修改参数或实例化模型
          - 需要检测`analyzer`的model_params字段是否有输入，如果有则将{"input_params":True}添加至结果,
            再经过检验输入参数与load_params返回的参数对，替换默认参数含有的键名，没有的直接过滤掉

        参数:
            params (Dict[str, Any]): 参数字典

        返回:
            bool: 校验通过返回 True

        异常:
            ValueError: 参数不合法时抛出
        """
        pass

    @abstractmethod
    def replace_params(self, default_params: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        替换默认参数

        ⚠️ 腹泻要求：
          - 禁止再次实例化或者调用instantiate_model实例化模型

        参数:
            default_params (Dict[str, Any]): 默认参数字典
            params (Dict[str, Any]): 输入参数字典

        返回:
            Dict[str, Any]: 替换和过滤后的参数字典
        """
        pass

    @abstractmethod
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> tuple:
        """
        执行任务特定的数据预处理（如特征工程、缺失值处理、标准化等），这个是对清洗模块的保证步骤，用于校正数据，不实现问题也不大

        ⚠️ 覆写要求：
          - 可调用基类的 fill_missing_values、feature_set_encoding 等方法
          - 必须返回处理后的 (X_processed, y_processed)
          - 若 y 为 None（如聚类），可只返回 X_processed
          - 只可以再次方法中实例化转换器的模型，用于对数据预处理

        参数:
            X (pd.DataFrame): 特征数据
            y (Optional[pd.Series]): 目标数据（可选）

        返回:
            tuple: 预处理后的 (X, y) 数据
        """
        pass

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """
        使用训练数据拟合模型

        ⚠️ 覆写要求：
          - 必须使用 self._model_instance（已在 analyzer 中实例化）
          - 调用 model.fit(...) 完成训练
          - 返回训练后的模型对象（通常为 self._model_instance）
          - 禁止在此方法中重新实例化模型！

        参数:
            X_train (pd.DataFrame): 训练特征
            y_train (Optional[pd.Series]): 训练标签

        返回:
            Any: 训练完成的模型对象
        """
        pass

    @abstractmethod
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> bool:
        """
        训练后处理，如特征重要性提取、模型解释、中间结果保存等

        ⚠️ 覆写要求：
          - 可调用 get_feature_importance 等方法
          - 必须实现模型存储和训练集/测试集存储到 TempStorage 供可视化调用
          - 直接返回 bool 值，因为结果不需要它参与构建
          - 不得修改模型或重新训练

        参数:
            model (Any): 训练完成的模型
            X (pd.DataFrame): 特征数据（通常为训练集）
            y (Optional[pd.Series]): 标签数据

        返回:
            bool: 后处理是否成功
        """
        pass

    @abstractmethod
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        提取模型的特征重要性（如随机森林的 feature_importances_）

        ⚠️ 覆写要求：
          - 若模型不支持重要性，返回空字典或全 0
          - 返回格式：{'feature_name': importance_value}

        参数:
            model (Any): 训练完成的模型

        返回:
            Dict[str, float]: 特征重要性字典
        """
        pass

    @abstractmethod
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """
        保存模型及相关产物（模型文件、编码器、特征列表等）到 ModelOutput 目录

        ⚠️ 覆写要求：
          - 使用 joblib/pickle 保存 model
          - 同时保存编码器（self._fitted_encoders）、特征名等元数据
          - 将模型保存至 ModelOutput 目录
          - 返回保存是否成功

        参数:
            model (Any): 模型对象
            filepath (str): 保存路径（不含扩展名）

        返回:
            bool: 是否成功
        """
        pass

    @abstractmethod
    def predict(self, model: Any, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """
        使用训练好的模型进行预测

        ⚠️ 覆写要求：
          - 调用 model.predict(X)
          - 若为分类任务且需解码，使用 self._fitted_encoders 还原原始标签
          - 返回 pd.Series 或 pd.DataFrame，index 与 X 一致

        参数:
            model (Any): 训练好的模型
            X (pd.DataFrame): 预测数据

        返回:
            Union[pd.Series, pd.DataFrame]: 预测结果
        """
        pass

    @abstractmethod
    def get_default_metrics(self, model_type: str) -> List[str]:
        """
        根据 model_type 返回默认评估指标列表

        ⚠️ 覆写要求：
          - 从配置文件读取或返回硬编码默认值
          - 如分类返回 ["accuracy", "f1_score"]，回归返回 ["mse", "r2_score"]

        参数:
            model_type (str): 模型类型（如 "classification"）

        返回:
            List[str]: 默认指标列表
        """
        pass

    @abstractmethod
    def build_result(self, 
                     model: Any,
                     model_score: Optional[Dict[str, float]],
                     train_set_path: str,
                     test_set_path: str,
                     feature_cols: List[str],
                     encoding_method: Dict[str, str],
                     feature_importance: Dict[str, float],
                     model_path: str
                     ) -> Dict[str, Any]:
        """
        构建并返回最终结果字典

        ⚠️ 覆写要求：
          - 必须返回包含所有分析结果的字典
          - 应包括模型评分、特征重要性、后处理结果等
          - 可以根据具体任务类型添加额外的返回字段

        参数:
            model (Any): 训练完成的模型
            model_score (Optional[Dict[str, float]]): 模型评估得分
            train_set_path (str): 训练集数据存储路径
            test_set_path (str): 测试集数据存储路径
            feature_cols (List[str]): 特征列
            encoding_method (Dict[str, str]): 特征编码方法
            feature_importance (Dict[str, float]): 特征重要性
            model_path (str): 模型存储路径

        返回:
            Dict[str, Any]: 完整的分析结果
            key: value
            {
                "model": object,
                "model_score": dict,
                "train_set_path": str,
                "test_set_path": str,
                "feature_cols": list[str],
                "encodeing_method": Dict[str, str],
                "feature_importance": Dict[str, float],
                "model_path": str
            }
            
        """
        pass

    # ==========================================
    # 模板方法 (Template Method)
    # 定义标准流程，子类不应重写
    # ==========================================

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
        执行完整分析流程的核心方法（模板方法模式）

        ⚠️ 该方法为模板方法，定义了标准的分析流程，子类不应重写此方法：
          加载参数 -> 校验参数 -> 参数替换 -> 预处理 -> 划分数据 ->
          实例化模型 -> 训练 -> 预测与评估 -> 后处理 -> 构建返回结果

        ⚠️ 子类在 analyzer 内部以调用 instantiate_model 的方式创建模型！
            除非遇到无法解决的bug则自定义一个与以上方法类似的放法替换实例化模型的功能
            实例化后的模型通过 self.model_instance 获取

        参数:
            df (pd.DataFrame): 输入的数据集，用于训练和测试模型
            learn_type (str): 学习类型（如 "supervised", "unsupervised"）
            model_type (str): 模型类型（如 "classification", "regression", "clustering"）
            model (str): 具体的模型名称（如 "randomforestclassifier", "svc"）
            random_state (int): 随机种子，用于保证结果的可重现性，默认为 42
            is_split (bool): 是否需要划分数据集，默认为 True
            split_ratio (float): 数据集划分比例（测试集占比），默认为 0.2
            feature_cols (Optional[List[str]]): 指定用作特征的列名列表，如果为 None 则使用除目标列外的所有列
            target_col (Optional[str]): 目标列名，对于无监督学习可以为 None
            metrics_list (Optional[List[str]]): 评估指标列表，如果为 None 则使用默认指标
            is_return_model_score (bool): 是否返回模型评估得分，默认为 True
            feature_cols_encoding (str): 特征列编码方式，可选 "auto", "onehot", "label", "none"，默认为 "auto"
            target_col_encoding (str): 目标列编码方式，可选 "auto", "label", "none"，默认为 "auto"
            test_set (Optional[pd.DataFrame]): 外部测试数据集，如果提供则不进行数据集划分
            model_params (Optional[Dict[str, Any]]): 模型超参数字典，如果为 None 则使用默认参数

        返回:
            Dict[str, Any]: 包含模型、评估得分、特征重要性、后处理结果等的字典
            
        异常:
            ValueError: 当参数校验失败或关键数据为空时抛出
        """
        # 本地参数定义
        params_result: Dict[str, Any] = {} # 从配置文件加载的参数
        model_info: List[str] = [] # 模型基本信息，包含模型名称、模块名、类型
        default_model_params: Dict[str, Any] = {} # 训练模型的基本配置
        validation_result:Dict[str, Any] = {} # 参数校验结果,内部包含对各个参数的调整信息
        final_model_params: Dict[str, Any] = {} # 最终的模型参数
        params: Dict[str, Any] = {}
        X: Optional[pd.DataFrame] = None  # 特征数据
        y: Optional[pd.Series] = None  # 目标数据
        X_processed: Optional[pd.DataFrame] = None  # 预处理后的特征数据
        y_processed: Optional[pd.Series] = None  # 预处理后的目标数据
        X_train: Optional[pd.DataFrame] = None  # 训练特征数据
        y_train: Optional[pd.Series] = None  # 训练目标数据
        X_test: Optional[pd.DataFrame] = None  # 测试特征数据
        y_test: Optional[pd.Series] = None  # 测试目标数据
        trained_model: Any = None  # 训练后的模型
        model_score: Optional[Dict[str, float]] = None  # 模型评估得分
        postprocess_result: bool = False  # 后处理结果
        feature_importance: Dict[str, float] = {}  # 特征重要性
        result: Dict[str, Any] = {}  # 最终结果
        encoding_method: Dict[str, str] = {}  # 编码方法
        train_set_path: str = ""  # 训练集路径
        test_set_path: str = ""  # 测试集路径
        model_path: str = ""  # 模型路径

        # 1. 加载模型参数
        # 从配置文件中加载指定模型的默认参数和模型信息
        params_result = self.load_model_params(model, model_type)
        model_info = params_result["model_info"]
        default_model_params = params_result["default_model_params"]
        
        # 2. 校验参数
        # 调用子类实现的 validate_params 方法校验所有输入参数的有效性
        validation_result = self.validate_params({
            "learn_type": learn_type,
            "model_type": model_type,
            "model": model,
            "random_state": random_state,
            "is_split": is_split,
            "split_ratio": split_ratio,
            "feature_cols": feature_cols,
            "target_col": target_col,
            "metrics_list": metrics_list,
            "is_return_model_score": is_return_model_score,
            "feature_cols_encoding": feature_cols_encoding,
            "target_col_encoding": target_col_encoding,
            "test_set": test_set,
            "model_params": model_params,
            "model_info": model_info,
            "default_model_params": default_model_params
        })
        # 检查参数校验是否通过
        if not validation_result.get("is_valid", False):
            raise ValueError("参数校验失败")

        # 3. 参数替换
        # 如果用户提供了自定义模型参数，则替换默认参数
        if model_params and validation_result.get("input_params"):
            final_model_params = self.replace_params(default_model_params, model_params)
        else:
            final_model_params = default_model_params

        # 4. 更新参数
        # 使用校验后的参数更新局部变量
        params = validation_result["params"]
        random_state = params.get("random_state", random_state)
        is_split = params.get("is_split", is_split)
        split_ratio = params.get("split_ratio", split_ratio)
        feature_cols = params.get("feature_cols", feature_cols)
        target_col = params.get("target_col", target_col)
        metrics_list = params.get("metrics_list", metrics_list)
        is_return_model_score = params.get("is_return_model_score", is_return_model_score)
        feature_cols_encoding = params.get("feature_cols_encoding", feature_cols_encoding)
        target_col_encoding = params.get("target_col_encoding", target_col_encoding)
        
        # 5. 准备数据
        # 从原始数据中提取特征和目标数据
        X, y = self._prepare_data(df, feature_cols, target_col)
        
        # 6. 预处理数据
        # 对特征和目标数据进行预处理（如编码、缺失值处理等）
        if X is not None:
            X_processed, y_processed = self.preprocess(X, y)
        else:
            raise ValueError("特征数据不能为空")
        
        # 7. 划分数据集
        # 根据配置划分训练集和测试集
        if X_processed is not None:
            X_train, X_test, y_train, y_test = self._split_dataset(
                X_processed, y_processed, df, is_split, test_set, 
                split_ratio, feature_cols, target_col
            )
        else:
            raise ValueError("处理后的特征数据不能为空")
            
        # 8. 实例化模型
        # 根据模型名称和参数实例化具体的模型对象
        self._model_instance = self.instantiate_model(model, random_state, final_model_params)
        
        # 9. 训练模型
        # 使用训练数据训练模型
        if X_train is not None:
            trained_model = self.train(X_train, y_train)
        else:
            raise ValueError("训练数据不能为空")
        
        # 10. 评估模型
        # 如果需要返回模型得分且测试数据存在，则进行模型评估
        if is_return_model_score and X_test is not None and y_test is not None:
            if metrics_list is None:
                metrics_list = self.get_default_metrics(model_type)
            model_score = self.evaluate_model(trained_model, X_test, y_test, metrics_list)
            
        # 11. 后处理
        # 对训练完成的模型进行后处理（如特征重要性提取等）
        if X_train is not None:
            postprocess_success = self.postprocess(trained_model, X_train, y_train)
            if not postprocess_success:
                logger.warning("后处理执行失败")
        else:
            raise ValueError("训练数据不能为空")
        
        # 12. 特征重要性
        # 提取模型的特征重要性信息
        feature_importance = self.get_feature_importance(trained_model)

        # 13. 保存模型
        # 保存训练好的模型到指定路径
        model_path = f"ModelOutput/自动保存/model_{int(time.time())}"
        save_success = self.save_model_artifacts(trained_model, model_path)
        if not save_success:
            logger.warning("模型保存失败")

        # 14. 构建结果
        # 将所有结果组合成最终的返回字典
        result = self.build_result(
            model=trained_model,
            model_score=model_score,
            train_set_path=train_set_path,
            test_set_path=test_set_path,
            feature_cols=feature_cols if feature_cols is not None else [],
            encoding_method=encoding_method,
            feature_importance=feature_importance,
            model_path=model_path
        )
        return result

    def _prepare_data(self, df: pd.DataFrame, feature_cols: Optional[List[str]], 
                      target_col: Optional[str]) -> tuple:
        """
        准备特征和目标数据

        参数:
            df (pd.DataFrame): 原始数据
            feature_cols (Optional[List[str]]): 特征列名列表
            target_col (Optional[str]): 目标列名

        返回:
            tuple: (X, y) 特征和目标数据
        """
        # 数据集检查
        if df is None:
            raise ValueError("数据集为空")

        if feature_cols:
            X_data = df[feature_cols].copy()
            if isinstance(X_data, pd.Series):
                X: pd.DataFrame = X_data.to_frame()
            else:
                X = X_data
        else:
            if target_col:
                X_data = df.drop(columns=[target_col]).copy()
            else:
                X_data = df.copy()
            if isinstance(X_data, pd.Series):
                X = X_data.to_frame()
            else:
                X = X_data
                
        y_data = df[target_col].copy() if target_col else None
        y: Optional[pd.Series] = None
        if y_data is not None:
            if isinstance(y_data, pd.DataFrame):
                y = y_data.iloc[:, 0]  # 取第一列作为Series
            else:
                y = y_data
                
        return X, y

    def _split_dataset(self, 
                       X_processed: pd.DataFrame, 
                       y_processed: Optional[pd.Series],
                       df: pd.DataFrame,
                       is_split: bool,
                       test_set: Optional[pd.DataFrame],
                       split_ratio: float,
                       feature_cols: Optional[List[str]],
                       target_col: Optional[str]) -> tuple:
        """
        划分数据集

        参数:
            X_processed (pd.DataFrame): 预处理后的特征数据
            y_processed (Optional[pd.Series]): 预处理后的目标数据
            df (pd.DataFrame): 原始数据
            is_split (bool): 是否需要划分数据集
            test_set (Optional[pd.DataFrame]): 测试数据集
            split_ratio (float): 划分比例
            feature_cols (Optional[List[str]]): 特征列名列表
            target_col (Optional[str]): 目标列名

        返回:
            tuple: (X_train, X_test, y_train, y_test) 训练和测试数据集
        """
        # 初始化测试集变量
        X_test: Optional[pd.DataFrame] = None
        y_test: Optional[pd.Series] = None
        X_train: pd.DataFrame = X_processed
        y_train: Optional[pd.Series] = y_processed

        if is_split and test_set is None:
            if y_processed is not None and target_col is not None:
                train_data = pd.concat([X_processed, y_processed], axis=1)
                train_subset, test_subset = self.split_data_set(train_data, 1 - split_ratio, y_processed)
                X_train = train_subset.drop(columns=[target_col])
                y_train = train_subset[target_col] if target_col in train_subset.columns else None
                X_test = test_subset.drop(columns=[target_col])
                y_test = test_subset[target_col] if target_col in test_subset.columns else None
            else:
                X_train, X_test = self.split_data_set(X_processed, 1 - split_ratio)
                y_train = None
        elif test_set is not None:
            X_train = X_processed
            y_train = y_processed
            if feature_cols:
                X_test_data = test_set[feature_cols].copy()
                if isinstance(X_test_data, pd.Series):
                    X_test = X_test_data.to_frame()
                else:
                    X_test = X_test_data
            else:
                if target_col:
                    X_test_data = test_set.drop(columns=[target_col]).copy()
                else:
                    X_test_data = test_set.copy()
                if isinstance(X_test_data, pd.Series):
                    X_test = X_test_data.to_frame()
                else:
                    X_test = X_test_data
            if X_test is not None:
                X_test, _ = self.preprocess(X_test, None)
        else:
            X_train = X_processed
            y_train = y_processed
            X_test = X_processed
            y_test = y_processed
            
        return X_train, X_test, y_train, y_test

    # ==========================================
    # 具体实现方法 (Concrete Methods)
    # 提供通用功能的实现
    # ==========================================

    def instantiate_model(self, model_name: str, random_state: int, model_params: Dict[str, Any]) -> Any:
        """
        【统一入口】实例化模型，确保全局只实例化一次

        从 model_analysis.json 或默认映射中查找模型类并实例化。
        该方法会被 analyzer 调用一次，子类不得重复调用。

        参数:
            model_name (str): 模型名称（不区分大小写）
            random_state (int): 随机种子
            model_params (Dict[str, Any]): 超参数

        返回:
            Any: 实例化的模型对象

        异常:
            ImportError, NotImplementedError: 模块或模型未找到
        """
        if model_params is None:
            model_params = {}

        # 统一处理模型名（转小写）
        model_key = model_name.lower().replace(" ", "")

        # 尝试加载配置文件中的映射
        model_mapping = self._load_model_mapping()

        if model_key not in model_mapping:
            logger.error(f"不支持的模型: {model_name}")
            raise NotImplementedError(f"模型 {model_name} 未在配置中定义")

        module_name = ""
        class_name = ""
        try:
            module_info = model_mapping[model_key]
            module_name = module_info["module"]
            class_name = module_info["class"]
            module = __import__(module_name, fromlist=[class_name])
            model_class = getattr(module, class_name)

            # 注入 random_state（若未提供）
            if "random_state" not in model_params:
                model_params["random_state"] = random_state

            model = model_class(**model_params)
            logger.info(f"模型 {model_name} 实例化成功: {model_class}")
            return model
        except ImportError as e:
            logger.error(f"导入失败 {module_name}.{class_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"实例化模型失败: {e}")
            raise

    def _load_model_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        内部方法：加载模型映射配置（优先从文件，失败则用默认）

        返回:
            Dict[str, Dict[str, str]]: 模型名 -> {module, class}
        """
        try:
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'Infrastructures', 'Configs')
            config_path = os.path.join(config_dir, 'model_analysis.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('model_mapping', self._get_default_model_mapping())
        except Exception as e:
            logger.warning(f"加载 model_analysis.json 失败，使用默认映射: {e}")

        return self._get_default_model_mapping()

    def _get_default_model_mapping(self) -> Dict[str, Dict[str, str]]:
        """返回内置的默认模型映射"""
        return {
            "logisticregression": {"module": "sklearn.linear_model", "class": "LogisticRegression"},
            "decisiontreeclassifier": {"module": "sklearn.tree", "class": "DecisionTreeClassifier"},
            "randomforestclassifier": {"module": "sklearn.ensemble", "class": "RandomForestClassifier"},
            "svc": {"module": "sklearn.svm", "class": "SVC"},
            "kneighborsclassifier": {"module": "sklearn.neighbors", "class": "KNeighborsClassifier"},
            "xgboostclassifier": {"module": "xgboost", "class": "XGBClassifier"},
            "linearregression": {"module": "sklearn.linear_model", "class": "LinearRegression"},
            "decisiontreeregressor": {"module": "sklearn.tree", "class": "DecisionTreeRegressor"},
            "randomforestregressor": {"module": "sklearn.ensemble", "class": "RandomForestRegressor"},
            "kmeans": {"module": "sklearn.cluster", "class": "KMeans"},
            "meanshift": {"module": "sklearn.cluster", "class": "MeanShift"},
            "agglomerativeclustering": {"module": "sklearn.cluster", "class": "AgglomerativeClustering"},
            "dbscan": {"module": "sklearn.cluster", "class": "DBSCAN"},
            "pca": {"module": "sklearn.decomposition", "class": "PCA"},
            "tsne": {"module": "sklearn.manifold", "class": "TSNE"},
            "mlpclassifier": {"module": "sklearn.neural_network", "class": "MLPClassifier"},
            "mlpregressor": {"module": "sklearn.neural_network", "class": "MLPRegressor"}
        }

    def load_config(self) -> Dict[str, Any]:
        """
        加载 JSON 配置文件

        返回:
            Dict[str, Any]: 解析后的配置字典

        异常:
            FileNotFoundError: 当文件不存在时
            json.JSONDecodeError: 当文件内容不是合法 JSON 时
        """
        config_path = Path(__file__).parent.parent.parent.parent.parent / 'Infrastructures' / 'Configs' / 'model_analysis.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"配置文件加载成功: {config_path.resolve()}")
            return config
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {config_path}, 错误: {e}")
            raise

    def feature_set_encoding(self, feature_set: pd.DataFrame, encoding_type: str) -> pd.DataFrame:
        """
        对特征集进行编码（仅处理 object/category 列）

        支持: 'onehot', 'label', 'auto'（>5个类别用 label，否则 onehot）, 'none'

        参数:
            feature_set (pd.DataFrame)
            encoding_type (str)

        返回:
            pd.DataFrame: 编码后特征集
        """
        logger.info(f"特征编码方式: {encoding_type}")
        if encoding_type == "none":
            return feature_set.copy()

        cat_cols = feature_set.select_dtypes(include=['object', 'category']).columns.tolist()
        if not cat_cols:
            return feature_set.copy()

        if encoding_type == "label" or (encoding_type == "auto" and len(cat_cols) > 5):
            df_encoded = feature_set.copy()
            for col in cat_cols:
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                self._fitted_encoders[f"feature_{col}"] = le
        else:
            df_encoded = pd.get_dummies(feature_set, columns=cat_cols, prefix=cat_cols)
            # 可选：保存 one-hot 的列名映射（如有需要）
        return df_encoded

    def target_col_encoding(self, target_col: pd.Series, encoding_type: str) -> tuple:
        """
        对目标列编码，返回编码后序列和编码器

        参数:
            target_col (pd.Series)
            encoding_type (str): "label" 或 "none"

        返回:
            tuple: (encoded_target, encoder)
        """
        if encoding_type == "none":
            return target_col.copy(), None

        le = LabelEncoder()
        encoded = pd.Series(
            le.fit_transform(target_col),
            name=target_col.name,
            index=target_col.index
        )
        self._fitted_encoders["target"] = le
        return encoded, le

    def split_data_set(self, data_set: pd.DataFrame, train_size: float,
                       stratify: Optional[pd.Series] = None) -> tuple:
        """
        划分训练/测试集

        参数:
            data_set: 数据集
            train_size: 训练占比
            stratify: 分层变量

        返回:
            tuple: (train_data, test_data)
        """
        try:
            train_data, test_data = train_test_split(
                data_set, train_size=train_size, stratify=stratify, random_state=42
            )
        except Exception:
            logger.warning("分层抽样失败，使用随机划分")
            train_data, test_data = train_test_split(
                data_set, train_size=train_size, random_state=42
            )
        return train_data, test_data

    def validate_cols_exist(self, cols: List[str], data_set: pd.DataFrame) -> bool:
        """检查列是否存在"""
        missing = [col for col in cols if col not in data_set.columns]
        if missing:
            raise KeyError(f"缺失列: {missing}")
        return True

    def fill_missing_values(self, data_set: pd.DataFrame, cols: List[str],
                            fill_strategy: str = "mean") -> pd.DataFrame:
        """填充缺失值"""
        data = data_set.copy()
        for col in cols:
            if col not in data.columns:
                continue
            if fill_strategy == "mean" and data[col].dtype in ['int64', 'float64']:
                data[col].fillna(data[col].mean(), inplace=True)
            elif fill_strategy == "median" and data[col].dtype in ['int64', 'float64']:
                data[col].fillna(data[col].median(), inplace=True)
            elif fill_strategy == "mode":
                mode_val = data[col].mode()
                if not mode_val.empty:
                    data[col].fillna(mode_val.iloc[0], inplace=True)
            elif fill_strategy == "forward":
                data[col].fillna(method='ffill', inplace=True)
            else:
                logger.warning(f"跳过列 {col} 的填充（策略不支持）")
        return data

    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series,
                       metrics: List[str]) -> Dict[str, float]:
        """通用模型评估"""
        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return {}

        results = {}
        for metric in metrics:
            try:
                if metric == "accuracy":
                    from sklearn.metrics import accuracy_score
                    results[metric] = accuracy_score(y_test, y_pred)
                elif metric == "precision":
                    from sklearn.metrics import precision_score
                    results[metric] = precision_score(y_test, y_pred, average='macro', zero_division='warn')
                elif metric == "recall":
                    from sklearn.metrics import recall_score
                    results[metric] = recall_score(y_test, y_pred, average='macro', zero_division='warn')
                elif metric == "f1_score":
                    from sklearn.metrics import f1_score
                    results[metric] = f1_score(y_test, y_pred, average='macro', zero_division='warn')
                elif metric == "roc_auc":
                    from sklearn.metrics import roc_auc_score
                    try:
                        y_proba = model.predict_proba(X_test)
                        results[metric] = roc_auc_score(y_test, y_proba, multi_class='ovr')
                    except:
                        results[metric] = float('nan')
                elif metric == "mse":
                    from sklearn.metrics import mean_squared_error
                    results[metric] = mean_squared_error(y_test, y_pred)
                elif metric == "rmse":
                    from sklearn.metrics import mean_squared_error
                    results[metric] = np.sqrt(mean_squared_error(y_test, y_pred))
                elif metric == "mae":
                    from sklearn.metrics import mean_absolute_error
                    results[metric] = mean_absolute_error(y_test, y_pred)
                elif metric == "r2_score":
                    from sklearn.metrics import r2_score
                    results[metric] = r2_score(y_test, y_pred)
                else:
                    logger.warning(f"未知指标: {metric}")
                    results[metric] = float('nan')
            except Exception as e:
                logger.warning(f"计算 {metric} 失败: {e}")
                results[metric] = float('nan')
        return results

    def load_model_params(self, model_name: str, model_type: str) -> Dict[str, Any]:
            """
            从配置文件加载指定模型的参数（超参数、特征映射、默认指标等）
            这是一个模板方法，子类可以直接使用而无需重新实现

            参数:
                model_name (str): 模型名称（如 "svc"）
                model_type (str): 模型类型（如 "classification"）

            返回:
                Dict[str, Any]: 包含模型配置的字典
                例：
                {
                "model_info": ["svc","sklearn.svm", "SVC"],
                    "default_model_params": {
                        "C": 1.0,
                        "kernel": "rbf",
                        "gamma": "scale",
                        "probability": True,
                    },
                }
            """
            # 加载配置文件,包含所有配置信息
            configs = self.load_config()
            
            # 获取模型特殊参数列表
            ML_special_params = configs["ML_model_special_params"]
            model_mapping = configs["model_mapping"]

            # 判断模型是否存在
            if model_type not in ML_special_params:
                raise ValueError(f"模型类型{model_type}不存在")
                
            if model_name not in ML_special_params[model_type]:  
                raise ValueError(f"模型{model_name}在{model_type}类型中不存在")

            # 声明结果与模型信息列表
            result: Dict[str, Any] = {}
            model_info: List[str] = []
            default_params: Dict[str, Any] = {}

            # 按固定顺序插入模型信息
            # 插入模型名
            model_info.append(model_name)
            # 插入模型模块名
            model_info.append(model_mapping[model_name]["module"])
            # 插入模型类名
            model_info.append(model_mapping[model_name]["class"])

            result["model_info"] = model_info

            # 过滤键信息
            default_params = {
                key: value for key, value in ML_special_params[model_type][model_name].items() if key != "key_description"
            }

            result["default_model_params"] = default_params

            return result