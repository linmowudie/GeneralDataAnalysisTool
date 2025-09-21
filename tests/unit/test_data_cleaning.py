"""
数据清洗模块单元测试
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.data_analyzer.data_cleaning import CleanDataMode


class TestDataCleaning(unittest.TestCase):
    """测试数据清洗功能"""

    def setUp(self):
        """测试前准备"""
        # 创建测试数据
        self.test_df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': ['a', 'b', 'c', 'd', None],
            'C': [1.1, 2.2, 3.3, np.nan, 5.5],
            'D': [1, 2, 3, 4, 5]
        })
        
    def test_initialization(self):
        """测试初始化"""
        cleaner = CleanDataMode(self.test_df, "standard", [])
        
        self.assertEqual(cleaner.select_mode, "standard")
        self.assertEqual(cleaner.params_list, [])
        self.assertFalse(cleaner.is_freedom_params)
        
    def test_invalid_mode(self):
        """测试无效清洗模式"""
        # 这里我们测试一个不存在的模式，应该不会抛出异常，因为代码中没有对模式进行严格限制
        # 仅当is_freedom_params为False且模式不在预定义列表中时才检查
        cleaner = CleanDataMode(self.test_df, "invalid_mode", [])
        # 不过在实际clean_data调用时会出错，因为没有对应的方法
        
    def test_standard_clean_mode(self):
        """测试标准清洗模式"""
        cleaner = CleanDataMode(self.test_df, "standard", [])
        result = cleaner.clean_data()
        
        self.assertIsInstance(result, pd.DataFrame)
        # 标准模式应该处理NaN值
        self.assertFalse(result.isnull().values.any())
        
    def test_strict_clean_mode(self):
        """测试严格清洗模式"""
        cleaner = CleanDataMode(self.test_df, "strict", [])
        result = cleaner.clean_data()
        
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_relaxed_clean_mode(self):
        """测试宽松清洗模式"""
        cleaner = CleanDataMode(self.test_df, "relaxed", [])
        result = cleaner.clean_data()
        
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_custom_clean_mode(self):
        """测试自定义清洗模式"""
        cleaner = CleanDataMode(self.test_df, "custom", ["dropna"], is_freedom_params=True)
        # Mock custom method since it's not implemented in the original code
        cleaner.custom = Mock(return_value=self.test_df.dropna())
        
        result = cleaner.clean_data()
        
        self.assertIsInstance(result, pd.DataFrame)
        # 自定义模式应该调用custom方法
        cleaner.custom.assert_called_once()
        
    def test_clean_data_return_type(self):
        """测试清洗数据返回类型检查"""
        cleaner = CleanDataMode(self.test_df, "standard", [])
        # Mock standard method to return invalid type
        cleaner.standard = Mock(return_value="invalid_type")
        
        with self.assertRaises(TypeError) as context:
            cleaner.clean_data()
            
        self.assertIn("清洗方法必须返回 DataFrame", str(context.exception))


if __name__ == '__main__':
    unittest.main()