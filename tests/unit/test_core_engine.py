"""
核心引擎模块单元测试
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

from Src.DataAnalyzer.core import DataProcessingEngine


class TestDataProcessingEngine(unittest.TestCase):
    """测试DataProcessingEngine类"""

    def setUp(self):
        """测试前准备"""
        self.engine = DataProcessingEngine()
        
    def tearDown(self):
        """测试后清理"""
        self.engine.cleanup()

    def test_initialization(self):
        """测试引擎初始化"""
        self.assertIsNone(self.engine.imported_data)
        self.assertIsNone(self.engine.cleaned_data)
        self.assertIsNone(self.engine.analyzed_data)
        self.assertIsNone(self.engine.visualized_plot)
        self.assertIsNone(self.engine.report_data)
        
    def test_import_data_without_data(self):
        """测试在没有数据时导入数据会引发异常"""
        with self.assertRaises(ValueError) as context:
            self.engine.clean_data("standard", [])
            
        self.assertIn("请先导入数据", str(context.exception))
        
    @patch('Src.DataAnalyzer.ModuleInterfaces.data_import.DataImport')
    def test_import_data_success(self, mock_data_import):
        """测试数据导入成功"""
        # 创建模拟数据
        mock_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        mock_import_instance = Mock()
        mock_import_instance.import_data.return_value = mock_df
        mock_data_import.return_value = mock_import_instance
        
        # 执行导入
        self.engine.import_data("test.csv", "csv")
        
        # 验证
        self.assertIsNotNone(self.engine.imported_data)
        mock_data_import.assert_called_once()
        
    @patch('Src.DataAnalyzer.ModuleInterfaces.data_cleaning.CleanDataMode')
    def test_clean_data_success(self, mock_clean_data_mode):
        """测试数据清洗成功"""
        # 准备数据
        self.engine.imported_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        mock_cleaned_df = pd.DataFrame({'A': [1, 2], 'B': [4, 5]})
        
        # 设置mock
        mock_clean_instance = Mock()
        mock_clean_instance.clean_data.return_value = mock_cleaned_df
        mock_clean_data_mode.return_value = mock_clean_instance
        
        # 执行清洗
        self.engine.clean_data("standard", [])
        
        # 验证
        self.assertIsNotNone(self.engine.cleaned_data)
        self.assertEqual(len(self.engine.cleaned_data), 2)
        mock_clean_data_mode.assert_called_once()
        
    def test_clean_data_without_import(self):
        """测试没有导入数据时清洗会引发异常"""
        with self.assertRaises(ValueError) as context:
            self.engine.clean_data("standard", [])
            
        self.assertIn("请先导入数据", str(context.exception))
        
    @patch('Src.DataAnalyzer.ModuleInterfaces.data_analysis.DataAnalyzer')
    def test_analyze_data_success(self, mock_data_analyzer):
        """测试数据分析成功"""
        # 准备数据
        self.engine.cleaned_data = pd.DataFrame({
            'feature1': [1, 2, 3], 
            'feature2': [4, 5, 6], 
            'target': [0, 1, 0]
        })
        
        # 设置mock
        mock_result = {'trained_model': "mock_model", 'scores': [0.8]}
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = mock_result
        mock_data_analyzer.return_value = mock_analyzer_instance
        
        # 执行分析
        self.engine.analyze_data("lr")
        
        # 验证
        self.assertIsNotNone(self.engine.analyzed_data)
        mock_data_analyzer.assert_called_once()
        
    def test_analyze_data_without_clean(self):
        """测试没有清洗数据时分析会引发异常"""
        with self.assertRaises(ValueError) as context:
            self.engine.analyze_data("lr")
            
        self.assertIn("请先进行数据清洗", str(context.exception))


if __name__ == '__main__':
    unittest.main()