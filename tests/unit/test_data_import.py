"""
数据导入模块单元测试（backend.Infrastructures.importers：FileImporter / DbImporter）
"""

import unittest
import sys
import os
import pandas as pd

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.Infrastructures.importers import FileImporter, DbImporter
from backend.shared.types import ImportError_


class TestDataImport(unittest.TestCase):
    """测试文件与数据库导入器"""

    def setUp(self):
        """测试前准备"""
        self.file_importer = FileImporter()
        self.db_importer = DbImporter()
        self.iris_csv = os.path.join(PROJECT_ROOT, "Data", "iris.csv")
        self.test_db = os.path.join(PROJECT_ROOT, "Data", "iris_test.db")

    def test_file_import_success(self):
        """测试文件导入成功"""
        df = self.file_importer.read(self.iris_csv)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)

    def test_file_import_failure(self):
        """测试文件导入失败抛出 ImportError_"""
        with self.assertRaises(ImportError_):
            self.file_importer.read("not_exist_file.csv")

    def test_database_import_without_connection_string(self):
        """测试数据库导入时缺少连接字符串"""
        with self.assertRaises(ImportError_) as context:
            self.db_importer.read("test_table", "sqlite", "")
        self.assertIn("导入数据库时，请提供数据库连接信息", str(context.exception))

    def test_database_import_unsupported_type(self):
        """测试不支持的数据库类型"""
        with self.assertRaises(ImportError_) as context:
            self.db_importer.read("test_table", "unknown_db", "sqlite:///test.db")
        self.assertIn("不支持数据库类型", str(context.exception))

    def test_database_import_success(self):
        """测试从 sqlite 数据库导入成功（若测试库存在）"""
        if not os.path.exists(self.test_db):
            self.skipTest("测试数据库不存在")
        conn_str = f"sqlite:///{self.test_db}"
        df = self.db_importer.read("iris", "sqlite", conn_str)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)

    def test_database_import_with_query(self):
        """测试使用自定义 SQL 查询导入"""
        if not os.path.exists(self.test_db):
            self.skipTest("测试数据库不存在")
        conn_str = f"sqlite:///{self.test_db}"
        df = self.db_importer.read(
            "iris", "sqlite", conn_str, query="SELECT * FROM iris LIMIT 5"
        )
        self.assertIsInstance(df, pd.DataFrame)
        self.assertLessEqual(len(df), 5)

    def test_database_import_invalid_query(self):
        """测试无效 SQL 查询抛出 ImportError_"""
        if not os.path.exists(self.test_db):
            self.skipTest("测试数据库不存在")
        conn_str = f"sqlite:///{self.test_db}"
        with self.assertRaises(ImportError_):
            self.db_importer.read("no_such_table", "sqlite", conn_str)


if __name__ == '__main__':
    unittest.main()
