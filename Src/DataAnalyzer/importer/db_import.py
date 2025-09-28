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
from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class DatabaseImport:
    """
    一个用于从各种数据库导入数据到 Pandas DataFrame 的类。
    使用 SQLAlchemy 创建数据库连接引擎。
    """

    # 支持的数据库类型及其对应的 SQLAlchemy 方言 (dialect)
    # 格式: {'数据库标识': 'SQLAlchemy 方言前缀'}
    supported_databases = {
        'sqlite': 'sqlite',
        'mysql': 'mysql+pymysql',  # 可以根据需要更换为 mysql+mysqlconnector, mysql+mysqldb 等
        
        'postgresql': 'postgresql+psycopg2', # 可以根据需要更换为 postgresql+pg8000 等
        
        'mssql': 'mssql+pyodbc', # Microsoft SQL Server
        
        'oracle': 'oracle+cx_oracle',
        'mongodb': 'mongodb',  # MongoDB (需要 pymongo)
        
        'redis': 'redis',      # Redis (需要 redis-py)
        
        # 可以添加更多支持的数据库
    }

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
        
        self.engine: Optional[Engine] = None
        self._create_engine()

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

    def _create_engine(self) -> None:
        """
        根据数据库类型和连接信息创建 SQLAlchemy 引擎。
        :raises ValueError: 当创建引擎失败时。
        """
        try:
            dialect = self.supported_databases[self.db_type]
            
            if self.db_type == 'sqlite':
                # SQLite 直接使用文件路径
                # 确保路径是绝对路径
                db_path = Path(self.connection_string).resolve()

                # 检查文件是否存在（可选）
                # if not db_path.exists():
                #     logging.warning(f"SQLite database file does not exist: {db_path}. It will be created upon first connection.")
                connection_url = f"{dialect}:///{db_path}"
            
            elif self.db_type == 'mongodb':
                # MongoDB 使用标准连接字符串
                connection_url = self.connection_string
            
            elif self.db_type == 'redis':
                # Redis 使用标准连接字符串
                connection_url = self.connection_string
            
            else:
                # 对于其他数据库，构建连接 URL
                # 这里假设 connection_string 是 'user:password@host:port/database' 格式
                # 更健壮的实现应该使用 urllib.parse 来解析
                connection_url = f"{dialect}://{self.connection_string}"
            
            self.engine = create_engine(connection_url)
            logger.info(f"数据库引擎成功创建：{self.db_type}.")

        except Exception as e:
            error_msg = f"{self.db_type}引擎创建失败: {e}"
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
        if self.engine is None:
            error_msg = "数据库引擎不可用，无法执行查询。"
            logger.error(error_msg)
            print(error_msg)
            return None

        try:
            # 特殊处理 MongoDB
            if self.db_type == 'mongodb':
                from pymongo import MongoClient
                import json
                
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
                logger.info(f"成功在 {self.db_type} 数据库上执行查询。")
                return df
            
            # 特殊处理 Redis
            elif self.db_type == 'redis':
                import redis
                import json
                
                # 解析 Redis 连接字符串
                r = redis.from_url(self.connection_string)

                # 获取键值
                value = r.get(query)
                if value:
                    try:
                        # 尝试解析为 JSON
                        data = json.loads(value)
                        df = pd.DataFrame(data if isinstance(data, list) else [data])
                    except json.JSONDecodeError:
                        # 如果不是 JSON，创建包含单个值的 DataFrame
                        df = pd.DataFrame([{query: value.decode('utf-8') if isinstance(value, bytes) else value}])
                    except Exception as e:
                        # 处理其他可能的解析错误
                        logger.warning(f"解析Redis数据时出错: {e}")
                        df = pd.DataFrame([{query: value.decode('utf-8') if isinstance(value, bytes) else value}])
                else:
                    # 键不存在
                    df = pd.DataFrame()
                
                logger.info(f"成功在 {self.db_type} 数据库上执行查询。")
                return df
            
            # 使用 pandas.read_sql 执行查询（传统 SQL 数据库）
            else:
                df = pd.read_sql(sql=query, con=self.engine, **kwargs)
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
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接关闭。")
            self.engine = None

    def __del__(self):
        """
        析构函数，确保在对象销毁时关闭连接。
        """
        self.close_connection()