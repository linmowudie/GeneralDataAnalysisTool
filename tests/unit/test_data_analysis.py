"""
数据分析模块单元测试
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

from backend.Models.analysis import DataAnalyzer


class TestDataAnalysis(unittest.TestCase):
    """测试数据分析功能"""

    def setUp(self):
        """测试前准备"""
        # 创建测试数据
        self.test_df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [2, 4, 6, 8, 10],
            'target': [0, 1, 0, 1, 0]
        })
        
    def test_initialization(self):
        """测试初始化"""
        analyzer = DataAnalyzer(
            df=self.test_df,
            model="linearregression"
        )
        
        self.assertEqual(analyzer.model_name, "linearregression")
        self.assertEqual(analyzer.random_state, 42)
        self.assertTrue(analyzer.is_split)
        self.assertEqual(analyzer.split_ratio, 0.8)
        
    def test_initialization_with_none_df(self):
        """测试使用None初始化"""
        with self.assertRaises(ValueError) as context:
            DataAnalyzer(df=None, model="linearregression")
            
        self.assertIn("数据集不能为空", str(context.exception))
        
    def test_initialization_with_empty_df(self):
        """测试使用空DataFrame初始化"""
        empty_df = pd.DataFrame()
        
        with self.assertRaises(ValueError) as context:
            DataAnalyzer(df=empty_df, model="linearregression")
            
        self.assertIn("数据集为空", str(context.exception))
        
    def test_initialization_with_invalid_target_col(self):
        """测试使用无效目标列初始化"""
        with self.assertRaises(ValueError) as context:
            DataAnalyzer(df=self.test_df, model="linearregression", target_col="invalid_column")
            
        self.assertIn("目标列 'invalid_column' 不存在于数据集列中", str(context.exception))
        
    def test_initialization_with_invalid_feature_cols(self):
        """测试使用无效特征列初始化"""
        with self.assertRaises(ValueError) as context:
            DataAnalyzer(df=self.test_df, model="linearregression", feature_cols=["invalid_column"])
            
        self.assertIn("以下特征列不存在于数据集中", str(context.exception))
        
    def test_analyze_method(self):
        """测试分析方法"""
        # Mock analyze_data 函数（DataAnalyzer.analyze 内部直调）
        with patch('backend.Models.analysis.analyzer.analyze_data') as mock_analyze_data:
            # 创建模拟结果
            mock_result = {
                'trained_model': Mock(),
                'scores': {'accuracy': 0.8},
                'predictions': [0, 1, 0]
            }
            mock_analyze_data.return_value = mock_result
            
            # 创建分析器并执行分析
            analyzer = DataAnalyzer(df=self.test_df, model="linearregression")
            result = analyzer.analyze()
            
            # 验证
            self.assertEqual(result, mock_result)
            mock_analyze_data.assert_called_once()


if __name__ == '__main__':
    unittest.main()