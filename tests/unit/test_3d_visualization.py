"""
3D可视化模块单元测试
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
from Src.DataAnalyzer.VisualizationModule.interactive import InteractiveVisualization


class Test3DVisualization(unittest.TestCase):
    """测试3D可视化功能"""

    def setUp(self):
        """测试前准备"""
        # 创建3D测试数据
        self.test_3d_params = {
            'task_type': 'transformer',
            'model_name': '3d',
            'feature': pd.DataFrame({
                'x': [1, 2, 3, 4, 5],
                'y': [2, 4, 6, 8, 10],
                'z': [3, 6, 9, 12, 15]
            })
        }
        
        # 创建交互式3D测试数据
        self.interactive_3d_params = {
            'task_type': 'transformer',
            'model_name': '3d',
            'feature': pd.DataFrame({
                'x': [1, 2, 3, 4, 5],
                'y': [2, 4, 6, 8, 10],
                'z': [3, 6, 9, 12, 15]
            }),
            'interactive': True
        }
        
    def test_3d_visualization_initialization(self):
        """测试3D可视化初始化"""
        visualizer = DataVisualization(self.test_3d_params)
        
        self.assertEqual(visualizer.param_dict, self.test_3d_params)
        
    def test_interactive_3d_visualization_initialization(self):
        """测试交互式3D可视化初始化"""
        visualizer = DataVisualization(self.interactive_3d_params)
        
        self.assertEqual(visualizer.param_dict, self.interactive_3d_params)
        self.assertTrue(visualizer.param_dict.get("interactive", False))
        
    def test_3d_visualization_base_class(self):
        """测试3D可视化基类"""
        # 创建交互式可视化对象
        interactive_viz = InteractiveVisualization({
            'data': self.test_3d_params['feature'],
            'x': 'x',
            'y': 'y',
            'z': 'z',
            'title': 'Test 3D Plot'
        })
        
        self.assertEqual(interactive_viz.title, 'Test 3D Plot')
        self.assertEqual(interactive_viz.x, 'x')
        self.assertEqual(interactive_viz.y, 'y')
        self.assertEqual(interactive_viz.params.get('z'), 'z')
        
    def test_static_vs_interactive_3d_visualization(self):
        """测试静态和交互式3D可视化的切换"""
        # 静态3D可视化
        static_visualizer = DataVisualization(self.test_3d_params)
        
        # 交互式3D可视化
        interactive_visualizer = DataVisualization(self.interactive_3d_params)
        
        # 验证参数设置
        self.assertFalse(static_visualizer.param_dict.get("interactive", False))
        self.assertTrue(interactive_visualizer.param_dict.get("interactive", False))


if __name__ == '__main__':
    unittest.main()