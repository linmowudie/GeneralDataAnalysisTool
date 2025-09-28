"""
Src/DataAnalyzer/importer/db_import.py
数据库导入模块

该模块提供从各种数据库导入数据的功能，支持MySQL、PostgreSQL等
常见数据库类型，通过SQLAlchemy实现数据库连接和查询。
"""

import pandas as pd
from typing import Optional, Union
from pathlib import Path
import logging
from sqlalchemy.exc import SQLAlchemyError

# 导入新的数据库处理模块
from .DataBaseDealing import DatabaseHandlerFactory, BaseDatabaseHandler
from ..Configs.config_manager import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseImport:
    """
    一个用于从各种数据库导入数据到 Pandas DataFrame 的类。
    使用 SQLAlchemy 创建数据库连接引擎。
    """

    # 支持的数据库类型
    supported_databases = DATABASE_CONFIG["supported_databases"]

    def __init__(self, connection_string: str, db_type: str) -> None:
        """
        初始化 DatabaseImport 实例。
        
        :param connection_string: 数据库连接字符串 (connection string)。
                                  对于 SQLite，可以直接是文件路径。
                                  对于其他数据库，应包含用户、密码、主机、端口、数据库名等信息。
                                  例如: 
                                  - MySQL: 'username:password@localhost:3306/mydatabase'
                                  - PostgreSQL: 'username:password@localhost:5432/mydatabase'
                                  - MSSQL: 'username:password@localhost:1433/mydatabase?driver=ODBC+Driver+17+for+SQL+Server'
                                  - MongoDB: 'mongodb://username:password@localhost:27017/mydatabase'
                                  - Redis: 'redis://localhost:6379'
        :param db_type: 数据库类型 ('sqlite', 'mysql', 'postgresql', 'mssql', 'oracle', 'mongodb', 'redis')。
                        如果未提供，尝试从 connection_string 推断或默认为 'sqlite'（如果路径以 .db, .sqlite, .sqlite3 结尾）。
        :raises ValueError: 当数据库类型不支持或连接字符串无效时。
        """
        self.connection_string = connection_string
        self.db_type = db_type.lower() if db_type else self._infer_db_type(connection_string)
        
        if self.db_type not in self.supported_databases:
            error_msg = f"不支持数据库类型{self.db_type}；可用类型：{list(self.supported_databases.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 创建数据库处理器
        self.db_handler: Optional[BaseDatabaseHandler] = None
        self._create_handler()

    def _infer_db_type(self, conn_str: str) -> str:
        """
        尝试从连接字符串推断数据库类型。
        如果无法推断，则默认为 'sqlite'（假设 conn_str 是一个文件路径）。
        
        :param conn_str: 连接字符串
        :return: 推断出的数据库类型
        """
        # 尝试通过常见的主机名或端口前缀来判断
        if '://' in conn_str:
            # 如果连接字符串已经包含了协议，尝试解析
            protocol = conn_str.split('://')[0].lower()
            for key, dialect in self.supported_databases.items():
                if dialect.split('+')[0] == protocol or protocol in dialect:
                    return key

        # 检查是否是 SQLite 文件路径 (常见扩展名)
        path = Path(conn_str)
        if path.suffix.lower() in ['.db', '.db3', '.sqlite', '.sqlite3', '.s3db']:
            return 'sqlite'

        # 默认返回 sqlite，假设输入的是 SQLite 文件路径
        return 'sqlite'

    def _create_handler(self) -> None:
        """
        根据数据库类型创建相应的处理器。
        """
        try:
            self.db_handler = DatabaseHandlerFactory.create_handler(
                self.connection_string, 
                self.db_type
            )
            logger.info(f"数据库处理器成功创建：{self.db_type}.")
        except Exception as e:
            error_msg = f"{self.db_type}处理器创建失败: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def select_db_import_type(self, query: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        执行 SQL 查询并返回结果作为 Pandas DataFrame。
        
        :param query: 要执行的 SQL 查询语句 (可以是 SELECT 语句或表名)。
                      对于 MongoDB，可以是集合名称。
                      对于 Redis，可以是键名。
                      如果提供的是表名，`read_sql` 会自动执行 SELECT *。
        :param kwargs: 传递给 pandas.read_sql 的额外参数。
                       例如: params (用于参数化查询), chunksize 等。
        :return: 包含查询结果的 Pandas DataFrame，如果发生错误则返回 None。
        """
        if self.db_handler is None:
            error_msg = "数据库处理器不可用，无法执行查询。"
            logger.error(error_msg)
            print(error_msg)
            return None

        try:
            df = self.db_handler.query_data(query, **kwargs)
            logger.info(f"Successfully executed query on {self.db_type} database.")
            return df
        except SQLAlchemyError as e:
            # 捕获 SQLAlchemy 特定的异常
            error_msg = f"在 {self.db_type} 上执行查询时发生 SQLAlchemy 错误: {e}"
            logger.error(error_msg)
            print(error_msg)
            return None
        except pd.errors.DatabaseError as e:
            # 捕获 Pandas 数据库相关的错误
            error_msg = f"从 {self.db_type} 读取数据时发生数据库错误: {e}"
            logger.error(error_msg)
            print(error_msg)
            return None
        except Exception as e:
            # 捕获其他可能的异常
            error_msg = f"从 {self.db_type} 读取数据时发生未预期的错误: {e}"
            logger.error(error_msg)
            print(error_msg)
            return None

    def close_connection(self) -> None:
        """
        显式关闭数据库连接引擎。
        """
        if self.db_handler:
            self.db_handler.close_connection()
            logger.info("数据库连接关闭。")

    def __del__(self):
        """
        析构函数，确保在对象销毁时关闭连接。
        """
        self.close_connection()