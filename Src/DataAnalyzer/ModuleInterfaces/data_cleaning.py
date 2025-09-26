"""
Src/DataAnalyzer/data_cleaning.py
数据清洗模块

该模块提供多种数据清洗模式，包括标准、严格和宽松模式，
也支持自定义参数进行数据清洗。继承自CleanData基类。
"""

# cleaning/clean_data_mode.py
import pandas as pd
from ..cleaning import CleanData
from typing import Union
import logging

logger = logging.getLogger(__name__)  # 获取当前模块的logger

class CleanDataMode(CleanData):
    MODES = ["standard", "strict", "relaxed"]

    def __init__(self, df: pd.DataFrame, select_mode: str, params_list: list[str], is_freedom_params: bool = False):
        super().__init__(df)
        self.df = df
        self.select_mode = select_mode
        self.params_list = params_list
        self.is_freedom_params = is_freedom_params
        
        logger.debug("CleanDataMode 初始化完成。模式: %s, 自定义参数: %s, 参数列表: %s",
                     self.select_mode, self.is_freedom_params, self.params_list)

    def clean_data(self) -> pd.DataFrame:
        logger.info("开始数据清洗流程")
        try:
            if not self.is_freedom_params:
                if self.select_mode not in self.MODES:
                    error_msg = f"不支持的清洗模式: '{self.select_mode}'，支持的模式: {self.MODES}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                logger.info("使用预设模式清洗数据: %s", self.select_mode)
                clean_method = getattr(self, self.select_mode, None)
                if clean_method is None:
                    error_msg = f"未实现清洗方法: {self.select_mode}"
                    logger.error(error_msg)
                    raise AttributeError(error_msg)

                cleaned_df = clean_method(self.df)
            else:
                logger.info("使用自定义参数清洗数据，参数列表: %s", self.params_list)
                if not self.params_list:
                    logger.warning("自定义参数列表为空，可能不会进行有效清洗")

                cleaned_df = self.custom(self.df, self.params_list)

            if not isinstance(cleaned_df, pd.DataFrame):
                error_msg = f"清洗方法必须返回 DataFrame，但返回了 {type(cleaned_df)}"
                logger.error(error_msg)
                raise TypeError(error_msg)

            logger.info("数据清洗成功完成")
            return cleaned_df
        except Exception as e:
            logger.error("数据清洗过程发生未预期错误", exc_info=True)
            raise ValueError(f"数据清洗失败: {str(e)}") from e