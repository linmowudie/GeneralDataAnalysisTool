"""
SQLite 数据库处理类
"""

import pandas as pd
from typing import Optional
from pathlib import Path
from sqlalchemy import create_engine
import logging
from .base_handler import BaseDatabaseHandler

logger = logging.getLogger(__name__)


class SQLiteHandler(BaseDatabaseHandler):
    """
    SQLite 数据库处理类
    """
    
    def create_engine(self) -> None:
        """
        创建 SQLite 数据库引擎
        """
        try:
            # SQLite 直接使用文件路径
            # 确保路径是绝对路径
            db_path = Path(self.connection_string).resolve()
            
            # 检查文件是否存在（可选）
            # if not db_path.exists():
            #     logging.warning(f"SQLite database file does not exist: {db_path}. It will be created upon first connection.")
            connection_url = f"sqlite:///{db_path}"
            self.engine = create_engine(connection_url)
            logger.info(f"SQLite 数据库引擎成功创建")
        except Exception as e:
            error_msg = f"SQLite 引擎创建失败: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def query_data(self, query: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        从 SQLite 数据库查询数据
        :param query: SQL 查询语句
        :param kwargs: 其他参数
        :return: DataFrame 或 None
        """
        try:
            if self.engine is None:
                self.create_engine()
            
            df = pd.read_sql(sql=query, con=self.engine, **kwargs)
            logger.info("成功在 SQLite 数据库上执行查询")
            return df
        except Exception as e:
            error_msg = f"从 SQLite 读取数据时发生错误: {e}"
            logger.error(error_msg)
            print(error_msg)
            return None