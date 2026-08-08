"""
测试工厂分发机制
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 直接导入需要的模块，避免复杂的依赖
from backend.Models.analysis.upgrade.Factory.main_factory import MainFactory
from backend.Models.analysis.upgrade.Factory.ml_factory import MLFactory
from backend.Models.analysis.upgrade.Factory.classification_factory import ClassificationFactory


def test_main_factory_dispatch():
    """测试主工厂分发功能"""
    print("=== 测试主工厂分发功能 ===")
    main_factory = MainFactory()
    
    # 注册ML工厂
    main_factory.register_factory("ML", MLFactory)  # type: ignore
    print(f"主工厂可用工厂类型: {main_factory.get_available_factories()}")
    
    # 获取ML工厂
    ml_factory = main_factory.get_factory("ML")
    if ml_factory:
        print(f"成功获取ML工厂: {type(ml_factory).__name__}")
        print(f"ML工厂可用任务工厂类型: {ml_factory.get_available_factories()}")  # type: ignore
        
        # 获取分类任务工厂
        classification_factory = ml_factory.get_factory("classification")  # type: ignore
        if classification_factory:
            print(f"成功获取分类任务工厂: {type(classification_factory).__name__}")
        else:
            print("获取分类任务工厂失败")
    else:
        print("获取ML工厂失败")


def test_ml_factory_dispatch():
    """测试ML工厂分发功能"""
    print("\n=== 测试ML工厂分发功能 ===")
    ml_factory = MLFactory()
    
    print(f"ML工厂可用任务工厂类型: {ml_factory.get_available_factories()}")
    
    # 测试获取各种任务工厂
    task_types = ["classification", "regression", "clustering", "dimensionality_reduction", "anomaly_detection", "transformer"]
    
    for task_type in task_types:
        factory = ml_factory.get_factory(task_type)  # type: ignore
        if factory:
            print(f"成功获取{task_type}任务工厂: {type(factory).__name__}")
        else:
            print(f"获取{task_type}任务工厂失败")


def test_classification_factory():
    """测试分类任务工厂功能"""
    print("\n=== 测试分类任务工厂功能 ===")
    classification_factory = ClassificationFactory()
    
    print(f"分类任务工厂可用分析器类型: {classification_factory.get_available_analyzers()}")
    
    # 尝试创建一个分析器实例（这里会失败，因为具体的分析器还没实现）
    analyzer = classification_factory.create_analyzer("random_forest")
    if analyzer:
        print(f"成功创建分析器实例: {type(analyzer).__name__}")
    else:
        print("创建分析器实例失败（可能是分析器尚未实现）")


if __name__ == "__main__":
    print("开始测试工厂分发机制...")
    
    try:
        test_main_factory_dispatch()
        test_ml_factory_dispatch()
        test_classification_factory()
        
        print("\n=== 测试完成 ===")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()