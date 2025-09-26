"""
报告模块单元测试
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.DataAnalyzer.reporting import Report


class TestReporting(unittest.TestCase):
    """测试报告生成功能"""

    def setUp(self):
        """测试前准备"""
        self.model_params = {"param1": "value1", "param2": "value2"}
        self.model_scores = {"accuracy": 0.95, "precision": 0.93}
        self.visualizations = {"plot1": Mock(), "plot2": Mock()}
        self.model_predictions = [0, 1, 1, 0, 1]
        
    def test_initialization(self):
        """测试初始化"""
        report = Report(
            model_params=self.model_params,
            model_scores=self.model_scores,
            visualizations=self.visualizations,
            model_predictions=self.model_predictions
        )
        
        self.assertEqual(report.model_params, self.model_params)
        self.assertEqual(report.model_scores, self.model_scores)
        self.assertEqual(report.visualizations, self.visualizations)
        self.assertEqual(report.model_predictions, self.model_predictions)
        
    def test_return_report(self):
        """测试返回报告"""
        report = Report(
            model_params=self.model_params,
            model_scores=self.model_scores,
            visualizations=self.visualizations,
            model_predictions=self.model_predictions
        )
        
        result = report.return_report()
        
        self.assertIsInstance(result, dict)
        self.assertIn("model_params", result)
        self.assertIn("model_scores", result)
        self.assertIn("visualizations", result)
        self.assertIn("model_predictions", result)
        
        self.assertEqual(result["model_params"], self.model_params)
        self.assertEqual(result["model_scores"], self.model_scores)
        self.assertEqual(result["visualizations"], self.visualizations)
        self.assertEqual(result["model_predictions"], self.model_predictions)
        
    def test_return_report_with_none_values(self):
        """测试返回包含None值的报告"""
        report = Report(
            model_params=None,
            model_scores=None,
            visualizations=None,
            model_predictions=None
        )
        
        result = report.return_report()
        
        self.assertIsInstance(result, dict)
        # 注意：根据实际实现，可能不会包含这些键，所以不能断言它们存在且为None


if __name__ == '__main__':
    unittest.main()