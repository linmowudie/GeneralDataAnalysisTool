"""
可视化策略模块单元测试
"""

import unittest
import sys
import os
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestVisualizationStrategies(unittest.TestCase):
    """测试可视化策略类"""

    def setUp(self):
        """测试前准备"""
        pass
        
    def tearDown(self):
        """测试后清理"""
        pass

    def test_strategy_selector(self):
        """测试策略选择器"""
        try:
            from backend.Models.visualization.upgrade.strategy import VisualizationStrategySelector
            
            selector = VisualizationStrategySelector()
            self.assertIsNotNone(selector)
        except Exception as e:
            self.fail(f"策略选择器测试失败: {e}")

    def test_classification_strategy_selection(self):
        """测试分类策略选择"""
        try:
            from backend.Models.visualization.upgrade.strategy import VisualizationStrategySelector
            
            selector = VisualizationStrategySelector()
            
            # 测试二分类情况
            binary_params = {"y_test": [0, 1, 0, 1]}
            charts = selector.select_charts_for_classification(binary_params)
            self.assertIn("confusion_matrix", charts)
            self.assertIn("roc_curve", charts)
            
            # 测试多分类情况
            multi_params = {"y_test": [0, 1, 2, 0, 1, 2]}
            charts = selector.select_charts_for_classification(multi_params)
            self.assertIn("confusion_matrix", charts)
            self.assertIn("roc_curve", charts)
        except Exception as e:
            self.fail(f"分类策略选择测试失败: {e}")

    def test_regression_strategy_selection(self):
        """测试回归策略选择"""
        try:
            from backend.Models.visualization.upgrade.strategy import VisualizationStrategySelector
            
            selector = VisualizationStrategySelector()
            
            # 测试回归任务图表选择
            params = {}
            charts = selector.select_charts_for_regression(params)
            self.assertIn("actual_vs_predicted", charts)
            self.assertIn("residuals_plot", charts)
        except Exception as e:
            self.fail(f"回归策略选择测试失败: {e}")

    def test_clustering_strategy_selection(self):
        """测试聚类策略选择"""
        try:
            from backend.Models.visualization.upgrade.strategy import VisualizationStrategySelector
            
            selector = VisualizationStrategySelector()
            
            # 测试聚类任务图表选择
            params = {}
            charts = selector.select_charts_for_clustering(params)
            self.assertIn("cluster_scatter", charts)
            self.assertIn("cluster_bar", charts)
        except Exception as e:
            self.fail(f"聚类策略选择测试失败: {e}")

    def test_transformer_strategy_selection(self):
        """测试变换器策略选择"""
        try:
            from backend.Models.visualization.upgrade.strategy import VisualizationStrategySelector
            
            selector = VisualizationStrategySelector()
            
            # 测试变换器任务图表选择
            params = {}
            charts = selector.select_charts_for_transformer(params)
            self.assertIn("before_after_distribution", charts)
        except Exception as e:
            self.fail(f"变换器策略选择测试失败: {e}")

    def test_common_strategy_selection(self):
        """测试通用策略选择"""
        try:
            from backend.Models.visualization.upgrade.strategy import VisualizationStrategySelector
            
            selector = VisualizationStrategySelector()
            
            # 测试通用图表选择
            params = {"task_list": ["scatter", "line"]}
            charts = selector.select_charts_for_common(params)
            self.assertIn("scatter", charts)
            self.assertIn("line", charts)
        except Exception as e:
            self.fail(f"通用策略选择测试失败: {e}")

    def test_base_strategy_abstract_methods(self):
        """测试基础策略抽象方法"""
        try:
            from backend.Models.visualization.upgrade.base_visualization import VisualizationStrategy
            
            # 测试抽象类存在所需的方法
            self.assertTrue(hasattr(VisualizationStrategy, 'validate_params'))
            self.assertTrue(hasattr(VisualizationStrategy, 'generate_static_charts'))
            self.assertTrue(hasattr(VisualizationStrategy, 'generate_interactive_charts'))
                
        except Exception as e:
            self.fail(f"基础策略抽象方法测试失败: {e}")

    def test_basic_visualization_strategy(self):
        """测试基础可视化策略实现"""
        try:
            from backend.Models.visualization.upgrade.factory import BasicVisualizationStrategy
            
            params = {}
            strategy = BasicVisualizationStrategy(params)
            
            # 测试验证参数方法
            strategy.validate_params()  # 应该不抛出异常
            
            # 测试生成静态图表方法
            static_charts = strategy.generate_static_charts()
            self.assertIsInstance(static_charts, dict)
            
            # 测试生成交互式图表方法
            interactive_charts = strategy.generate_interactive_charts()
            self.assertIsInstance(interactive_charts, dict)
            
        except Exception as e:
            self.fail(f"基础可视化策略测试失败: {e}")


if __name__ == '__main__':
    unittest.main()