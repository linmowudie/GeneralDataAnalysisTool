"""
交互式可视化基类单元测试
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

from backend.Models.visualization.interactive import InteractiveVisualization


class TestInteractiveVisualizationBase(unittest.TestCase):
    """测试交互式可视化基类"""

    def setUp(self):
        """测试前准备"""
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10],
            'category': ['A', 'B', 'A', 'B', 'A']
        })
        
        self.base_params = {
            'data': self.test_data,
            'x': 'x',
            'y': 'y',
            'title': 'Test Interactive Plot',
            'labels': {'x': 'X Axis', 'y': 'Y Axis'},
            'color': 'category',
            'size': None,
            'hover_data': ['category']
        }
        
    def test_initialization(self):
        """测试初始化"""
        viz = InteractiveVisualization(self.base_params)
        
        self.assertEqual(viz.data.shape, self.test_data.shape)
        self.assertEqual(viz.x, 'x')
        self.assertEqual(viz.y, 'y')
        self.assertEqual(viz.title, 'Test Interactive Plot')
        self.assertEqual(viz.labels, {'x': 'X Axis', 'y': 'Y Axis'})
        self.assertEqual(viz.color, 'category')
        self.assertEqual(viz.size, None)
        self.assertEqual(viz.hover_data, ['category'])
        
    @patch('backend.Models.visualization.interactive.px')
    def test_scatter_plot(self, mock_px):
        """测试散点图"""
        mock_fig = MagicMock()
        mock_px.scatter.return_value = mock_fig
        
        viz = InteractiveVisualization(self.base_params)
        fig = viz.scatter_plot()
        
        self.assertEqual(fig, mock_fig)
        mock_px.scatter.assert_called_once_with(
            self.test_data,
            x='x',
            y='y',
            color='category',
            size=None,
            hover_data=['category'],
            title='Test Interactive Plot',
            labels={'x': 'X Axis', 'y': 'Y Axis'}
        )
        
    @patch('backend.Models.visualization.interactive.px')
    def test_line_plot(self, mock_px):
        """测试折线图"""
        mock_fig = MagicMock()
        mock_px.line.return_value = mock_fig
        
        viz = InteractiveVisualization(self.base_params)
        fig = viz.line_plot()
        
        self.assertEqual(fig, mock_fig)
        mock_px.line.assert_called_once_with(
            self.test_data,
            x='x',
            y='y',
            color='category',
            hover_data=['category'],
            title='Test Interactive Plot',
            labels={'x': 'X Axis', 'y': 'Y Axis'}
        )
        
    @patch('backend.Models.visualization.interactive.px')
    def test_bar_plot(self, mock_px):
        """测试条形图"""
        mock_fig = MagicMock()
        mock_px.bar.return_value = mock_fig
        
        viz = InteractiveVisualization(self.base_params)
        fig = viz.bar_plot()
        
        self.assertEqual(fig, mock_fig)
        mock_px.bar.assert_called_once_with(
            self.test_data,
            x='x',
            y='y',
            color='category',
            hover_data=['category'],
            title='Test Interactive Plot',
            labels={'x': 'X Axis', 'y': 'Y Axis'}
        )
        
    @patch('backend.Models.visualization.interactive.px')
    def test_histogram(self, mock_px):
        """测试直方图"""
        mock_fig = MagicMock()
        mock_px.histogram.return_value = mock_fig
        
        viz = InteractiveVisualization(self.base_params)
        fig = viz.histogram()
        
        self.assertEqual(fig, mock_fig)
        mock_px.histogram.assert_called_once_with(
            self.test_data,
            x='x',
            color='category',
            hover_data=['category'],
            title='Test Interactive Plot',
            labels={'x': 'X Axis', 'y': 'Y Axis'}
        )
        
    @patch('backend.Models.visualization.interactive.go.Figure')
    @patch('backend.Models.visualization.interactive.go')
    def test_heatmap(self, mock_go_module, mock_figure):
        """测试热力图"""
        mock_fig = MagicMock()
        mock_figure.return_value = mock_fig
        mock_heatmap = MagicMock()
        mock_go_module.Heatmap.return_value = mock_heatmap
        
        viz = InteractiveVisualization(self.base_params)
        fig = viz.heatmap([[1, 2], [3, 4]])
        
        self.assertEqual(fig, mock_fig)
        mock_go_module.Heatmap.assert_called_once()
        
    @patch('backend.Models.visualization.interactive.px')
    def test_box_plot(self, mock_px):
        """测试箱线图"""
        mock_fig = MagicMock()
        mock_px.box.return_value = mock_fig
        
        viz = InteractiveVisualization(self.base_params)
        fig = viz.box_plot()
        
        self.assertEqual(fig, mock_fig)
        mock_px.box.assert_called_once_with(
            self.test_data,
            x='x',
            y='y',
            color='category',
            hover_data=['category'],
            title='Test Interactive Plot',
            labels={'x': 'X Axis', 'y': 'Y Axis'}
        )
        
    @patch('backend.Models.visualization.interactive.px')
    def test_violin_plot(self, mock_px):
        """测试小提琴图"""
        mock_fig = MagicMock()
        mock_px.violin.return_value = mock_fig
        
        viz = InteractiveVisualization(self.base_params)
        fig = viz.violin_plot()
        
        self.assertEqual(fig, mock_fig)
        mock_px.violin.assert_called_once_with(
            self.test_data,
            x='x',
            y='y',
            color='category',
            hover_data=['category'],
            title='Test Interactive Plot',
            labels={'x': 'X Axis', 'y': 'Y Axis'}
        )
        
    def test_missing_data(self):
        """测试缺少数据的情况"""
        params = self.base_params.copy()
        del params['data']
        
        viz = InteractiveVisualization(params)
        self.assertIsNone(viz.data)


if __name__ == '__main__':
    unittest.main()