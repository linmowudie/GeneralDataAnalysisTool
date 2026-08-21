"""
测试common模块中的可视化功能（策略体系）

原测试基于已删除的升级版 DataVisualization 接口；现改为直接测试
backend.Models.visualization.upgrade.common 下的各图表策略。
"""

import unittest
import numpy as np
import sys
import os

# 添加项目根目录到路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.Models.visualization.upgrade.common.scatter import ScatterPlotStrategy
from backend.Models.visualization.upgrade.common.line import LinePlotStrategy
from backend.Models.visualization.upgrade.common.bar import BarPlotStrategy
from backend.Models.visualization.upgrade.common.histogram import HistogramStrategy
from backend.Models.visualization.upgrade.common.heatmap import HeatmapStrategy
from backend.Models.visualization.upgrade.common.box import BoxPlotStrategy
from backend.Models.visualization.upgrade.common.violin_plot import ViolinPlotStrategy
from backend.Models.visualization.upgrade.common.area_plot import AreaPlotStrategy
from backend.Models.visualization.upgrade.common.step_plot import StepPlotStrategy
from backend.Models.visualization.upgrade.common.pair_plot import PairPlotStrategy
from backend.Models.visualization.upgrade.common.bubble_plot import BubblePlotStrategy
from backend.Models.visualization.upgrade.common.density_contour_plot import DensityContourPlotStrategy


class TestCommonVisualization(unittest.TestCase):
    """测试common模块中的各种图表类型"""

    def setUp(self):
        """测试前的准备工作"""
        np.random.seed(42)
        self.X = np.random.randn(100, 5)
        self.params = {"X": self.X}

    def _run_strategy(self, strategy, expected_key):
        """执行策略并验证静态/交互式图表输出"""
        strategy.validate_params()

        static_charts = strategy.generate_static_charts()
        self.assertIsInstance(static_charts, dict)
        self.assertIn(expected_key, static_charts)

        interactive_charts = strategy.generate_interactive_charts()
        self.assertIsInstance(interactive_charts, dict)
        self.assertGreater(len(interactive_charts), 0)

    def test_scatter_plot(self):
        """测试散点图"""
        self._run_strategy(ScatterPlotStrategy(self.params), "scatter_plot")

    def test_line_plot(self):
        """测试折线图"""
        self._run_strategy(LinePlotStrategy(self.params), "line_plot")

    def test_bar_plot(self):
        """测试柱状图"""
        self._run_strategy(BarPlotStrategy(self.params), "bar_plot")

    def test_histogram(self):
        """测试直方图"""
        self._run_strategy(HistogramStrategy(self.params), "histogram")

    def test_heatmap(self):
        """测试热力图"""
        params = {"X": np.random.rand(5, 5)}
        self._run_strategy(HeatmapStrategy(params), "heatmap")

    def test_box_plot(self):
        """测试箱线图"""
        self._run_strategy(BoxPlotStrategy(self.params), "box_plot")

    def test_violin_plot(self):
        """测试小提琴图"""
        self._run_strategy(ViolinPlotStrategy(self.params), "violin_plot")

    def test_area_plot(self):
        """测试面积图"""
        self._run_strategy(AreaPlotStrategy(self.params), "area_plot")

    def test_step_plot(self):
        """测试阶梯图"""
        self._run_strategy(StepPlotStrategy(self.params), "step_plot")

    def test_pair_plot(self):
        """测试成对图"""
        self._run_strategy(PairPlotStrategy(self.params), "pair_plot")

    def test_bubble_plot(self):
        """测试气泡图"""
        self._run_strategy(BubblePlotStrategy(self.params), "bubble_plot")

    def test_density_contour_plot(self):
        """测试密度等高线图"""
        self._run_strategy(DensityContourPlotStrategy(self.params), "density_contour_plot")


if __name__ == '__main__':
    unittest.main()
