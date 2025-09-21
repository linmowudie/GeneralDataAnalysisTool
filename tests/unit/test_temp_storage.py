"""
临时存储管理器单元测试
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
import pickle
from unittest.mock import Mock, patch, MagicMock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.data_analyzer.temp_storage.manager import TempStorageManager


class TestTempStorageManager(unittest.TestCase):
    """测试临时存储管理器"""

    def setUp(self):
        """测试前准备"""
        self.base_path = "Src/data_analyzer/temp_storage"
        self.manager = TempStorageManager(self.base_path)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertTrue(os.path.exists(self.manager.imported_path))
        self.assertTrue(os.path.exists(self.manager.cleaned_path))
        self.assertTrue(os.path.exists(self.manager.analyzed_path))
        self.assertTrue(os.path.exists(self.manager.visualized_path))
        
    def test_save_and_load_data(self):
        """测试保存和加载数据"""
        # 创建测试数据
        test_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        
        # 保存数据
        file_path = self.manager.save_data(test_data, 'imported', 'test_data.pkl')
        
        # 验证文件已创建
        self.assertTrue(os.path.exists(file_path))
        
        # 加载数据
        loaded_data = self.manager.load_data('imported', 'test_data.pkl')
        
        # 验证数据一致性
        pd.testing.assert_frame_equal(test_data, loaded_data)
        
    def test_save_and_load_non_dataframe(self):
        """测试保存和加载非DataFrame数据"""
        # 创建测试数据
        test_data = {'key1': 'value1', 'key2': [1, 2, 3]}
        
        # 保存数据
        file_path = self.manager.save_data(test_data, 'imported', 'test_dict.pkl')
        
        # 验证文件已创建
        self.assertTrue(os.path.exists(file_path))
        
        # 加载数据
        loaded_data = self.manager.load_data('imported', 'test_dict.pkl')
        
        # 验证数据一致性
        self.assertEqual(test_data, loaded_data)
        
    def test_save_large_dataframe_as_parquet(self):
        """测试保存大数据DataFrame为parquet格式"""
        # 创建大型测试数据
        large_data = pd.DataFrame({
            'A': range(10001),  # 超过10000行
            'B': range(10001, 20002)
        })
        
        # 保存数据
        file_path = self.manager.save_data(large_data, 'imported', 'large_data.pkl')
        
        # 验证保存为parquet格式
        self.assertTrue(str(file_path).endswith('.parquet'))
        self.assertTrue(os.path.exists(file_path))
        
    def test_load_nonexistent_data(self):
        """测试加载不存在的数据"""
        loaded_data = self.manager.load_data('imported', 'nonexistent.pkl')
        self.assertIsNone(loaded_data)
        
    def test_clear_stage_data(self):
        """测试清理阶段数据"""
        # 创建测试数据并保存
        test_data = pd.DataFrame({'A': [1, 2, 3]})
        self.manager.save_data(test_data, 'imported', 'test_data.pkl')
        
        # 验证文件存在
        file_path = self.manager.imported_path / 'test_data.pkl'
        self.assertTrue(os.path.exists(file_path))
        
        # 清理数据
        self.manager.clear_stage_data('imported')
        
        # 验证文件已被删除
        self.assertFalse(os.path.exists(file_path))
        
    def test_clear_all_data(self):
        """测试清理所有数据"""
        # 创建测试数据并保存到各个阶段
        test_data = pd.DataFrame({'A': [1, 2, 3]})
        self.manager.save_data(test_data, 'imported', 'test1.pkl')
        self.manager.save_data(test_data, 'cleaned', 'test2.pkl')
        self.manager.save_data(test_data, 'analyzed', 'test3.pkl')
        self.manager.save_data(test_data, 'visualized', 'test4.pkl')
        
        # 验证文件存在
        self.assertTrue(os.path.exists(self.manager.imported_path / 'test1.pkl'))
        self.assertTrue(os.path.exists(self.manager.cleaned_path / 'test2.pkl'))
        self.assertTrue(os.path.exists(self.manager.analyzed_path / 'test3.pkl'))
        self.assertTrue(os.path.exists(self.manager.visualized_path / 'test4.pkl'))
        
        # 清理所有数据
        self.manager.clear_all_data()
        
        # 验证所有文件已被删除
        self.assertFalse(os.path.exists(self.manager.imported_path / 'test1.pkl'))
        self.assertFalse(os.path.exists(self.manager.cleaned_path / 'test2.pkl'))
        self.assertFalse(os.path.exists(self.manager.analyzed_path / 'test3.pkl'))
        self.assertFalse(os.path.exists(self.manager.visualized_path / 'test4.pkl'))
        
    def test_invalid_stage(self):
        """测试使用无效阶段"""
        with self.assertRaises(ValueError) as context:
            self.manager.save_data("test", "invalid_stage", "test.pkl")
            
        self.assertIn("不支持的阶段", str(context.exception))


if __name__ == '__main__':
    unittest.main()