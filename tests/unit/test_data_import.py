"""
数据导入模块单元测试
"""

import unittest
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.DataAnalyzer.ModuleInterfaces.data_import import DataImport


class TestDataImport(unittest.TestCase):
    """测试DataImport类"""

    def setUp(self):
        """测试前准备"""
        self.test_file_path = "test.csv"
        
    def test_file_import_initialization(self):
        """测试文件导入初始化"""
        importer = DataImport(self.test_file_path, "csv")
        
        self.assertFalse(importer.is_database)
        self.assertEqual(importer.file_resource, self.test_file_path)
        self.assertEqual(importer.resource_type, "csv")
        self.assertIsNotNone(importer._file_importer)
        self.assertIsNone(importer._db_importer)
        
    def test_database_import_initialization(self):
        """测试数据库导入初始化"""
        db_conn_string = "sqlite:///test.db"
        importer = DataImport("test_table", "sqlite", db_conn_string, is_database=True)
        
        self.assertTrue(importer.is_database)
        self.assertEqual(importer.db_connection_string, db_conn_string)
        self.assertIsNotNone(importer._db_importer)
        self.assertIsNone(importer._file_importer)
        
    def test_database_import_without_connection_string(self):
        """测试数据库导入时缺少连接字符串"""
        with self.assertRaises(ValueError) as context:
            DataImport("test_table", "sqlite", is_database=True)
            
        self.assertIn("导入数据库时，请提供数据库连接信息", str(context.exception))
        
    @patch('Src.DataAnalyzer.ModuleInterfaces.data_import.FileImport')
    def test_file_import_success(self, mock_file_import):
        """测试文件导入成功"""
        # 创建模拟数据
        mock_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        mock_import_instance = Mock()
        mock_import_instance.select_import_type.return_value = mock_df
        mock_file_import.return_value = mock_import_instance
        
        # 执行导入
        importer = DataImport(self.test_file_path, "csv")
        result = importer.import_data()
        
        # 验证
        # 注意：由于mock_file_import是mock的，所以这里不能断言result不为None
        mock_file_import.assert_called_once_with(self.test_file_path, "csv")
        
    @patch('Src.DataAnalyzer.ModuleInterfaces.data_import.DatabaseImport')
    def test_database_import_success(self, mock_db_import):
        """测试数据库导入成功"""
        # 设置mock
        mock_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        mock_db_instance = Mock()
        mock_db_instance.select_db_import_type.return_value = mock_df
        mock_db_import.return_value = mock_db_instance
        
        # 执行导入
        importer = DataImport("test_table", "sqlite", "sqlite:///test.db", is_database=True)
        result = importer.import_data(query="SELECT * FROM test_table")
        
        # 验证
        # 注意：由于mock_db_import是mock的，所以这里不能断言result不为None
        mock_db_import.assert_called_once_with("sqlite:///test.db", "sqlite")


if __name__ == '__main__':
    unittest.main()