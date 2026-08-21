"""
交互式可视化模块单元测试
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

from backend.Models.visualization import DataVisualization
from backend.Models.visualization.interactive import InteractiveVisualization
from backend.Models.visualization.interactive_registry import interactive_plot_registry


class TestInteractiveVisualization(unittest.TestCase):
    """测试交互式可视化功能"""

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
            'target': pd.Series([3, 6, 9, 12, 15]),
            'predict': pd.Series([2.9, 6.1, 8.8, 12.2, 14.9]),
            'interactive': True
        }
        
        # 创建一个不支持的模型测试数据
        self.unsupported_params = {
            'task_type': 'regression',
            'model_name': 'unsupported_model',
            'feature': pd.DataFrame({
                'feature1': [1, 2, 3, 4, 5],
                'feature2': [2, 4, 6, 8, 10]
            }),
            'target': pd.Series([3, 6, 9, 12, 15]),
            'predict': pd.Series([2.9, 6.1, 8.8, 12.2, 14.9]),
            'interactive': True
        }
        
        # 创建3D测试数据
        self.test_3d_params = {
            'task_type': 'transformer',
            'model_name': '3d',
            'feature': pd.DataFrame({
                'x': [1, 2, 3, 4, 5],
                'y': [2, 4, 6, 8, 10],
                'z': [3, 6, 9, 12, 15]
            }),
            'interactive': True
        }
        
    def test_interactive_visualization_initialization(self):
        """测试交互式可视化初始化"""
        visualizer = DataVisualization(self.test_params)
        
        self.assertEqual(visualizer.param_dict, self.test_params)
        self.assertTrue(visualizer.param_dict.get("interactive", False))
        
    def test_interactive_visualization_plot_chart_not_implemented(self):
        """测试交互式图表绘制方法未实现的情况"""
        # 创建可视化器并执行绘图
        visualizer = DataVisualization(self.unsupported_params)
        
        # 由于我们没有实际的注册函数，这里会抛出NotImplementedError
        with self.assertRaises(NotImplementedError):
            result = visualizer.plot_chart()
            
    def test_interactive_visualization_plot_chart_implemented(self):
        """测试交互式图表绘制方法已实现的情况"""
        # 创建可视化器并执行绘图
        visualizer = DataVisualization(self.test_params)
        
        # 由于linearregression有实现的交互式可视化函数，应该不会抛出异常
        try:
            result = visualizer.plot_chart()
            # 结果应该是一个字典
            self.assertIsInstance(result, dict)
        except NotImplementedError:
            # 如果出现NotImplementedError，说明测试失败
            self.fail("plot_chart() raised NotImplementedError unexpectedly!")
            
    def test_interactive_visualization_base_class(self):
        """测试交互式可视化基类"""
        # 创建交互式可视化对象
        interactive_viz = InteractiveVisualization({
            'data': self.test_params['feature'],
            'x': 'feature1',
            'y': 'feature2',
            'title': 'Test Interactive Plot'
        })
        
        self.assertEqual(interactive_viz.title, 'Test Interactive Plot')
        self.assertEqual(interactive_viz.x, 'feature1')
        self.assertEqual(interactive_viz.y, 'feature2')
        
    @patch('backend.Models.visualization.interactive.px')
    def test_interactive_scatter_plot(self, mock_px):
        """测试交互式散点图"""
        mock_fig = MagicMock()
        mock_px.scatter.return_value = mock_fig
        
        # 创建交互式可视化对象
        interactive_viz = InteractiveVisualization({
            'data': self.test_params['feature'],
            'x': 'feature1',
            'y': 'feature2',
            'title': 'Test Interactive Scatter Plot'
        })
        
        # 调用散点图方法
        fig = interactive_viz.scatter_plot()
        
        # 验证
        self.assertEqual(fig, mock_fig)
        mock_px.scatter.assert_called_once()
        
    @patch('backend.Models.visualization.interactive.px')
    def test_interactive_line_plot(self, mock_px):
        """测试交互式折线图"""
        mock_fig = MagicMock()
        mock_px.line.return_value = mock_fig
        
        # 创建交互式可视化对象
        interactive_viz = InteractiveVisualization({
            'data': self.test_params['feature'],
            'x': 'feature1',
            'y': 'feature2',
            'title': 'Test Interactive Line Plot'
        })
        
        # 调用折线图方法
        fig = interactive_viz.line_plot()
        
        # 验证
        self.assertEqual(fig, mock_fig)
        mock_px.line.assert_called_once()
        
    @patch('backend.Models.visualization.interactive.px')
    def test_interactive_bar_plot(self, mock_px):
        """测试交互式条形图"""
        mock_fig = MagicMock()
        mock_px.bar.return_value = mock_fig
        
        # 创建交互式可视化对象
        interactive_viz = InteractiveVisualization({
            'data': self.test_params['feature'],
            'x': 'feature1',
            'y': 'feature2',
            'title': 'Test Interactive Bar Plot'
        })
        
        # 调用条形图方法
        fig = interactive_viz.bar_plot()
        
        # 验证
        self.assertEqual(fig, mock_fig)
        mock_px.bar.assert_called_once()
        
    def test_interactive_plot_registry(self):
        """测试交互式可视化注册表"""
        # 创建注册表实例
        registry = interactive_plot_registry
        
        # 验证注册表初始化
        self.assertIsInstance(registry._registry, dict)
        
        # 测试注册装饰器
        mock_func = Mock()
        registry.register("test_task", "test_model")(mock_func)
        
        # 验证函数已注册
        registered_func = registry.get_plot_function("test_task", "test_model")
        self.assertEqual(registered_func, mock_func)
        
    def test_interactive_visualization_with_3d_data(self):
        """测试3D数据的交互式可视化"""
        visualizer = DataVisualization(self.test_3d_params)
        
        self.assertEqual(visualizer.param_dict, self.test_3d_params)
        self.assertTrue(visualizer.param_dict.get("interactive", False))
        
    def test_static_vs_interactive_visualization(self):
        """测试静态和交互式可视化的切换"""
        # 静态可视化
        static_params = self.test_params.copy()
        static_params['interactive'] = False
        static_visualizer = DataVisualization(static_params)
        
        # 交互式可视化
        interactive_visualizer = DataVisualization(self.test_params)
        
        # 验证参数设置
        self.assertFalse(static_visualizer.param_dict.get("interactive", True))
        self.assertTrue(interactive_visualizer.param_dict.get("interactive", False))


if __name__ == '__main__':
    unittest.main()