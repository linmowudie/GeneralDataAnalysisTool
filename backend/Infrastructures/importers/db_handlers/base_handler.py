"""
数据库处理基础类
"""

import pandas as pd
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class BaseDatabaseHandler:
    """
    数据库处理基础类
    """
    
    def __init__(self, connection_string: str, db_type: str):
        self.connection_string = connection_string
        self.db_type = db_type
        self.engine: Optional[Engine] = None
    
    def create_engine(self):
        """
        创建数据库引擎
        """
        raise NotImplementedError("子类必须实现 create_engine 方法")
    
    def query_data(self, query: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        查询数据
        :param query: 查询语句
        :param kwargs: 其他参数
        :return: DataFrame 或 None
        """
        raise NotImplementedError("子类必须实现 query_data 方法")
    
    def close_connection(self) -> None:
        """
        关闭数据库连接
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None