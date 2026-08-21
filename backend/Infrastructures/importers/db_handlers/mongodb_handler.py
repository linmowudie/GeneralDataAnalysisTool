"""
MongoDB 数据库处理类
"""

import pandas as pd
from typing import Optional
from pymongo import MongoClient
import logging
from .base_handler import BaseDatabaseHandler

logger = logging.getLogger(__name__)


class MongoDBHandler(BaseDatabaseHandler):
    """
    MongoDB 数据库处理类
    """
    
    def create_engine(self) -> None:
        """
        MongoDB 不需要创建传统意义上的引擎
        """
        pass
    
    def query_data(self, query: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        从 MongoDB 查询数据
        :param query: 集合名称
        :param kwargs: 其他参数
        :return: DataFrame 或 None
        """
        try:
            # 解析 MongoDB 连接字符串
            client = MongoClient(self.connection_string)
            
            # 从连接字符串中提取数据库名称
            db_name = self.connection_string.split('/')[-1].split('?')[0]
            db = client[db_name]
            
            # 查询数据
            collection = db[query]
            data = list(collection.find())
            
            # 转换 ObjectId 为字符串
            for doc in data:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            # 转换为 DataFrame
            df = pd.DataFrame(data)
            logger.info("成功在 MongoDB 数据库上执行查询")
            return df
        except Exception as e:
            error_msg = f"从 MongoDB 读取数据时发生错误: {e}"
            logger.error(error_msg)
            print(error_msg)
            return None