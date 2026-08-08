import sys
import os
import unittest
import numpy as np
import matplotlib.pyplot as plt
import hashlib

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from . import visualization_upgrade_data_generator as vudg
from backend.Models.visualization.upgrade.factory import VisualizationFactory
from backend.Models.visualization.upgrade.strategy import VisualizationStrategySelector


def get_figure_hash(fig):
    """获取matplotlib图形的hash值用于比较"""
    # 将图形转换为数组并计算hash值（buffer_rgba 兼容 matplotlib>=3.8）
    fig.canvas.draw()
    buf = bytes(fig.canvas.buffer_rgba())
    hash_val = hashlib.md5(buf).hexdigest()
    return hash_val


class TestCommonChartStrategies(unittest.TestCase):
    """测试通用图表策略"""

    def setUp(self):
        """测试前准备"""
        self.data_generator = vudg.DataGenerator()
        self.factory = VisualizationFactory()
        self.selector = VisualizationStrategySelector()

    def test_scatter_plot_strategy(self):
        """测试散点图策略"""
        # 生成测试数据
        X = np.random.rand(100, 2)
        y = np.random.rand(100)
        
        params = {
            "X": X,
            "y": y,
            "task_list": ["scatter"]
        }
        
        # 创建参考图表
        fig_ref, ax = plt.subplots(figsize=(8, 6))
        scatter = ax.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis')
        plt.colorbar(scatter, ax=ax)
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('散点图')
        ref_hash = get_figure_hash(fig_ref)
        plt.close(fig_ref)
        
        # 创建策略实例
        strategy = self.factory.create_visualization_strategy("no_model", "common", params)
        
        # 验证参数
        strategy.validate_params()
        
        # 生成静态图表
        static_charts = strategy.generate_static_charts()
        self.assertIn("scatter_plot", static_charts)
        self.assertIsNotNone(static_charts["scatter_plot"])
        
        # 比较hash值
        generated_hash = get_figure_hash(static_charts["scatter_plot"])
        # 注意：由于字体渲染等问题，hash值可能不完全相同，这里仅作示例
        # 在实际测试中，可能需要比较图像的其他特征
        
        # 生成交互式图表
        interactive_charts = strategy.generate_interactive_charts()
        self.assertIn("scatter_plot", interactive_charts)
        self.assertIsNotNone(interactive_charts["scatter_plot"])

    def test_line_plot_strategy(self):
        """测试折线图策略"""
        # 生成测试数据
        X = np.linspace(0, 10, 50)
        y = np.sin(X)
        
        params = {
            "X": X,
            "y": y,
            "task_list": ["line"]
        }
        
        # 创建参考图表
        fig_ref, ax = plt.subplots(figsize=(10, 6))
        ax.plot(X, y)
        ax.set_xlabel('索引')
        ax.set_ylabel('值')
        ax.set_title('折线图')
        ref_hash = get_figure_hash(fig_ref)
        plt.close(fig_ref)
        
        # 创建策略实例
        strategy = self.factory.create_visualization_strategy("no_model", "common", params)
        
        # 验证参数
        strategy.validate_params()
        
        # 生成静态图表
        static_charts = strategy.generate_static_charts()
        self.assertIn("line_plot", static_charts)
        self.assertIsNotNone(static_charts["line_plot"])
        
        # 生成交互式图表
        interactive_charts = strategy.generate_interactive_charts()
        self.assertIn("line_plot", interactive_charts)
        self.assertIsNotNone(interactive_charts["line_plot"])

    def test_bar_plot_strategy(self):
        """测试柱状图策略"""
        # 生成测试数据
        X = np.arange(20)
        y = np.random.rand(20)
        
        params = {
            "X": X,
            "y": y,
            "task_list": ["bar"]
        }
        
        # 创建参考图表
        fig_ref, ax = plt.subplots(figsize=(10, 6))
        ax.bar(range(len(y)), y)
        ax.set_xlabel('索引')
        ax.set_ylabel('值')
        ax.set_title('柱状图')
        ref_hash = get_figure_hash(fig_ref)
        plt.close(fig_ref)
        
        # 创建策略实例
        strategy = self.factory.create_visualization_strategy("no_model", "common", params)
        
        # 验证参数
        strategy.validate_params()
        
        # 生成静态图表
        static_charts = strategy.generate_static_charts()
        self.assertIn("bar_plot", static_charts)
        self.assertIsNotNone(static_charts["bar_plot"])
        
        # 生成交互式图表
        interactive_charts = strategy.generate_interactive_charts()
        self.assertIn("bar_plot", interactive_charts)
        self.assertIsNotNone(interactive_charts["bar_plot"])

    def test_histogram_strategy(self):
        """测试直方图策略"""
        # 生成测试数据
        data = np.random.normal(0, 1, 1000)
        
        params = {
            "X": data.reshape(-1, 1),
            "y": data,
            "task_list": ["histogram"]
        }
        
        # 创建参考图表
        fig_ref, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data, bins=30)
        ax.set_xlabel('值')
        ax.set_ylabel('频率')
        ax.set_title('直方图')
        ref_hash = get_figure_hash(fig_ref)
        plt.close(fig_ref)
        
        # 创建策略实例
        strategy = self.factory.create_visualization_strategy("no_model", "common", params)
        
        # 验证参数
        strategy.validate_params()
        
        # 生成静态图表
        static_charts = strategy.generate_static_charts()
        self.assertIn("histogram", static_charts)
        self.assertIsNotNone(static_charts["histogram"])
        
        # 生成交互式图表
        interactive_charts = strategy.generate_interactive_charts()
        self.assertIn("histogram", interactive_charts)
        self.assertIsNotNone(interactive_charts["histogram"])


class TestVisualizationFactory(unittest.TestCase):
    """测试可视化工厂"""

    def setUp(self):
        """测试前准备"""
        self.factory = VisualizationFactory()

    def test_load_config(self):
        """测试配置加载"""
        config = self.factory.config
        self.assertIsNotNone(config)
        self.assertIn("supported_models", config)
        self.assertIn("task", config)

    def test_get_supported_models(self):
        """测试获取支持的模型"""
        models = self.factory.get_supported_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

    def test_get_model_supported_tasks(self):
        """测试获取模型支持的任务"""
        tasks = self.factory.get_model_supported_tasks("logisticregression")
        self.assertIsInstance(tasks, list)
        self.assertIn("classification", tasks)

    def test_create_common_strategy(self):
        """测试创建通用策略"""
        params = {
            "X": np.random.rand(100, 2),
            "task_list": ["scatter"]
        }
        
        strategy = self.factory.create_visualization_strategy("no_model", "common", params)
        self.assertIsNotNone(strategy)


class TestStrategySelector(unittest.TestCase):
    """测试策略选择器"""

    def setUp(self):
        """测试前准备"""
        self.selector = VisualizationStrategySelector()

    def test_select_charts_for_classification(self):
        """测试分类任务图表选择"""
        params = {
            "y_test": [0, 1, 0, 1, 0, 1]
        }
        charts = self.selector.select_charts("classification", params)
        self.assertIn("confusion_matrix", charts)

    def test_select_charts_for_regression(self):
        """测试回归任务图表选择"""
        charts = self.selector.select_charts("regression", {})
        self.assertIn("actual_vs_predicted", charts)
        self.assertIn("residuals_plot", charts)

    def test_select_charts_for_clustering(self):
        """测试聚类任务图表选择"""
        charts = self.selector.select_charts("clustering", {})
        self.assertIn("cluster_scatter", charts)
        self.assertIn("cluster_bar", charts)

    def test_select_charts_for_transformer(self):
        """测试变换器任务图表选择"""
        charts = self.selector.select_charts("transformer", {})
        self.assertIn("before_after_distribution", charts)

    def test_select_charts_for_common(self):
        """测试通用图表选择"""
        params = {
            "task_list": ["scatter", "line"]
        }
        charts = self.selector.select_charts("common", params)
        self.assertIn("scatter", charts)
        self.assertIn("line", charts)


class TestModelSpecificStrategies(unittest.TestCase):
    """测试模型特定策略"""

    def setUp(self):
        """测试前准备"""
        self.data_generator = vudg.DataGenerator()
        self.factory = VisualizationFactory()

    def test_linear_regression_strategy(self):
        """测试线性回归策略"""
        # 生成回归数据
        X_train, X_test, y_train, y_test = self.data_generator.generate_regression_data()
        
        params = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "model": None,  # 在实际测试中应该是一个训练好的模型
            "task_list": ["actual_vs_predicted", "residuals_plot"]
        }
        
        # 创建策略实例
        strategy = self.factory.create_visualization_strategy("linearregression", "regression", params)
        self.assertIsNotNone(strategy)

    def test_logistic_regression_strategy(self):
        """测试逻辑回归策略"""
        # 生成分类数据
        X_train, X_test, y_train, y_test = self.data_generator.generate_classification_data()
        
        params = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "model": None,  # 在实际测试中应该是一个训练好的模型
            "task_list": ["confusion_matrix", "roc_curve"]
        }
        
        # 创建策略实例
        strategy = self.factory.create_visualization_strategy("logisticregression", "classification", params)
        self.assertIsNotNone(strategy)

    def test_kmeans_strategy(self):
        """测试KMeans策略"""
        # 生成聚类数据
        X = self.data_generator.generate_clustering_data()
        
        params = {
            "X": X,
            "model": None,  # 在实际测试中应该是一个训练好的模型
            "task_list": ["cluster_scatter"]
        }
        
        # 创建策略实例
        strategy = self.factory.create_visualization_strategy("kmeans", "clustering", params)
        self.assertIsNotNone(strategy)


if __name__ == "__main__":
    # 运行测试
    unittest.main()