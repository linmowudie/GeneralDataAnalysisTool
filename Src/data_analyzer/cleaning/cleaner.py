# cleaning/cleaner.py
import pandas as pd
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
import logging
from scipy.stats import zscore
import numpy as np

# -------------------------------
# 日志配置（入口调用一次即可）
# -------------------------------
from ..log_setting import setup_logging

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 配置类（带参数注释 | 优化：使用 Google/NumPy 风格 Docstring）
# --------------------------------------------------
@dataclass
class Config:
    """
    数据清洗配置类，用于控制清洗流程的各个参数。

    支持通过字符串列表解析参数，例如：
        [
            "columns=['A', 'B']",
            "drop_duplicates=True",
            "handle_missing='fill'",
            "fill_method='median'",
            "outlier_method='iqr'",
            "schema_rules={'A': {'min': 0}}"
        ]

    Attributes:
        columns (Optional[List[str]]): 要保留的列名列表。None 表示保留所有列。
        drop_duplicates (bool): 是否删除重复行。
        duplicate_subset (Optional[List[str]]): 去重时参考的列。None 表示基于所有列。
        handle_missing (str): 缺失值处理策略：'drop', 'fill', 'auto'。
        fill_value (Any): 固定值填充缺失值（优先于 fill_method）。
        fill_method (str): 填充方法：'mean', 'median', 'mode', 'ffill', 'bfill'。
        outlier_method (str): 异常值处理方法：'iqr', 'zscore', 'none'。
        outlier_threshold (float): 异常值阈值（IQR 倍数或 Z-score 标准差）。
        custom_cleaners (Optional[List[Callable]]): 用户自定义清洗函数列表。
        validate_schema (bool): 是否启用 schema 验证。
        schema_rules (Optional[Dict]): 每列的验证规则，如 {'age': {'min': 0, 'max': 100}}。
        return_stats (bool): 是否返回清洗统计（预留功能）。
    """
    columns: Optional[List[str]] = None
    drop_duplicates: bool = True
    duplicate_subset: Optional[List[str]] = None
    handle_missing: str = 'auto'  # 支持 'drop', 'fill', 'auto'
    fill_value: Any = None
    fill_method: str = 'mean'  # mean/median/mode/ffill/bfill
    outlier_method: str = 'iqr'  # iqr/zscore/none
    outlier_threshold: float = 1.5
    custom_cleaners: Optional[List[Callable[[pd.DataFrame], pd.DataFrame]]] = None
    validate_schema: bool = False
    schema_rules: Optional[Dict[str, Dict[str, Any]]] = None
    return_stats: bool = False


# --------------------------------------------------
# 清洗类 | 优化：增强日志 + 安全 + 注释
# --------------------------------------------------
class CleanData:
    """
    数据清洗核心类，提供标准、严格、宽松及自定义清洗模式。
    """

    def __init__(self, df: pd.DataFrame):
        if df is None:
            raise ValueError("输入 DataFrame 不能为 None")
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"期望 pd.DataFrame，但得到 {type(df)}")

        logger.debug("CleanData 初始化，输入数据形状: %s", df.shape)
        self.df = df

    def strict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        严格清洗模式：删除所有缺失值和重复行。

        Args:
            df (pd.DataFrame): 输入数据

        Returns:
            pd.DataFrame: 清洗后数据

        Example:
            >>> cleaner = CleanData(df)
            >>> cleaned = cleaner.strict(df)
        """
        logger.info("执行 strict 模式清洗")
        logger.debug("strict 模式前数据形状: %s", df.shape)

        df_cleaned = df.dropna().drop_duplicates()

        logger.info("strict 模式完成，删除缺失值和重复行")
        logger.debug("strict 模式后数据形状: %s", df_cleaned.shape)
        return df_cleaned

    def standard(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准清洗模式：去重 + 智能填充缺失值（数值用中位数，类别用众数）。

        Args:
            df (pd.DataFrame): 输入数据

        Returns:
            pd.DataFrame: 清洗后数据
        """
        logger.info("执行 standard 模式清洗")
        logger.debug("standard 模式前数据形状: %s", df.shape)

        df = df.copy()
        df = df.drop_duplicates()

        numeric_cols = df.select_dtypes(include='number').columns
        object_cols = df.select_dtypes(include='object').columns

        for col in numeric_cols:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            logger.debug("数值列 '%s' 使用中位数 %.2f 填充缺失值", col, median_val)

        for col in object_cols:
            mode_result = df[col].mode()
            if not mode_result.empty:
                df[col].fillna(mode_result[0], inplace=True)
            else:
                df[col].fillna('unknown', inplace=True)
            logger.debug("类别列 '%s' 填充完成", col)

        logger.info("standard 模式完成")
        logger.debug("standard 模式后数据形状: %s", df.shape)
        return df

    def relaxed(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        宽松清洗模式：仅去重，保留缺失值。

        Args:
            df (pd.DataFrame): 输入数据

        Returns:
            pd.DataFrame: 去重后数据
        """
        logger.info("执行 relaxed 模式清洗")
        logger.debug("relaxed 模式前数据形状: %s", df.shape)

        df_cleaned = df.drop_duplicates()

        logger.info("relaxed 模式完成，仅删除重复行")
        logger.debug("relaxed 模式后数据形状: %s", df_cleaned.shape)
        return df_cleaned

    def custom(self, df: pd.DataFrame, params_list: List[str]) -> pd.DataFrame:
        """
        自定义清洗模式：解析参数并应用配置。

        Args:
            df (pd.DataFrame): 输入数据
            params_list (List[str]): 参数列表，格式为 "key=value"

        Returns:
            pd.DataFrame: 清洗后数据

        Notes:
            - 使用安全解析，避免 eval 执行任意代码
            - 无效参数将被忽略并记录警告
            - 若无有效参数，则回退到 standard 模式
        """
        logger.info("开始 custom 模式清洗，参数数量: %d", len(params_list))
        config = Config()
        valid_keys = []

        # 安全解析参数（避免 eval）
        for param in params_list:
            try:
                key, raw_value = param.split('=', 1)
                key = key.strip()
                value = self._safe_eval(raw_value.strip())

                if hasattr(config, key):
                    setattr(config, key, value)
                    valid_keys.append(key)
                    logger.debug("成功解析参数: %s = %s", key, value)
                else:
                    logger.warning("无效参数名 '%s' 已忽略", key)

            except ValueError:
                logger.error("参数格式错误，缺少 '=': %s", param)
            except Exception as e:
                logger.error("参数解析失败 '%s': %s", param, e)

        if not valid_keys:
            logger.warning("所有自定义参数无效，回退到 standard 模式")
            return self.standard(df.copy())

        logger.info("应用自定义配置，有效参数: %s", valid_keys)
        return self._apply_config(df, config)

    def _safe_eval(self, value_str: str) -> Any:
        """
        安全地解析字符串为 Python 字面量（替代 eval）。
        仅支持基本类型：str, int, float, bool, list, dict, None。

        Args:
            value_str (str): 要解析的字符串

        Returns:
            解析后的值

        Raises:
            ValueError: 解析失败
        """
        import ast
        try:
            return ast.literal_eval(value_str)
        except (SyntaxError, ValueError):
            # 如果不是字面量，视为字符串
            return value_str.strip("'\"")

    def _apply_config(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """
        根据配置对象执行完整的清洗流程。

        Args:
            df (pd.DataFrame): 输入数据
            config (Config): 清洗配置

        Returns:
            pd.DataFrame: 清洗后数据
        """
        logger.debug("开始应用清洗配置")
        df = df.copy()  # 保留原始数据

        try:
            df = self._select_columns(df, config)
            df = self._handle_duplicates(df, config)
            df = self._handle_missing_values(df, config)
            df = self._handle_outliers(df, config)
            df = self._validate_schema_rules(df, config)
            df = self._apply_custom_cleaners(df, config)

            logger.info("配置应用完成，最终数据形状: %s", df.shape)
        except Exception as e:
            logger.error("清洗流程中发生错误", exc_info=True)
            raise

        return df

    def _select_columns(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """保留指定列。"""
        if not config.columns:
            return df

        missing = [c for c in config.columns if c not in df.columns]
        if missing:
            logger.error("指定列不存在: %s", missing)
            raise KeyError(f"列不存在: {missing}")

        logger.info("保留列: %s", config.columns)
        return df[config.columns]

    def _handle_duplicates(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """处理重复行。"""
        if config.drop_duplicates:
            subset_str = str(config.duplicate_subset) if config.duplicate_subset else "所有列"
            logger.info("删除重复行，参考列: %s", subset_str)
            df = df.drop_duplicates(subset=config.duplicate_subset)
        return df

    def _handle_missing_values(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """处理缺失值。"""
        logger.info("处理缺失值，策略: %s", config.handle_missing)

        if config.handle_missing == 'drop':
            initial_rows = len(df)
            df = df.dropna()
            logger.info("删除含缺失值的行，减少 %d 行", initial_rows - len(df))
            return df

        if config.handle_missing == 'fill':
            if config.fill_value is not None:
                df = df.fillna(config.fill_value)
                logger.info("使用固定值 '%s' 填充缺失值", config.fill_value)
                return df

            numeric_cols = df.select_dtypes(include='number').columns
            for col in numeric_cols:
                if config.fill_method == 'mean':
                    val = df[col].mean()
                elif config.fill_method == 'median':
                    val = df[col].median()
                elif config.fill_method == 'mode':
                    mode = df[col].mode()
                    val = mode[0] if not mode.empty else np.nan
                else:
                    logger.warning("未知填充方法 '%s'，跳过列 '%s'", config.fill_method, col)
                    continue

                df[col].fillna(val, inplace=True)
                logger.debug("列 '%s' 使用 '%s' (%s) 填充", col, config.fill_method, val)

        return df

    def _handle_outliers(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """处理异常值。"""
        if config.outlier_method == 'none':
            return df

        logger.info("检测并处理异常值，方法: %s, 阈值: %.2f", config.outlier_method, config.outlier_threshold)
        initial_rows = len(df)
        numeric_cols = df.select_dtypes(include='number').columns

        if config.outlier_method == 'iqr':
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - config.outlier_threshold * IQR
                upper = Q3 + config.outlier_threshold * IQR
                mask = df[col].between(lower, upper)
                df = df[mask]
                removed = initial_rows - len(df)
                if removed > 0:
                    logger.info("IQR 方法在列 '%s' 中移除 %d 个异常值", col, removed)

        elif config.outlier_method == 'zscore':
            numeric_cols = df.select_dtypes(include='number').columns
            for col in numeric_cols:
                clean_data = df[col].dropna()
                if len(clean_data) == 0:
                    logger.warning("列 '%s' 中没有有效的数值数据，无法进行 Z-score 方法的异常值检测", col)
                    continue
                z_scores = np.array(zscore(clean_data, nan_policy='omit'))  # 明确转为 ndarray
                mask = np.abs(z_scores) < config.outlier_threshold
                reindexed_mask = pd.Series(mask, index=clean_data.index).reindex(df.index, fill_value=True)
                df = df[reindexed_mask]
                
            removed = initial_rows - len(df)
            if removed > 0:
                logger.info("Z-score 方法共移除 %d 个异常值", removed)

        return df

    def _validate_schema_rules(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """验证并过滤数据。"""
        if not config.validate_schema or not config.schema_rules:
            return df

        logger.info("执行 schema 验证，规则数量: %d", len(config.schema_rules))
        for col, rules in config.schema_rules.items():
            if col not in df.columns:
                logger.warning("验证规则中列 '%s' 不存在，跳过", col)
                continue

            logger.debug("验证列 '%s': %s", col, rules)

            if 'dtype' in rules:
                try:
                    df[col] = df[col].astype(rules['dtype'])
                    logger.debug("列 '%s' 类型转换为 %s", col, rules['dtype'])
                except Exception as e:
                    logger.error("列 '%s' 类型转换失败: %s", col, e)
                    raise TypeError(f"类型转换失败: {col}") from e

            if 'min' in rules:
                df = df[df[col] >= rules['min']]
                logger.debug("列 '%s' 应用最小值约束: >= %.2f", col, rules['min'])
            if 'max' in rules:
                df = df[df[col] <= rules['max']]
                logger.debug("列 '%s' 应用最大值约束: <= %.2f", col, rules['max'])

        return df

    def _apply_custom_cleaners(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """应用用户自定义清洗函数。"""
        if not config.custom_cleaners:
            return df

        logger.info("应用 %d 个自定义清洗函数", len(config.custom_cleaners))
        for i, func in enumerate(config.custom_cleaners):
            try:
                df = func(df)
                logger.debug("自定义函数 %d 执行成功", i+1)
            except Exception as e:
                logger.error("自定义函数 %d 执行失败: %s", i+1, e, exc_info=True)
                raise

        return df