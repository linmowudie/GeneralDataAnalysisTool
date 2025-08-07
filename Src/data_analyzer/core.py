# data_engine.py
from . import data_import
from . import data_analyzer
from . import data_cleaning
from . import data_visualization
from . import reporting
from . import log_setting

import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Any, Union
from matplotlib.figure import Figure  # 用于类型提示

class DataProcessingEngine:
    """
    数据处理引擎类
    提供统一接口供外部调用，封装完整的数据处理流程
    """

    def __init__(
        self,
        resource_path: Union[Path, str],
        resource_type: str,
        db_connection_string: str,
        query: str,  # 修正拼写：quary -> query
        select_mode: str,
        params_list: list[str],
        is_database: bool = False,
        is_freedom_params: bool = False
    ):
        # 初始化配置参数
        self.resource_path = resource_path
        self.resource_type = resource_type
        self.db_connection_string = db_connection_string
        self.is_database = is_database
        self.query = query  # 修正拼写

        self.select_mode = select_mode
        self.params_list = params_list
        self.is_freedom_params = is_freedom_params

        # 初始化中间数据（必须显式赋值为 None）
        self.imported_data: Optional[pd.DataFrame] = None
        self.cleaned_data: Optional[pd.DataFrame] = None
        self.analyzed_data: Optional[pd.DataFrame] = None
        self.visualized_plot: Optional[Figure] = None  

        # 初始化日志：调用 log_setting.setup_logging()
        self.logger = log_setting.setup_logging()

        # 可选：记录实例化信息
        self.logger.debug(
            "DataProcessingEngine 初始化完成，资源路径: %s, 数据源类型: %s",
            self.resource_path, self.resource_type
        )

    def import_data(self) -> None:
        """导入数据，可导入文件或者数据库的表"""
        try:
            importer = data_import.DataImport(
                file_resource=self.resource_path,
                resource_type=self.resource_type,
                db_connection_string=self.db_connection_string,
                is_database=self.is_database
            )
            self.imported_data = importer.import_data(query=self.query)

        except Exception as e:
            error_msg = f"数据导入失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)  # 记录完整堆栈
            raise ValueError(error_msg) from e

    def clean_data(self) -> None:
        """数据清洗阶段"""
        if self.imported_data is None:
            error_msg = "请先导入数据"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            cleaner = data_cleaning.CleanDataMode(
                self.imported_data,
                self.select_mode,
                self.params_list,
                self.is_freedom_params
            )
            self.cleaned_data = cleaner.clean_data()

        except Exception as e:
            error_msg = f"数据清洗失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e


   