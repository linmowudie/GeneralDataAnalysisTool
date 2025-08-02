import pandas as pd
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
import logging
from scipy.stats import zscore
import numpy as np
from ..log_setting import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# --------------------------------------------------
# 配置类（带参数注释）
# --------------------------------------------------
@dataclass
class Config:
    """
    清洗配置类。
    
    支持的参数可通过 params_list 传入，例如：
        [
            "columns=['A', 'B']",               # 仅保留指定列
            "drop_duplicates=True",             # 是否去重
            "duplicate_subset=['A']",           # 去重时参考的列
            "handle_missing='fill'",            # 缺失值处理策略：'drop' | 'fill' | 'auto'
            "fill_value=0",                     # 缺失值填充固定值（优先于 fill_method）
            "fill_method='median'",             # 缺失值填充方法：'mean' | 'median' | 'mode' | 'ffill' | 'bfill'
            "outlier_method='iqr'",             # 异常值处理方式：'iqr' | 'zscore' | 'none'
            "outlier_threshold=1.5",            # 异常值阈值（用于 iqr/zscore）
            "validate_schema=True",             # 是否启用数据验证
            "schema_rules={'A': {'min': 0}}",   # 每列验证规则
            "return_stats=False"                # 是否返回清洗统计（预留）
        ]

    :param columns: 要保留的列名列表，若为 None 则保留所有列。
    :param drop_duplicates: 是否删除重复行，默认为 True。
    :param duplicate_subset: 执行去重时参考的列列表，若为 None 则基于所有列判断重复。
    :param handle_missing: 缺失值处理策略，可选值：'drop'（删除含缺失的行）、'fill'（填充）、'auto'（自动选择）。
    :param fill_value: 用于填充缺失值的固定值，若不为 None，则优先于 fill_method 使用。
    :param fill_method: 填充缺失值的方法，可选：'mean'、'median'、'mode'、'ffill'、'bfill'。
    :param outlier_method: 异常值检测与处理方法，可选：'iqr'（四分位距）、'zscore'（Z 分数）、'none'（不处理）。
    :param outlier_threshold: 异常值判定的阈值。IQR 方法中为倍数，Z-score 中为标准差倍数。
    :param custom_cleaners: 用户自定义清洗函数列表，每个函数接收并返回一个 DataFrame。
    :param validate_schema: 是否根据 schema_rules 对数据进行验证和过滤。
    :param schema_rules: 每列的验证规则字典，例如 {'A': {'min': 0, 'max': 100}, 'B': {'required': True}}。
    :param return_stats: 是否返回清洗过程的统计信息（当前为预留功能，尚未实现）。
    """
    columns: Optional[List[str]] = None
    drop_duplicates: bool = True
    duplicate_subset: Optional[List[str]] = None
    handle_missing: str = 'auto'
    fill_value: Any = None
    fill_method: str = 'mean'
    outlier_method: str = 'iqr'
    outlier_threshold: float = 1.5
    custom_cleaners: Optional[List[Callable[[pd.DataFrame], pd.DataFrame]]] = None
    validate_schema: bool = False
    schema_rules: Optional[Dict[str, Dict[str, Any]]] = None
    return_stats: bool = False

# --------------------------------------------------
# 清洗类
# --------------------------------------------------
class CleanData:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    def strict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        严格模式：对数据进行最彻底的清洗。
        
        功能说明：
        - 删除所有包含缺失值（NaN）的行（dropna）。
        - 删除所有完全重复的行（drop_duplicates）。
        - 仅保留完整且唯一的记录，适用于对数据质量要求极高的场景。
        
        参数:
            df (pd.DataFrame): 输入的原始数据框。
            
        返回:
            pd.DataFrame: 清洗后的数据框，不含缺失值和重复行。
        """
        return df.dropna().drop_duplicates()

    def standard(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准模式：采用常规策略处理缺失值和重复数据。
        
        功能说明：
        - 创建数据框副本，避免修改原始数据。
        - 删除完全重复的行。
        - 对数值型列的缺失值，使用该列的中位数（median）填充。
        - 对类别型（object）列的缺失值，使用该列的众数（mode）填充；
          若众数为空（如全为空值），则填充为 'unknown' 字符串。
        - 平衡了数据保留与质量，适用于大多数标准数据分析任务。
        
        参数:
            df (pd.DataFrame): 输入的原始数据框。
            
        返回:
            pd.DataFrame: 清洗并填充缺失值后的数据框，无重复行。
        """
        df = df.copy()
        df = df.drop_duplicates()
        for col in df.select_dtypes(include='number').columns:
            df[col].fillna(df[col].median(), inplace=True)
        for col in df.select_dtypes(include='object').columns:
            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown', inplace=True)
        return df

    def relaxed(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        宽松模式：仅处理重复数据，保留尽可能多的记录。
        
        功能说明：
        - 仅删除完全重复的行（保留第一次出现的记录）。
        - 不处理任何缺失值，保留 NaN。
        - 适用于数据缺失较多但仍需保留所有信息的探索性分析阶段。
        
        参数:
            df (pd.DataFrame): 输入的原始数据框。
            
        返回:
            pd.DataFrame: 去重后的数据框，保留所有非重复行（含缺失值）。
        """
        return df.drop_duplicates()

    def custom(self, df: pd.DataFrame, params_list: List[str]) -> pd.DataFrame:
        """
        自定义清洗模式。
        如果所有参数无效，则回退到 standard 模式。
        :param params_list: 自定义参数列表，格式为 "key=value"。
        """
        config = Config()
        valid_keys = []

        for param in params_list:
            try:
                # 解析参数
                key, value_str = param.split('=', 1)
                key = key.strip()
                value = eval(value_str.strip(), {"__builtins__": {}}, {})

                # 检查参数
                if hasattr(config, key):
                    setattr(config, key, value)
                    valid_keys.append(key)

                else:
                    logger.warning(f"无效参数: {key}，已忽略。")

            except Exception as e:
                logger.error(f"参数解析失败: {param}，错误: {e}")

        if not valid_keys:
            logger.warning("所有自定义参数无效，回退到 standard 模式。")
            return self.standard(df)

        return self._apply_config(df, config)

    def _apply_config(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """
        根据配置执行数据清洗逻辑（主流程）。

        :param df: 输入的原始数据框。
        :param config: 数据清洗配置对象（Config 类实例）。
        :return: 清洗后的数据框。
        """
        df = df.copy()

        df = self._select_columns(df, config)
        df = self._handle_duplicates(df, config)
        df = self._handle_missing_values(df, config)
        df = self._handle_outliers(df, config)
        df = self._validate_schema_rules(df, config)
        df = self._apply_custom_cleaners(df, config)

        return df


    def _select_columns(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """
        保留指定列，若列不存在则报错。

        :param df: 输入数据框。
        :param config: 配置对象。
        :return: 仅包含指定列的 DataFrame。
        """
        if not config.columns:
            return df

        missing = [c for c in config.columns if c not in df.columns]
        if missing:
            logger.error(f"列不存在: {missing}")
            raise KeyError(f"列不存在: {missing}")

        return df[config.columns]


    def _handle_duplicates(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """
        根据配置删除重复行。

        :param df: 输入数据框。
        :param config: 配置对象。
        :return: 去重后的 DataFrame。
        """
        if config.drop_duplicates:
            df = df.drop_duplicates(subset=config.duplicate_subset)
        return df


    def _handle_missing_values(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """
        处理缺失值：删除或填充。

        :param df: 输入数据框。
        :param config: 配置对象。
        :return: 缺失值处理后的 DataFrame。
        """
        if config.handle_missing == 'drop':
            return df.dropna()

        elif config.handle_missing == 'fill':
            if config.fill_value is not None:
                return df.fillna(config.fill_value)

            # 填充数值型列
            numeric_cols = df.select_dtypes(include='number').columns
            for col in numeric_cols:
                if config.fill_method == 'mean':
                    df[col].fillna(df[col].mean(), inplace=True)
                elif config.fill_method == 'median':
                    df[col].fillna(df[col].median(), inplace=True)
                elif config.fill_method == 'mode':
                    mode = df[col].mode()
                    df[col].fillna(mode[0] if not mode.empty else None, inplace=True)
        return df


    def _handle_outliers(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """
        根据配置处理异常值（IQR 或 Z-score 方法）。

        :param df: 输入数据框。
        :param config: 配置对象。
        :return: 过滤异常值后的 DataFrame。
        """
        if config.outlier_method == 'iqr':
            numeric_cols = df.select_dtypes(include='number').columns
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - config.outlier_threshold * IQR
                upper = Q3 + config.outlier_threshold * IQR
                df = df[df[col].between(lower, upper)]

        elif config.outlier_method == 'zscore':
            numeric_cols = df.select_dtypes(include='number').columns
            for col in numeric_cols:
                clean_data = df[col].dropna()
                z_scores = zscore(clean_data, nan_policy='omit')
                mask = np.abs(z_scores) < config.outlier_threshold
                reindexed_mask = mask.reindex(df.index, fill_value=True)
                df = df[reindexed_mask]

        return df


    def _validate_schema_rules(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """
        根据 schema_rules 验证并过滤数据（类型、范围等）。

        :param df: 输入数据框。
        :param config: 配置对象。
        :return: 验证通过的 DataFrame。
        """
        if not config.validate_schema or not config.schema_rules:
            return df

        for col, rules in config.schema_rules.items():
            if col not in df.columns:
                logger.warning(f"验证规则中列不存在: {col}")
                continue

            # 类型转换
            if 'dtype' in rules:
                try:
                    df[col] = df[col].astype(rules['dtype'])
                except Exception as e:
                    logger.error(f"列 {col} 类型转换失败: {e}")
                    raise TypeError(f"列 {col} 类型转换失败: {e}")

            # 范围检查
            if 'min' in rules:
                df = df[df[col] >= rules['min']]
            if 'max' in rules:
                df = df[df[col] <= rules['max']]

        return df


    def _apply_custom_cleaners(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """
        应用用户自定义清洗函数列表。

        :param df: 输入数据框。
        :param config: 配置对象。
        :return: 经自定义函数处理后的 DataFrame。
        """
        if config.custom_cleaners:
            for func in config.custom_cleaners:
                df = func(df)
        return df
