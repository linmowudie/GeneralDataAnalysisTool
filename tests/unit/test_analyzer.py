"""
分析器模块单元测试
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

from Src.DataAnalyzer.AnalysisModule.analyzer import AnalyzeData


class TestAnalyzer(unittest.TestCase):
    """测试分析器功能"""

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
        analyzer = AnalyzeData(
            df=self.test_df,
            model="LinearRegression",
            target_col="target"
        )
        
        self.assertEqual(analyzer.kwargs['df'].shape, self.test_df.shape)
        self.assertEqual(analyzer.kwargs['model'], "LinearRegression")
        self.assertEqual(analyzer.kwargs['random_state'], 42)
        self.assertTrue(analyzer.kwargs['is_split'])
        self.assertEqual(analyzer.kwargs['split_ratio'], 0.8)
        self.assertEqual(analyzer.kwargs['target_col'], "target")
        
    @patch('Src.DataAnalyzer.analysis.analyzer.LinearRegression')
    @patch('sklearn.model_selection.train_test_split')
    def test_run_method_with_split(self, mock_train_test_split, mock_model_class):
        """测试运行方法（带数据分割）"""
        # 创建模拟数据
        X_train = pd.DataFrame({'feature1': [1, 2, 3, 4], 'feature2': [2, 4, 6, 8]})
        X_test = pd.DataFrame({'feature1': [5], 'feature2': [10]})
        y_train = pd.Series([0, 1, 0, 1])
        y_test = pd.Series([0])
        
        mock_train_test_split.return_value = (X_train, X_test, y_train, y_test)
        
        # 创建模拟模型
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.predict.return_value = [0]
        mock_model_class.return_value = mock_model
        
        # 创建分析器并运行
        analyzer = AnalyzeData(
            df=self.test_df, 
            model="LinearRegression", 
            target_col="target",
            is_return_training_set=True  # 确保返回训练集
        )
        result = analyzer.run()
        
        # 验证
        self.assertIsInstance(result, dict)
        self.assertIn('trained_model', result)
        self.assertIn('X_train', result)
        self.assertIn('X_test', result)
        self.assertIn('y_train', result)
        self.assertIn('y_test', result)
        
    @patch('Src.DataAnalyzer.analysis.analyzer.LinearRegression')
    def test_run_method_without_split(self, mock_model_class):
        """测试运行方法（不带数据分割）"""
        # 创建模拟模型
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.predict.return_value = [0, 1, 0, 1, 0]
        mock_model_class.return_value = mock_model
        
        # 创建分析器并运行
        analyzer = AnalyzeData(df=self.test_df, model="LinearRegression", target_col="target", is_split=False)
        result = analyzer.run()
        
        # 验证
        self.assertIsInstance(result, dict)
        self.assertIn('trained_model', result)


if __name__ == '__main__':
    unittest.main()