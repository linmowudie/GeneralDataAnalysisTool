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

from Src.DataAnalyzer.ModuleInterfaces.data_visualization import DataVisualization


class TestDataVisualization(unittest.TestCase):
    """测试数据可视化功能"""

    def setUp(self):
        """测试前准备"""
        # 创建测试数据
        self.test_params = {
            'task_type': 'regression',
            'model_name': 'linearregression',
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
        
    def test_plot_chart_method(self):
        """测试图表绘制方法"""
        # 创建可视化器并执行绘图
        visualizer = DataVisualization(self.test_params)
        result = visualizer.plot_chart()
        
        # 验证
        self.assertIsInstance(result, dict)
        
    def test_plot_chart_without_feature_data(self):
        """测试没有特征数据时的图表绘制"""
        params = self.test_params.copy()
        del params['feature']  # 删除特征数据以触发错误
        
        visualizer = DataVisualization(params)
        
        # 应该抛出ValueError异常
        with self.assertRaises(ValueError):
            visualizer.plot_chart()


if __name__ == '__main__':
    unittest.main()