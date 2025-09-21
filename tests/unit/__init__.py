"""
单元测试包初始化文件
"""

import unittest


def create_test_suite():
    """创建测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试用例
    suite.addTests(loader.discover('tests/unit', pattern='test_*.py'))
    
    return suite


if __name__ == '__main__':
    # 运行所有测试
    runner = unittest.TextTestRunner(verbosity=2)
    suite = create_test_suite()
    runner.run(suite)