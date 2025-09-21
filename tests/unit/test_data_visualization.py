"""
数据可视化模块单元测试
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

from Src.data_analyzer.data_visualization import DataVisualization


class TestDataVisualization(unittest.TestCase):
    """测试数据可视化功能"""

    def setUp(self):
        """测试前准备"""
        # 创建测试数据
        self.test_params = {
            'task_type': 'classification',
            'model_name': 'logisticregression',
            'feature': pd.DataFrame({
                'feature1': [1, 2, 3, 4, 5],
                'feature2': [2, 4, 6, 8, 10]
            }),
            'target': pd.Series([0, 1, 0, 1, 0]),
            'predict': pd.Series([0, 1, 1, 1, 0])
        }
        
    def test_initialization(self):
        """测试初始化"""
        visualizer = DataVisualization(self.test_params)
        
        self.assertEqual(visualizer.param_dict, self.test_params)
        
    @patch('Src.data_analyzer.data_visualization.PlotRegistry')
    def test_plot_chart_method(self, mock_registry):
        """测试图表绘制方法"""
        # 创建模拟绘图器
        mock_plotter = Mock()
        mock_plotter.plot.return_value = {"test_plot": Mock()}
        
        # 创建模拟注册表
        mock_registry_instance = Mock()
        mock_registry_instance.get_plotter.return_value = mock_plotter
        mock_registry.return_value = mock_registry_instance
        
        # 创建可视化器并执行绘图
        visualizer = DataVisualization(self.test_params)
        result = visualizer.plot_chart()
        
        # 验证
        self.assertIsInstance(result, dict)
        mock_registry.assert_called()  # 改为assert_called而不是assert_called_once
        mock_registry_instance.get_plotter.assert_called_once()
        mock_plotter.plot.assert_called_once()
        
    @patch('Src.data_analyzer.data_visualization.PlotRegistry')
    def test_plot_chart_without_feature_data(self, mock_registry):
        """测试没有特征数据时的图表绘制"""
        params = self.test_params.copy()
        params['feature'] = None
        
        # 创建模拟绘图器
        mock_plotter = Mock()
        mock_plotter.plot.return_value = {}
        
        # 创建模拟注册表
        mock_registry_instance = Mock()
        mock_registry_instance.get_plotter.return_value = mock_plotter
        mock_registry.return_value = mock_registry_instance
        
        visualizer = DataVisualization(params)
        result = visualizer.plot_chart()
        
        # 验证返回结果
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()