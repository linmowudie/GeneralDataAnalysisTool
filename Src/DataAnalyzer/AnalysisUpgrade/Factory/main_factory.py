"""
主工厂：根据 learn_type 分发
"""

from typing import Dict, Any, Optional, Type
from ..Cores.base_factory import BaseFactory
from ..Cores.base_analyzer import BaseAnalyzer


class MainFactory:
    """
    主工厂类，根据 learn_type 选择对应的工厂
    """
    
    # 工厂映射表
    _factories: Dict[str, Any] = {}
    
    @classmethod
    def register_factory(cls, learn_type: str, factory_class: Type[BaseFactory]) -> None:
        """
        注册工厂类
        
        参数:
            learn_type (str): 学习类型
            factory_class (Type[BaseFactory]): 工厂类
        """
        cls._factories[learn_type.lower()] = factory_class
        print(f"已注册工厂: {learn_type} -> {factory_class.__name__}")
    
    @classmethod
    def create_factory(cls, learn_type: str) -> Optional[BaseFactory]:
        """
        创建工厂实例
        
        参数:
            learn_type (str): 学习类型
            
        返回:
            Optional[BaseFactory]: 工厂实例，如果未找到则返回None
        """
        factory_class = cls._factories.get(learn_type.lower())
        if factory_class:
            return factory_class()
        else:
            print(f"未找到对应的工厂: {learn_type}")
            return None
    
    @classmethod
    def get_available_factories(cls) -> list:
        """
        获取所有可用的工厂类型
        
        返回:
            list: 可用工厂类型列表
        """
        return list(cls._factories.keys())