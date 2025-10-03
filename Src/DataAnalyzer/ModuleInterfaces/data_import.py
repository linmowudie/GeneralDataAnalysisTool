"""
Src/DataAnalyzer/data_import.py
数据导入模块

该模块提供统一的数据导入接口，支持从文件和数据库导入数据。
使用组合模式替代继承，避免耦合问题。支持大文件读取优化。
"""

from pathlib import Path
from typing import Union, Optional
import logging
import pandas as pd
import os
from ..ImporterModule.db_import import DatabaseImport
from ..ImporterModule.file_import import FileImport

logger = logging.getLogger(__name__)


class DataImport:
    """
    统一的数据导入接口，支持文件和数据库。
    使用组合模式，避免多重继承带来的问题。
    """

    def __init__(
        self,
        file_resource: Union[str, Path],
        resource_type: str,
        db_connection_string: Optional[str] = None,
        is_database: bool = False,
    ) -> None:
        """
        初始化 DataImport 实例。

        :param file_resource: 文件路径或数据库表名（根据模式决定）
        :param resource_type: 文件类型（csv/json/xlsx）或数据库类型（sqlite/postgresql）
        :param db_connection_string: 数据库连接字符串（仅数据库模式需要）
        :param is_database: 是否从数据库导入
        """
        self.is_database = is_database
        self.file_resource = file_resource
        self.resource_type = resource_type
        self.db_connection_string = db_connection_string

        # 组合：内部持有两个导入器，按需初始化
        self._file_importer: Optional[FileImport] = None
        self._db_importer: Optional[DatabaseImport] = None

        if self.is_database:
            if not db_connection_string:
                raise ValueError("导入数据库时，请提供数据库连接信息。")
            self._db_importer = DatabaseImport(db_connection_string, resource_type)
        else:
            self._file_importer = FileImport(file_resource, resource_type)

    def import_data(self, chunksize: Optional[int] = None, **kwargs) -> Optional[pd.DataFrame]:
        """
        执行数据导入。

        :param chunksize: 分块读取大小，用于大文件处理
        :param kwargs: 传递给具体导入方法的参数
        :return: Pandas DataFrame 或 None
        """
        logger.info(f"开始导入数据")

        try:
            if self.is_database:
                if self._db_importer is None:
                    raise RuntimeError("数据库导入器未初始化")
                return self._db_importer.select_db_import_type(**kwargs)
            else:
                if self._file_importer is None:
                    raise RuntimeError("文件导入器未初始化")
                
                # 获取文件大小，如果大于100MB则启用分块读取
                file_size_mb = os.path.getsize(self.file_resource) / (1024 * 1024)
                if chunksize is None and file_size_mb > 100:
                    logger.info(f"检测到大文件 ({file_size_mb:.2f} MB)，启用分块读取")
                    chunksize = 10000  # 默认分块大小为10000行
                    
                return self._file_importer.select_import_type(chunksize=chunksize)
        except Exception as e:
            logger.error(f"导入错误: {e}")
            print(f"导入错误: {e}")
            return None
        
        finally:
            logger.info(f"数据导入完成")

    def close_connection(self) -> None:
        """关闭数据库连接（如果是数据库模式）"""
        if self._db_importer is not None:
            self._db_importer.close_connection()

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """自动关闭数据库连接"""
        self.close_connection()

    def __del__(self):
        """安全兜底"""
        try:
            self.close_connection()
        except:
            pass  # 忽略