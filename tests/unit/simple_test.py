"""
简化版测试文件，用于测试DataVisualisationUpgrade模块
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_imports():
    """测试导入是否正常"""
    try:
        from Src.DataAnalyzer.DataVisualisationUpgrade.factory import VisualizationFactory
        from Src.DataAnalyzer.DataVisualisationUpgrade.strategy import VisualizationStrategySelector
        print("✓ 成功导入所有模块")
        return True
    except Exception as e:
        print(f"✗ 导入模块时出错: {e}")
        return False

def test_factory_creation():
    """测试工厂创建"""
    try:
        from Src.DataAnalyzer.DataVisualisationUpgrade.factory import VisualizationFactory
        factory = VisualizationFactory()
        print("✓ 成功创建工厂实例")
        return True
    except Exception as e:
        print(f"✗ 创建工厂实例时出错: {e}")
        return False

def test_strategy_selector():
    """测试策略选择器"""
    try:
        from Src.DataAnalyzer.DataVisualisationUpgrade.strategy import VisualizationStrategySelector
        selector = VisualizationStrategySelector()
        charts = selector.select_charts("classification", {})
        print(f"✓ 策略选择器工作正常，返回图表: {charts}")
        return True
    except Exception as e:
        print(f"✗ 策略选择器测试出错: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试DataVisualisationUpgrade模块...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_factory_creation,
        test_strategy_selector
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！")
        return 0
    else:
        print("部分测试失败！")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)