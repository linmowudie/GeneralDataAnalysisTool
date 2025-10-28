from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import logging
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os

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
    """

    def __init__(self):
        """
        初始化分析器。子类可扩展初始化逻辑，但不应在此处实例化模型。
        """
        self._model_instance = None  # 内部缓存已实例化的模型（仅供 analyzer 使用）
        self._fitted_encoders = {}   # 用于保存训练中使用的编码器（如 LabelEncoder）

    @abstractmethod
    def load_params(self, model_name: str) -> Dict[str, Any]:
        """
        从配置文件加载指定模型的参数（超参数、特征映射、默认指标等）

        ⚠️ 覆写要求：
          - 必须调用 self.load_config(...) 加载配置
          - 返回字典格式：{'model_name': ..., 'hyper_params': ..., 'feature_cols': ..., 'target_col': ...}
          - 不得在此方法中实例化模型

        参数:
            model_name (str): 模型名称（如 "random_forest"）

        返回:
            Dict[str, Any]: 包含模型配置的字典
        """
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        校验加载的参数是否合法（如必要字段是否存在、类型是否正确）

        ⚠️ 覆写要求：
          - 必须对关键字段（如 feature_cols, target_col）进行存在性和类型检查
          - 若校验失败，抛出 ValueError
          - 不得在此方法中修改参数或实例化模型

        参数:
            params (Dict[str, Any]): 参数字典

        返回:
            bool: 校验通过返回 True

        异常:
            ValueError: 参数不合法时抛出
        """
        pass

    @abstractmethod
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> tuple:
        """
        执行任务特定的数据预处理（如特征工程、缺失值处理、标准化等）

        ⚠️ 覆写要求：
          - 可调用基类的 fill_missing_values、feature_set_encoding 等方法
          - 必须返回处理后的 (X_processed, y_processed)
          - 若 y 为 None（如聚类），可只返回 X_processed
          - 不得在此方法中实例化模型

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
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """
        训练后处理，如特征重要性提取、模型解释、中间结果保存等

        ⚠️ 覆写要求：
          - 可调用 get_feature_importance 等方法
          - 返回字典格式的后处理结果
          - 不得修改模型或重新训练

        参数:
            model (Any): 训练完成的模型
            X (pd.DataFrame): 特征数据（通常为训练集）
            y (Optional[pd.Series]): 标签数据

        返回:
            Dict[str, Any]: 后处理结果
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
        保存模型及相关产物（模型文件、编码器、特征列表等）

        ⚠️ 覆写要求：
          - 使用 joblib/pickle 保存 model
          - 同时保存编码器（self._fitted_encoders）、特征名等元数据
          - 返回保存是否成功

        参数:
            model (Any): 模型对象
            filepath (str): 保存路径（不含扩展名）

        返回:
            bool: 是否成功
        """
        pass

    @abstractmethod
    def predict(self, model: Any, X: pd.DataFrame) -> pd.Series:
        """
        使用训练好的模型进行预测

        ⚠️ 覆写要求：
          - 调用 model.predict(X)
          - 若为分类任务且需解码，使用 self._fitted_encoders 还原原始标签
          - 返回 pd.Series，index 与 X 一致

        参数:
            model (Any): 训练好的模型
            X (pd.DataFrame): 预测数据

        返回:
            pd.Series: 预测结果
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

        ⚠️ 该方法由子类实现，但应遵循统一流程：
          1. 加载参数 -> 2. 校验参数 -> 3. 预处理 -> 4. 划分数据 ->
          5. 实例化模型 -> 6. 训练 -> 7. 预测与评估 -> 8. 后处理 -> 9. 保存

        ⚠️ 子类不得在 analyzer 内部调用 instantiate_model 以外的方式创建模型！

        （详见具体子类实现）
        """
        pass

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

        try:
            module_name = model_mapping[model_key]["module"]
            class_name = model_mapping[model_key]["class"]
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
            config_dir = os.path.join(os.path.dirname(__file__), '..', 'Configs')
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

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        加载 JSON 配置文件

        参数:
            config_file (str): 文件路径

        返回:
            Dict[str, Any]: 配置字典

        异常:
            FileNotFoundError, json.JSONDecodeError
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"配置文件加载成功: {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {config_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {config_file}, 错误: {e}")
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
                    results[metric] = precision_score(y_test, y_pred, average='macro', zero_division=0)
                elif metric == "recall":
                    from sklearn.metrics import recall_score
                    results[metric] = recall_score(y_test, y_pred, average='macro', zero_division=0)
                elif metric == "f1_score":
                    from sklearn.metrics import f1_score
                    results[metric] = f1_score(y_test, y_pred, average='macro', zero_division=0)
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
                    results[metric] = mean_squared_error(y_test, y_pred, squared=False)
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