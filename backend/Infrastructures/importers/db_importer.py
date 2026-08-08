"""
backend/Infrastructures/importers/db_importer.py
DbImporter：按连接串读取数据库表或 SQL 查询

统一签名 read(source, **kwargs) -> DataFrame，异常统一抛 ImportError_。
（连接/查询实现原位于 Engine/ImporterModule/db_import.DatabaseImport，已内联；
处理器位于 db_handlers，原 DataBaseDealing）
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from backend.Infrastructures.Configs.config_manager import DATABASE_CONFIG  # noqa: E402
from backend.shared.types import ImportError_  # noqa: E402
from .db_handlers import BaseDatabaseHandler, DatabaseHandlerFactory  # noqa: E402

logger = logging.getLogger(__name__)


class DbImporter:
    """数据库读取器"""

    # 支持的数据库类型（来自 database_config.json）
    SUPPORTED = DATABASE_CONFIG["supported_databases"]

    def read(self, source: str, db_type: str, db_connection_string: str,
             query: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        从数据库读取数据为 DataFrame

        :param source: 表名（当未提供 query 时作为查询目标）
        :param db_type: 数据库类型（sqlite/mysql 等，缺省时从连接串推断）
        :param db_connection_string: 数据库连接字符串
        :param query: SQL 查询语句（缺省为 SELECT * FROM {source}）
        :return: DataFrame
        :raises ImportError_: 读取失败
        """
        if not db_connection_string:
            raise ImportError_("导入数据库时，请提供数据库连接信息")

        effective_query = query or f"SELECT * FROM {source}"
        effective_db_type = (db_type.lower() if db_type
                             else self._infer_db_type(db_connection_string))

        if effective_db_type not in self.SUPPORTED:
            raise ImportError_(
                f"不支持数据库类型 {effective_db_type}；可用类型：{list(self.SUPPORTED.keys())}"
            )

        handler: Optional[BaseDatabaseHandler] = None
        try:
            # SQLiteHandler 期望纯文件路径（原 DataBaseDealing 语义），剥离 URL 前缀
            effective_conn = db_connection_string
            if effective_db_type == "sqlite" and effective_conn.startswith("sqlite:///"):
                effective_conn = effective_conn[len("sqlite:///"):]

            handler = DatabaseHandlerFactory.create_handler(
                effective_conn, effective_db_type
            )
            df = handler.query_data(effective_query, **kwargs)
            if df is None:
                raise ImportError_(f"数据库查询返回空结果: {effective_query}")
            logger.info("数据库查询完成: %s (%s)", effective_query, effective_db_type)
            return df
        except ImportError_:
            raise
        except (SQLAlchemyError, pd.errors.DatabaseError) as e:
            logger.error("数据库查询失败: %s", e, exc_info=True)
            raise ImportError_(f"数据库查询失败: {str(e)}") from e
        except Exception as e:
            logger.error("数据库读取失败: %s", e, exc_info=True)
            raise ImportError_(f"数据库读取失败: {str(e)}") from e
        finally:
            if handler is not None:
                try:
                    handler.close_connection()
                except Exception:
                    pass

    # ------------------------------------------------------------------ 内部
    @classmethod
    def _infer_db_type(cls, conn_str: str) -> str:
        """从连接串推断数据库类型，无法推断时默认 sqlite"""
        if "://" in conn_str:
            protocol = conn_str.split("://")[0].lower()
            for key, dialect in cls.SUPPORTED.items():
                if dialect.split("+")[0] == protocol or protocol in dialect:
                    return key

        path = Path(conn_str)
        if path.suffix.lower() in [".db", ".db3", ".sqlite", ".sqlite3", ".s3db"]:
            return "sqlite"
        return "sqlite"
