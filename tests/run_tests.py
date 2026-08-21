"""
运行所有单元测试
"""

import unittest
import sys
import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_all_tests():
    """运行所有单元测试"""
    # 发现并运行测试（同时收录 test_*.py 与遗留的 *_test.py 命名文件）
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for pattern in ('test_*.py', '*_test.py'):
        suite.addTests(loader.discover('tests/unit', pattern=pattern))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)