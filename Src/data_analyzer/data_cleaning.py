import pandas as pd
from .cleaning import cleaner
from typing import Union
import logging

class CleanDataMode(cleaner.CleanData):
    """
    定义参数模块，用于定义数据清洗模式
    :param df: 数据集
    ......
    """
    mode: list = [
        "standard",
        "strict",
        "relaxed"
    ]
    def __init__(self, df: pd.DataFrame, select_mode: str, params_list: list[str], is_freedom_params: bool = False):
        """
        初始化数据清洗模式
        :param df: 数据集
        :param select_mode: 选择的清洗模式
        :param params_list: 自选参数列表（当且仅当is_freedom_params为True时生效）
        :param is_freedom_params: 是否使用自定义参数
        """
        super().__init__(df)

        self.df = df
        self.select_mode = select_mode
        self.params_list = params_list
        self.is_freedom_params = is_freedom_params
    def clean_data(self) -> Union[pd.DataFrame, None]:
        if not self.is_freedom_params:
            if self.select_mode in self.mode:
                try:
                    clean_mothod = getattr(self, self.select_mode)
                    self.df = clean_mothod(self.df)
                    return self.df
                except Exception as e:
                    logging.error(f"无法使用默认模式清洗数据：{e}")
                    return None
                    
        else:
            try:
                self.df = self.custom(self.df, self.params_list)
                return self.df
            except Exception as e:
                logging.error(f"无法使用自由参数形式清洗数据{e}")
                return None