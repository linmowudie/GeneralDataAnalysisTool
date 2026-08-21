"""
DataVisualisationUpgrade模块的完整测试套件
"""

import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入测试模块
from tests.unit.visualization_upgrade_tester import (
    TestCommonChartStrategies,
    TestVisualizationFactory,
    TestStrategySelector,
    TestModelSpecificStrategies
)


def create_test_suite():
    """创建测试套件"""
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTest(unittest.makeSuite(TestCommonChartStrategies))
    suite.addTest(unittest.makeSuite(TestVisualizationFactory))
    suite.addTest(unittest.makeSuite(TestStrategySelector))
    suite.addTest(unittest.makeSuite(TestModelSpecificStrategies))
    
    return suite


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = create_test_suite()
    
    # 创建测试运行器
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 运行测试
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    # 运行测试
    test_result = run_tests()
    
    # 输出测试结果摘要
    print("\n" + "="*50)
    print("测试结果摘要:")
    print(f"运行测试数: {test_result.testsRun}")
    print(f"失败数: {len(test_result.failures)}")
    print(f"错误数: {len(test_result.errors)}")
    print(f"成功率: {((test_result.testsRun - len(test_result.failures) - len(test_result.errors)) / test_result.testsRun * 100):.2f}%" if test_result.testsRun > 0 else "0%")
    print("="*50)
