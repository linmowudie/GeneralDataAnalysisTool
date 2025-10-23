"""
DataVisualisationUpgrade模块单元测试
"""

import unittest
import sys
import os
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestDataVisualizationUpgrade(unittest.TestCase):
    """测试DataVisualisationUpgrade模块"""

    def setUp(self):
        """测试前准备"""
        pass
        
    def tearDown(self):
        """测试后清理"""
        pass

    def test_factory_creation(self):
        """测试工厂类创建"""
        try:
            from Src.DataAnalyzer.DataVisualisationUpgrade.factory import VisualizationFactory
            factory = VisualizationFactory()
            self.assertIsNotNone(factory)
        except Exception as e:
            self.fail(f"工厂类创建失败: {e}")

    def test_base_visualization_strategy(self):
        """测试基础可视化策略类"""
        try:
            from Src.DataAnalyzer.DataVisualisationUpgrade.base_visualization import VisualizationStrategy
            # 这是一个抽象类，不能直接实例化
            self.assertTrue(hasattr(VisualizationStrategy, 'validate_params'))
            self.assertTrue(hasattr(VisualizationStrategy, 'generate_static_charts'))
            self.assertTrue(hasattr(VisualizationStrategy, 'generate_interactive_charts'))
        except Exception as e:
            self.fail(f"基础可视化策略类测试失败: {e}")

    def test_common_chart_strategies(self):
        """测试通用图表策略"""
        try:
            from Src.DataAnalyzer.DataVisualisationUpgrade.common.scatter import ScatterPlotStrategy
            from Src.DataAnalyzer.DataVisualisationUpgrade.common.line import LinePlotStrategy
            from Src.DataAnalyzer.DataVisualisationUpgrade.common.bar import BarPlotStrategy
            
            # 创建测试数据
            test_params = {
                "X": np.random.rand(10, 2),
                "y": np.random.rand(10)
            }
            
            # 测试散点图策略
            scatter_strategy = ScatterPlotStrategy(test_params)
            self.assertIsNotNone(scatter_strategy)
            
            # 测试折线图策略
            line_strategy = LinePlotStrategy(test_params)
            self.assertIsNotNone(line_strategy)
            
            # 测试柱状图策略
            bar_strategy = BarPlotStrategy(test_params)
            self.assertIsNotNone(bar_strategy)
        except Exception as e:
            self.fail(f"通用图表策略测试失败: {e}")

    def test_classification_strategies(self):
        """测试分类任务策略"""
        try:
            from Src.DataAnalyzer.DataVisualisationUpgrade.classification.logisticregression import LogisticRegressionStrategy
            from Src.DataAnalyzer.DataVisualisationUpgrade.classification.decisiontreeclassifier import DecisionTreeClassifierStrategy
            
            # 创建测试数据
            test_params = {
                "model": Mock(),
                "X_test": np.random.rand(10, 2),
                "y_test": np.random.randint(0, 2, 10)
            }
            
            # 测试逻辑回归策略
            lr_strategy = LogisticRegressionStrategy(test_params)
            self.assertIsNotNone(lr_strategy)
            
            # 测试决策树策略
            dt_strategy = DecisionTreeClassifierStrategy(test_params)
            self.assertIsNotNone(dt_strategy)
        except Exception as e:
            self.fail(f"分类任务策略测试失败: {e}")

    def test_clustering_strategies(self):
        """测试聚类任务策略"""
        try:
            from Src.DataAnalyzer.DataVisualisationUpgrade.clustering.kmeans import KMeansStrategy
            
            # 创建测试数据
            test_params = {
                "X": np.random.rand(20, 2),
                "model": Mock()
            }
            
            # 测试KMeans策略
            kmeans_strategy = KMeansStrategy(test_params)
            self.assertIsNotNone(kmeans_strategy)
        except Exception as e:
            self.fail(f"聚类任务策略测试失败: {e}")

    def test_regression_strategies(self):
        """测试回归任务策略"""
        try:
            from Src.DataAnalyzer.DataVisualisationUpgrade.regression.linearregression import LinearRegressionStrategy
            
            # 创建测试数据
            test_params = {
                "model": Mock(),
                "X_test": np.random.rand(10, 2),
                "y_test": np.random.rand(10)
            }
            
            # 测试线性回归策略
            lr_strategy = LinearRegressionStrategy(test_params)
            self.assertIsNotNone(lr_strategy)
        except Exception as e:
            self.fail(f"回归任务策略测试失败: {e}")

    def test_transformer_strategies(self):
        """测试变换器任务策略"""
        try:
            from Src.DataAnalyzer.DataVisualisationUpgrade.transformer.pca import PCAStrategy
            
            # 创建测试数据
            test_params = {
                "model": Mock(),
                "X_train": np.random.rand(20, 5)
            }
            
            # 测试PCA策略
            pca_strategy = PCAStrategy(test_params)
            self.assertIsNotNone(pca_strategy)
        except Exception as e:
            self.fail(f"变换器任务策略测试失败: {e}")

    def test_utils_functions(self):
        """测试工具函数"""
        try:
            from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_confusion_matrix import plot_confusion_matrix
            from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_roc_curve import plot_roc_curve
            
            # 测试混淆矩阵工具函数
            y_true = [0, 1, 0, 1]
            y_pred = [0, 1, 1, 1]
            fig, ax = plot_confusion_matrix(y_true, y_pred)
            self.assertIsNotNone(fig)
            self.assertIsNotNone(ax)
            
            # 测试ROC曲线工具函数
            y_true = [0, 1, 0, 1]
            y_pred_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.8, 0.2], [0.3, 0.7]])
            fig, ax = plot_roc_curve(y_true, y_pred_proba)
            self.assertIsNotNone(fig)
            self.assertIsNotNone(ax)
        except Exception as e:
            self.fail(f"工具函数测试失败: {e}")


if __name__ == '__main__':
    unittest.main()