"""
可视化工厂模块单元测试
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestVisualizationFactory(unittest.TestCase):
    """测试VisualizationFactory类"""

    def setUp(self):
        """测试前准备"""
        pass
        
    def tearDown(self):
        """测试后清理"""
        pass

    @patch('backend.Models.visualization.upgrade.factory.os.path.dirname')
    def test_factory_initialization(self, mock_dirname):
        """测试工厂初始化"""
        try:
            from backend.Models.visualization.upgrade.factory import VisualizationFactory
            
            # 模拟路径
            mock_dirname.return_value = PROJECT_ROOT
            
            # 创建工厂实例
            factory = VisualizationFactory()
            self.assertIsNotNone(factory)
            self.assertIsNotNone(factory.config)
        except Exception as e:
            self.fail(f"工厂初始化失败: {e}")

    def test_get_model_supported_tasks(self):
        """测试获取模型支持的任务类型"""
        try:
            from backend.Models.visualization.upgrade.factory import VisualizationFactory
            
            factory = VisualizationFactory()
            
            # 测试逻辑回归模型支持的任务类型
            supported_tasks = factory.get_model_supported_tasks("logisticregression")
            self.assertIn("classification", supported_tasks)
            
            # 测试KMeans模型支持的任务类型
            supported_tasks = factory.get_model_supported_tasks("kmeans")
            self.assertIn("clustering", supported_tasks)
            
            # 测试PCA模型支持的任务类型
            supported_tasks = factory.get_model_supported_tasks("pca")
            self.assertIn("transformer", supported_tasks)
        except Exception as e:
            self.fail(f"获取模型支持任务类型失败: {e}")

    def test_get_supported_models(self):
        """测试获取支持的模型列表"""
        try:
            from backend.Models.visualization.upgrade.factory import VisualizationFactory
            
            factory = VisualizationFactory()
            supported_models = factory.get_supported_models()
            
            # 检查一些已知的模型是否在支持列表中
            self.assertIn("logisticregression", supported_models)
            self.assertIn("kmeans", supported_models)
            self.assertIn("pca", supported_models)
        except Exception as e:
            self.fail(f"获取支持模型列表失败: {e}")

    def test_is_common_chart(self):
        """测试判断是否为通用图表"""
        try:
            from backend.Models.visualization.upgrade.factory import VisualizationFactory
            
            factory = VisualizationFactory()
            
            # 测试通用图表
            self.assertTrue(factory.is_common_chart("scatter"))
            self.assertTrue(factory.is_common_chart("line"))
            self.assertTrue(factory.is_common_chart("bar"))
            
            # 测试非通用图表
            self.assertFalse(factory.is_common_chart("confusion_matrix"))
        except Exception as e:
            self.fail(f"判断通用图表失败: {e}")

    @patch('backend.Models.visualization.upgrade.factory.VisualizationFactory._create_common_strategy')
    def test_create_common_strategy(self, mock_create_common):
        """测试创建通用图表策略"""
        try:
            from backend.Models.visualization.upgrade.factory import VisualizationFactory
            
            factory = VisualizationFactory()
            
            # 创建模拟策略
            mock_strategy = Mock()
            mock_create_common.return_value = mock_strategy
            
            # 测试创建散点图策略
            params = {"task_list": ["scatter"]}
            strategy = factory.create_visualization_strategy("no_model", "common", params)
            
            # 验证调用了创建通用策略的方法
            mock_create_common.assert_called()
        except Exception as e:
            self.fail(f"创建通用图表策略失败: {e}")

    def test_select_charts(self):
        """测试选择图表类型"""
        try:
            from backend.Models.visualization.upgrade.factory import VisualizationFactory
            
            factory = VisualizationFactory()
            
            # 测试分类任务图表选择
            params = {"y_test": [0, 1, 0, 1]}
            charts = factory.select_charts("logisticregression", "classification", params)
            self.assertIsNotNone(charts)
            
            # 测试回归任务图表选择
            charts = factory.select_charts("linearregression", "regression", params)
            self.assertIsNotNone(charts)
            
            # 测试聚类任务图表选择
            charts = factory.select_charts("kmeans", "clustering", params)
            self.assertIsNotNone(charts)
        except Exception as e:
            self.fail(f"选择图表类型失败: {e}")


if __name__ == '__main__':
    unittest.main()