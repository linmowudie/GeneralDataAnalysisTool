"""
测试common模块中的可视化功能
"""

import unittest
import numpy as np
import sys
import os

# 添加项目根目录到路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from Src.DataAnalyzer.ModuleInterfaces.data_visualization_upgrade_interfaces import DataVisualization


class TestCommonVisualization(unittest.TestCase):
    """测试common模块中的各种图表类型"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试数据
        np.random.seed(42)
        self.X = np.random.randn(100, 5)
        self.y = np.random.randint(0, 3, 100)
        self.sizes = np.random.randint(20, 100, 100)
        
        # 数据字典
        self.data_dict = {
            "X": self.X,
            "y": self.y,
            "sizes": self.sizes
        }
        
        # 样式参数
        self.label_style = "测试图表"
        self.plot_style = "default"
        self.font_style = "sans-serif"

    def test_scatter_plot(self):
        """测试散点图"""
        # 创建散点图可视化对象
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["scatter"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        # 生成图表
        charts = viz.generate_plot()
        
        # 验证结果
        self.assertIsInstance(charts, dict)
        self.assertIn("scatter_plot", charts)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["scatter"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)
        self.assertIn("scatter_plot", charts_interactive)

    def test_line_plot(self):
        """测试折线图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["line"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["line"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_bar_plot(self):
        """测试柱状图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["bar"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["bar"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_histogram(self):
        """测试直方图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["histogram"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["histogram"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_box_plot(self):
        """测试箱线图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["box"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["box"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_heatmap(self):
        """测试热力图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["heatmap"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["heatmap"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_violin_plot(self):
        """测试小提琴图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["violin_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["violin_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_pair_plot(self):
        """测试成对图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["pair_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["pair_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_density_contour_plot(self):
        """测试密度等高线图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["density_contour_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["density_contour_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_bubble_plot(self):
        """测试气泡图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["bubble_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["bubble_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_area_plot(self):
        """测试面积图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["area_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["area_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)

    def test_step_plot(self):
        """测试阶梯图"""
        viz = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["step_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=False
        )
        
        charts = viz.generate_plot()
        self.assertIsInstance(charts, dict)
        
        # 测试交互式图表
        viz_interactive = DataVisualization(
            model_name="no_model",
            model=None,
            task_list=["step_plot"],
            data_dict=self.data_dict,
            label_style=self.label_style,
            plot_style=self.plot_style,
            font_style=self.font_style,
            interactive=True
        )
        
        charts_interactive = viz_interactive.generate_plot()
        self.assertIsInstance(charts_interactive, dict)


if __name__ == "__main__":
    unittest.main()