"""
文件导入模块单元测试（backend.Infrastructures.importers.file_importer.FileImporter）
"""

import unittest
import sys
import os
import pandas as pd
from unittest.mock import patch

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.Infrastructures.importers.file_importer import FileImporter
from backend.shared.types import ImportError_


class TestFileImporter(unittest.TestCase):
    """测试 FileImporter 类"""

    def setUp(self):
        """测试前准备"""
        self.importer = FileImporter()
        self.iris_csv = os.path.join(PROJECT_ROOT, "Data", "iris.csv")

    def test_read_csv_success(self):
        """测试读取真实 CSV 文件"""
        df = self.importer.read(self.iris_csv)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)

    def test_read_with_explicit_file_type(self):
        """测试显式指定文件类型"""
        df = self.importer.read(self.iris_csv, file_type="csv")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)

    def test_read_nonexistent_file(self):
        """测试读取不存在的文件抛出 ImportError_"""
        with self.assertRaises(ImportError_) as context:
            self.importer.read("not_exist_file.csv")
        self.assertIn("文件不存在", str(context.exception))

    def test_read_unsupported_file_type(self):
        """测试不支持的文件类型抛出 ImportError_"""
        with self.assertRaises(ImportError_) as context:
            self.importer.read(self.iris_csv, file_type="txt")
        self.assertIn("不支持的文件类型", str(context.exception))

    @patch('pandas.read_csv')
    def test_read_csv_with_chunksize(self, mock_read_csv):
        """测试CSV分块读取"""
        # 设置mock：nrows=0 取表头；chunksize 返回迭代器
        header_df = pd.DataFrame(columns=['A', 'B'])
        chunk1 = pd.DataFrame({'A': [1, 2], 'B': [4, 5]})
        chunk2 = pd.DataFrame({'A': [3], 'B': [6]})

        def side_effect(*args, **kwargs):
            if kwargs.get('nrows') == 0:
                return header_df
            return iter([chunk1, chunk2])

        mock_read_csv.side_effect = side_effect

        result = self.importer.read(self.iris_csv, chunksize=2)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)

    def test_read_json_success(self):
        """测试读取 JSON 文件"""
        json_path = os.path.join(PROJECT_ROOT, "Data", "iris.json")
        if os.path.exists(json_path):
            df = self.importer.read(json_path)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)

    def test_read_excel_success(self):
        """测试读取 Excel 文件"""
        xlsx_path = os.path.join(PROJECT_ROOT, "Data", "iris.xlsx")
        if os.path.exists(xlsx_path):
            df = self.importer.read(xlsx_path)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)


if __name__ == '__main__':
    unittest.main()
