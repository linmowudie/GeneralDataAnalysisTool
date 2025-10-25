from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import logging
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import numpy as np

logger = logging.getLogger(__name__)

class BaseAnalyzer(ABC):
    """
    数据分析器基类
    
    所有具体的分析器类都必须继承自此类，并实现其中的抽象方法。
    此类提供了所有分析器共用的方法和属性。
    """

    def __init__(self):
        """
        初始化分析器基类
        """
        pass

    @abstractmethod
    def load_params(self, config_path: str) -> Dict[str, Any]:
        """
        从配置文件中加载任务参数
        
        参数:
            config_path (str): 配置文件路径
            
        返回:
            Dict[str, Any]: 包含模型名称、超参数、特征列、目标列等的字典
        """
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        参数校验方法，检查当前任务所需的特定参数是否合法
        
        参数:
            params (Dict[str, Any]): 待校验的参数字典
            
        返回:
            bool: 校验是否通过
            
        异常:
            ValueError: 当参数不合法时抛出
        """
        pass

    @abstractmethod
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> tuple:
        """
        数据预处理方法，定义任务特定的特征工程逻辑
        
        参数:
            X (pd.DataFrame): 特征数据
            y (Optional[pd.Series]): 目标数据
            
        返回:
            tuple: 预处理后的(X, y)数据
        """
        pass

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """
        模型训练方法，使用训练集数据拟合模型
        
        参数:
            X_train (pd.DataFrame): 训练特征数据
            y_train (Optional[pd.Series]): 训练目标数据
            
        返回:
            Any: 训练完成的模型对象
        """
        pass

    @abstractmethod
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """
        训练后处理方法，用于执行特征重要性提取、模型解释等操作
        
        参数:
            model (Any): 训练完成的模型
            X (pd.DataFrame): 特征数据
            y (Optional[pd.Series]): 目标数据
            
        返回:
            Dict[str, Any]: 包含后处理结果的字典
        """
        pass

    @abstractmethod
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        获取特征重要性或权重的方法
        
        参数:
            model (Any): 训练完成的模型
            
        返回:
            Dict[str, float]: 特征重要性字典，键为特征名，值为重要性分数
        """
        pass

    @abstractmethod
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """
        模型产物持久化方法，负责将模型文件、编码器、特征列表等关键信息序列化保存
        
        参数:
            model (Any): 要保存的模型对象
            filepath (str): 保存路径
            
        返回:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def predict(self, model: Any, X: pd.DataFrame) -> pd.Series:
        """
        封装的预测方法，接收新数据并输出模型预测结果
        
        参数:
            model (Any): 训练完成的模型
            X (pd.DataFrame): 待预测的特征数据
            
        返回:
            pd.Series: 预测结果
        """
        pass

    @abstractmethod
    def get_default_metrics(self, model_type: str) -> List[str]:
        """
        根据 model_type 从 model_analysis.json 配置文件中加载默认评估指标列表
        
        参数:
            model_type (str): 模型类型，如 "classification", "regression" 等
            
        返回:
            List[str]: 默认评估指标列表
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
              - model: 训练完成的模型对象
              - model_score: 模型评估得分
              - train_set: 实际用于训练的特征-标签数据集
              - test_set: 实际用于测试的数据集
              - feature_cols: 经过预处理后的最终特征列名
              - encoding_method: 编码方式记录
        """
        pass

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        加载配置文件方法，从指定路径加载配置文件，返回字典格式的配置信息
        
        参数:
            config_file (str): 配置文件路径
            
        返回:
            Dict[str, Any]: 配置信息字典
            
        异常:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式错误
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"配置文件 {config_file} 加载成功")
            return config
        except FileNotFoundError:
            logger.error(f"配置文件 {config_file} 不存在")
            raise
        except json.JSONDecodeError:
            logger.error(f"配置文件 {config_file} 格式错误")
            raise

    def feature_set_encoding(self, feature_set: pd.DataFrame, encoding_type: str) -> pd.DataFrame:
        """
        特征集编码方法，支持多种编码方式，自动识别类别型变量并执行相应编码
        
        参数:
            feature_set (pd.DataFrame): 待编码的特征数据集
            encoding_type (str): 编码方式，支持 "onehot"、"label"、"ordinal"、"target"、"none"、"auto" 等
            
        返回:
            pd.DataFrame: 编码后的特征数据集
        """
        logger.info(f"对特征集进行 {encoding_type} 编码")
        
        # 识别类别型变量
        categorical_columns = feature_set.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if not categorical_columns:
            logger.info("未发现类别型变量，跳过编码")
            return feature_set
            
        if encoding_type == "none":
            logger.info("编码方式为 'none'，跳过编码")
            return feature_set
            
        # 复制数据以避免修改原始数据
        encoded_features = feature_set.copy()
        
        if encoding_type == "label" or (encoding_type == "auto" and len(categorical_columns) > 5):
            # 使用标签编码
            for col in categorical_columns:
                le = LabelEncoder()
                encoded_features[col] = le.fit_transform(feature_set[col].astype(str))
                logger.debug(f"列 {col} 使用标签编码完成")
                
        elif encoding_type == "onehot" or encoding_type == "auto":
            # 使用独热编码
            encoded_features = pd.get_dummies(feature_set, columns=categorical_columns, prefix=categorical_columns)
            logger.debug(f"对列 {categorical_columns} 使用独热编码完成")
            
        return encoded_features

    def target_col_encoding(self, target_col: pd.Series, encoding_type: str) -> tuple:
        """
        目标列编码方法，根据任务类型及指定编码方式对目标变量进行编码
        
        参数:
            target_col (pd.Series): 待编码的目标列
            encoding_type (str): 编码方式，分类任务常用 "label"，回归为 "none"
            
        返回:
            tuple: (编码后的目标列, 编码器对象)
        """
        logger.info(f"对目标列进行 {encoding_type} 编码")
        
        if encoding_type == "none":
            logger.info("目标列编码方式为 'none'，跳过编码")
            return target_col, None
            
        # 使用标签编码
        le = LabelEncoder()
        encoded_target = pd.Series(le.fit_transform(target_col), name=target_col.name, index=target_col.index)
        logger.debug("目标列标签编码完成")
        
        return encoded_target, le

    def split_data_set(self, data_set: pd.DataFrame, train_size: float, stratify: Optional[pd.Series] = None) -> tuple:
        """
        数据集划分方法，根据train_size参数将数据划分为训练集和测试集
        
        参数:
            data_set (pd.DataFrame): 待划分的数据集
            train_size (float): 训练集占比，范围 (0,1)
            stratify (Optional[pd.Series]): 分层抽样依据列，默认为None
            
        返回:
            tuple: (X_train, X_test, y_train, y_test) 或 (X_train, X_test) 的元组
        """
        logger.info(f"按照 {train_size} 比例划分数据集")
        
        # 如果没有提供stratify参数，则不使用分层抽样
        if stratify is not None:
            try:
                train_data, test_data = train_test_split(
                    data_set, 
                    train_size=train_size, 
                    stratify=stratify,
                    random_state=42
                )
            except ValueError as e:
                logger.warning(f"分层抽样失败: {e}，使用普通划分")
                train_data, test_data = train_test_split(
                    data_set, 
                    train_size=train_size,
                    random_state=42
                )
        else:
            train_data, test_data = train_test_split(
                data_set, 
                train_size=train_size,
                random_state=42
            )
            
        logger.debug(f"训练集大小: {len(train_data)}, 测试集大小: {len(test_data)}")
        return train_data, test_data

    def validate_cols_exist(self, cols: List[str], data_set: pd.DataFrame) -> bool:
        """
        列存在性校验方法，检查指定列是否均存在于输入DataFrame中
        
        参数:
            cols (List[str]): 待检查的列名列表
            data_set (pd.DataFrame): 数据集
            
        返回:
            bool: 列是否存在
            
        异常:
            KeyError: 当列不存在时抛出
        """
        missing_cols = [col for col in cols if col not in data_set.columns]
        if missing_cols:
            logger.error(f"以下列在数据集中不存在: {missing_cols}")
            raise KeyError(f"以下列在数据集中不存在: {missing_cols}")
        return True

    def fill_missing_values(self, data_set: pd.DataFrame, cols: List[str], 
                           fill_strategy: str = "mean") -> pd.DataFrame:
        """
        缺失值填充方法，支持多种填充策略
        
        参数:
            data_set (pd.DataFrame): 包含缺失值的数据集
            cols (List[str]): 需要填充的列名列表
            fill_strategy (str): 填充策略，支持 "mean"(均值)、"median"(中位数)、"mode"(众数)、"forward"(前向填充) 等
            
        返回:
            pd.DataFrame: 填充后的数据集
        """
        logger.info(f"使用 {fill_strategy} 策略填充缺失值")
        
        # 复制数据以避免修改原始数据
        filled_data = data_set.copy()
        
        for col in cols:
            if col not in filled_data.columns:
                logger.warning(f"列 {col} 不存在于数据集中，跳过")
                continue
                
            if fill_strategy == "mean":
                # 均值填充（仅适用于数值型）
                if filled_data[col].dtype in ['int64', 'float64']:
                    filled_data[col].fillna(filled_data[col].mean(), inplace=True)
                else:
                    logger.warning(f"列 {col} 不是数值型，无法使用均值填充")
                    
            elif fill_strategy == "median":
                # 中位数填充（仅适用于数值型）
                if filled_data[col].dtype in ['int64', 'float64']:
                    filled_data[col].fillna(filled_data[col].median(), inplace=True)
                else:
                    logger.warning(f"列 {col} 不是数值型，无法使用中位数填充")
                    
            elif fill_strategy == "mode":
                # 众数填充
                mode_value = filled_data[col].mode()
                if not mode_value.empty:
                    filled_data[col].fillna(mode_value.iloc[0], inplace=True)
                else:
                    logger.warning(f"列 {col} 无众数，无法填充")
                    
            elif fill_strategy == "forward":
                # 前向填充
                filled_data[col].fillna(method='ffill', inplace=True)
                
            else:
                logger.warning(f"未知的填充策略: {fill_strategy}")
                
        logger.debug("缺失值填充完成")
        return filled_data

    def build_model_instance(self, model_name: str, model_params: Optional[Dict[str, Any]] = None) -> Any:
        """
        根据模型名称和参数从模型注册表中实例化对应模型对象
        
        参数:
            model_name (str): 模型名称
            model_params (Optional[Dict[str, Any]]): 模型超参数
            
        返回:
            Any: 实例化的模型对象
            
        异常:
            NotImplementedError: 当模型未实现时抛出
        """
        logger.info(f"构建 {model_name} 模型实例")
        
        # 确保model_params是一个字典
        if model_params is None:
            model_params = {}
            
        # 定义模型映射字典
        model_mapping = {
            "logisticregression": ("sklearn.linear_model", "LogisticRegression"),
            "decisiontreeclassifier": ("sklearn.tree", "DecisionTreeClassifier"),
            "randomforestclassifier": ("sklearn.ensemble", "RandomForestClassifier"),
            "svc": ("sklearn.svm", "SVC"),
            "kneighborsclassifier": ("sklearn.neighbors", "KNeighborsClassifier"),
            "xgboostclassifier": ("xgboost", "XGBClassifier"),
            "linearregression": ("sklearn.linear_model", "LinearRegression"),
            "decisiontreeregressor": ("sklearn.tree", "DecisionTreeRegressor"),
            "randomforestregressor": ("sklearn.ensemble", "RandomForestRegressor"),
            "kmeans": ("sklearn.cluster", "KMeans"),
            "meanshift": ("sklearn.cluster", "MeanShift"),
            "agglomerativeclustering": ("sklearn.cluster", "AgglomerativeClustering")
        }
        
        # 根据模型名称导入并实例化模型
        if model_name in model_mapping:
            try:
                module_name, class_name = model_mapping[model_name]
                module = __import__(module_name, fromlist=[class_name])
                model_class = getattr(module, class_name)
                model = model_class(**model_params)
                logger.debug(f"模型 {model_name} 实例化成功")
                return model
            except ImportError as e:
                logger.error(f"导入模型 {model_name} 失败: {e}")
                raise ImportError(f"无法导入 {model_name} 所需的库，请检查是否已安装")
            except Exception as e:
                logger.error(f"模型 {model_name} 实例化失败: {e}")
                raise
        else:
            logger.error(f"未实现的模型: {model_name}")
            raise NotImplementedError(f"模型 {model_name} 未实现")

    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series, 
                      metrics: List[str]) -> Dict[str, float]:
        """
        通用模型评估方法，接收模型、测试数据和metrics_list，计算性能指标
        
        参数:
            model (Any): 训练完成的模型
            X_test (pd.DataFrame): 测试特征数据
            y_test (pd.Series): 测试目标数据
            metrics (List[str]): 评估指标列表
            
        返回:
            Dict[str, float]: 评估结果字典，键为指标名，值为指标值
        """
        logger.info(f"使用指标 {metrics} 评估模型")
        
        # 获取模型预测结果
        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            logger.error(f"模型预测失败: {e}")
            return {}
            
        results = {}
        
        for metric in metrics:
            try:
                if metric == "accuracy":
                    from sklearn.metrics import accuracy_score
                    results[metric] = accuracy_score(y_test, y_pred)
                    
                elif metric == "precision":
                    from sklearn.metrics import precision_score
                    # 对于多分类问题，使用macro平均
                    results[metric] = precision_score(y_test, y_pred, average='macro', zero_division='warn')
                    
                elif metric == "recall":
                    from sklearn.metrics import recall_score
                    # 对于多分类问题，使用macro平均
                    results[metric] = recall_score(y_test, y_pred, average='macro', zero_division='warn')
                    
                elif metric == "f1_score":
                    from sklearn.metrics import f1_score
                    # 对于多分类问题，使用macro平均
                    results[metric] = f1_score(y_test, y_pred, average='macro', zero_division='warn')
                    
                elif metric == "roc_auc":
                    from sklearn.metrics import roc_auc_score
                    # 注意：对于多分类问题，roc_auc_score需要特殊处理
                    try:
                        y_pred_proba = model.predict_proba(X_test)
                        results[metric] = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
                    except:
                        # 如果无法计算概率，则跳过该指标
                        logger.warning("无法计算ROC AUC指标")
                        results[metric] = np.nan
                        
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
                    logger.warning(f"未知的评估指标: {metric}")
                    
            except Exception as e:
                logger.warning(f"计算指标 {metric} 时出错: {e}")
                results[metric] = np.nan
                
        logger.debug("模型评估完成")
        return results
