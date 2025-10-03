"""
数据库处理器工厂类
"""

from typing import Dict, Type
from .base_handler import BaseDatabaseHandler
from .sqlite_handler import SQLiteHandler
from .mongodb_handler import MongoDBHandler
from .redis_handler import RedisHandler
from .sql_handler import SQLHandler

class DatabaseHandlerFactory:
    """
    数据库处理器工厂类，用于创建不同数据库类型的处理器实例
    """
    
    # 数据库类型与处理器类的映射
    _handlers: Dict[str, Type[BaseDatabaseHandler]] = {
        'sqlite': SQLiteHandler,
        'mongodb': MongoDBHandler,
        'redis': RedisHandler,
        'mysql': SQLHandler,
        'postgresql': SQLHandler,
        'mssql': SQLHandler,
        'oracle': SQLHandler
    }
    
    @classmethod
    def create_handler(cls, connection_string: str, db_type: str) -> BaseDatabaseHandler:
        """
        创建数据库处理器实例
        :param connection_string: 连接字符串
        :param db_type: 数据库类型
        :return: 数据库处理器实例
        """
        db_type = db_type.lower()
        handler_class = cls._handlers.get(db_type)
        
        if handler_class is None:
            raise ValueError(f"不支持的数据库类型: {db_type}")
        
        return handler_class(connection_string, db_type)
    
    @classmethod
    def register_handler(cls, db_type: str, handler_class: Type[BaseDatabaseHandler]) -> None:
        """
        注册新的数据库处理器
        :param db_type: 数据库类型
        :param handler_class: 处理器类
        """
        cls._handlers[db_type.lower()] = handler_class