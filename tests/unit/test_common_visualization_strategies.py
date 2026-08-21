"""
通用可视化策略模块单元测试
"""

import unittest
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import Mock, patch, MagicMock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestCommonVisualizationStrategies(unittest.TestCase):
    """测试通用可视化策略类"""

    def setUp(self):
        """测试前准备"""
        pass
        
    def tearDown(self):
        """测试后清理"""
        plt.close('all')

    def test_scatter_plot_strategy(self):
        """测试散点图策略"""
        try:
            from backend.Models.visualization.upgrade.common.scatter import ScatterPlotStrategy
            
            # 创建测试数据
            params = {
                "X": np.random.rand(20, 2),
                "y": np.random.rand(20)
            }
            
            strategy = ScatterPlotStrategy(params)
            
            # 测试参数验证
            strategy.validate_params()
            
            # 测试生成静态图表
            static_charts = strategy.generate_static_charts()
            self.assertIsInstance(static_charts, dict)
            
            # 测试生成交互式图表
            interactive_charts = strategy.generate_interactive_charts()
            self.assertIsInstance(interactive_charts, dict)
            
        except Exception as e:
            self.fail(f"散点图策略测试失败: {e}")

    def test_line_plot_strategy(self):
        """测试折线图策略"""
        try:
            from backend.Models.visualization.upgrade.common.line import LinePlotStrategy
            
            # 创建测试数据
            params = {
                "X": np.random.rand(20, 2),
                "y": np.random.rand(20)
            }
            
            strategy = LinePlotStrategy(params)
            
            # 测试参数验证
            strategy.validate_params()
            
            # 测试生成静态图表
            static_charts = strategy.generate_static_charts()
            self.assertIsInstance(static_charts, dict)
            
            # 测试生成交互式图表
            interactive_charts = strategy.generate_interactive_charts()
            self.assertIsInstance(interactive_charts, dict)
            
        except Exception as e:
            self.fail(f"折线图策略测试失败: {e}")

    def test_bar_plot_strategy(self):
        """测试柱状图策略"""
        try:
            from backend.Models.visualization.upgrade.common.bar import BarPlotStrategy
            
            # 创建测试数据
            params = {
                "X": np.random.rand(10, 2)
            }
            
            strategy = BarPlotStrategy(params)
            
            # 测试参数验证
            strategy.validate_params()
            
            # 测试生成静态图表
            static_charts = strategy.generate_static_charts()
            self.assertIsInstance(static_charts, dict)
            
            # 测试生成交互式图表
            interactive_charts = strategy.generate_interactive_charts()
            self.assertIsInstance(interactive_charts, dict)
            
        except Exception as e:
            self.fail(f"柱状图策略测试失败: {e}")

    def test_histogram_strategy(self):
        """测试直方图策略"""
        try:
            from backend.Models.visualization.upgrade.common.histogram import HistogramStrategy
            
            # 创建测试数据
            params = {
                "X": np.random.rand(100)
            }
            
            strategy = HistogramStrategy(params)
            
            # 测试参数验证
            strategy.validate_params()
            
            # 测试生成静态图表
            static_charts = strategy.generate_static_charts()
            self.assertIsInstance(static_charts, dict)
            
            # 测试生成交互式图表
            interactive_charts = strategy.generate_interactive_charts()
            self.assertIsInstance(interactive_charts, dict)
            
        except Exception as e:
            self.fail(f"直方图策略测试失败: {e}")

    def test_box_plot_strategy(self):
        """测试箱线图策略"""
        try:
            from backend.Models.visualization.upgrade.common.box import BoxPlotStrategy
            
            # 创建测试数据
            params = {
                "X": np.random.rand(50, 3)
            }
            
            strategy = BoxPlotStrategy(params)
            
            # 测试参数验证
            strategy.validate_params()
            
            # 测试生成静态图表
            static_charts = strategy.generate_static_charts()
            self.assertIsInstance(static_charts, dict)
            
            # 测试生成交互式图表
            interactive_charts = strategy.generate_interactive_charts()
            self.assertIsInstance(interactive_charts, dict)
            
        except Exception as e:
            self.fail(f"箱线图策略测试失败: {e}")

    def test_heatmap_strategy(self):
        """测试热力图策略"""
        try:
            from backend.Models.visualization.upgrade.common.heatmap import HeatmapStrategy
            
            # 创建测试数据（HeatmapStrategy 需要 X 参数）
            data = np.random.rand(5, 5)
            params = {
                "X": data
            }
            
            strategy = HeatmapStrategy(params)
            
            # 测试参数验证
            strategy.validate_params()
            
            # 测试生成静态图表
            static_charts = strategy.generate_static_charts()
            self.assertIsInstance(static_charts, dict)
            
            # 测试生成交互式图表
            interactive_charts = strategy.generate_interactive_charts()
            self.assertIsInstance(interactive_charts, dict)
            
        except Exception as e:
            self.fail(f"热力图策略测试失败: {e}")


if __name__ == '__main__':
    unittest.main()