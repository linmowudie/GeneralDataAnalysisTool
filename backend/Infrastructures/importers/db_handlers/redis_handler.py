"""
Redis 数据库处理类
"""

import pandas as pd
from typing import Optional
import redis
import json
import logging
from .base_handler import BaseDatabaseHandler

logger = logging.getLogger(__name__)


class RedisHandler(BaseDatabaseHandler):
    """
    Redis 数据库处理类
    """
    
    def create_engine(self) -> None:
        """
        Redis 不需要创建传统意义上的引擎
        """
        pass
    
    def query_data(self, query: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        从 Redis 查询数据
        :param query: 键名
        :param kwargs: 其他参数
        :return: DataFrame 或 None
        """
        try:
            # 解析 Redis 连接字符串，使用 decode_responses=True 自动解码响应
            r = redis.from_url(self.connection_string, decode_responses=True)
            
            # 获取键值
            value = r.get(query)
            if value:
                try:
                    # 尝试解析为 JSON
                    data = json.loads(value)
                    df = pd.DataFrame(data if isinstance(data, list) else [data])
                except json.JSONDecodeError:
                    # 如果不是 JSON，创建包含单个值的 DataFrame
                    df = pd.DataFrame([{query: value}])
                except Exception as e:
                    # 处理其他可能的解析错误
                    logger.warning(f"解析Redis数据时出错: {e}")
                    df = pd.DataFrame([{query: value}])
            else:
                # 键不存在
                df = pd.DataFrame()
            
            logger.info("成功在 Redis 数据库上执行查询")
            return df
        except Exception as e:
            error_msg = f"从 Redis 读取数据时发生错误: {e}"
            logger.error(error_msg)
            print(error_msg)
            return None