"""
通用 SQL 数据库处理类（支持 MySQL、PostgreSQL、MSSQL、Oracle 等）
"""

import pandas as pd
from typing import Optional, Dict
from sqlalchemy import create_engine
import logging
from .base_handler import BaseDatabaseHandler

logger = logging.getLogger(__name__)


class SQLHandler(BaseDatabaseHandler):
    """
    通用 SQL 数据库处理类
    """
    
    # 数据库方言映射
    dialects = {
        'mysql': 'mysql+pymysql',
        'postgresql': 'postgresql+psycopg2',
        'mssql': 'mssql+pyodbc',
        'oracle': 'oracle+cx_oracle'
    }
    
    def __init__(self, connection_string: str, db_type: str):
        super().__init__(connection_string, db_type)
        self.dialect = self.dialects.get(db_type, 'mysql+pymysql')  # 默认使用 MySQL
    
    def create_engine(self) -> None:
        """
        创建 SQL 数据库引擎
        """
        try:
            # 构建连接 URL
            # 这里假设 connection_string 是 'user:password@host:port/database' 格式
            # 更健壮的实现应该使用 urllib.parse 来解析
            connection_url = f"{self.dialect}://{self.connection_string}"
            self.engine = create_engine(connection_url)
            logger.info(f"{self.db_type.upper()} 数据库引擎成功创建")
        except Exception as e:
            error_msg = f"{self.db_type.upper()} 引擎创建失败: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def query_data(self, query: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        从 SQL 数据库查询数据
        :param query: SQL 查询语句
        :param kwargs: 其他参数
        :return: DataFrame 或 None
        """
        try:
            if self.engine is None:
                self.create_engine()
            
            df = pd.read_sql(sql=query, con=self.engine, **kwargs)
            logger.info(f"成功在 {self.db_type.upper()} 数据库上执行查询")
            return df
        except Exception as e:
            error_msg = f"从 {self.db_type.upper()} 读取数据时发生错误: {e}"
            logger.error(error_msg)
            print(error_msg)
            return None