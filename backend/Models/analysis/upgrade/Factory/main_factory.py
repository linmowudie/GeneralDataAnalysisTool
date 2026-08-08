"""
主工厂：根据 learn_type 分发
"""

from typing import Dict, Any, Optional, Type
from ..Cores.base_factory import BaseFactory
from ..Cores.base_analyzer import BaseAnalyzer


class MainFactory(BaseFactory):
    """
    主工厂类，根据 learn_type 选择对应的工厂
    """
    
    # 工厂映射表
    _factories: Dict[str, Type[BaseFactory]] = {}
    
    def create_analyzer(self, model_name: str, **kwargs) -> Optional[BaseAnalyzer]:
        """
        主工厂不直接创建分析器实例，仅作分发使用
        
        参数:
            model_name (str): 学习类型（ML 或 DL）
            **kwargs: 传递给分析器构造函数的参数
            
        返回:
            Optional[BaseAnalyzer]: 分析器实例，如果未找到则返回None
        """
        print("主工厂不直接创建分析器，请使用get_factory方法获取对应的工厂实例")
        return None
    
    def register_analyzer(self, model_name: str, analyzer_class: Type[BaseAnalyzer]) -> None:
        """
        注册工厂类
        
        参数:
            model_name (str): 学习类型
            analyzer_class (Type[BaseAnalyzer]): 工厂类（在主工厂中实际上是工厂类）
        """
        # 由于BaseFactory接口要求analyzer_class是BaseAnalyzer类型，但我们实际需要的是工厂类
        # 这里为了保持接口一致性，我们假设传入的是工厂类但类型标注为BaseAnalyzer
        self._factories[model_name.lower()] = analyzer_class  # type: ignore
        print(f"已注册工厂: {model_name} -> {analyzer_class.__name__}")
    
    def get_available_analyzers(self) -> list:
        """
        获取所有可用的工厂类型
        
        返回:
            list: 可用工厂类型列表
        """
        return list(self._factories.keys())
    
    def get_factory(self, model_type: str) -> Optional[BaseFactory]:
        """
        获取工厂实例
        
        参数:
            model_type (str): 学习类型（ML 或 DL）
            
        返回:
            Optional[BaseFactory]: 工厂实例，如果未找到则返回None
        """
        factory_class = self._factories.get(model_type.lower())
        if factory_class:
            return factory_class()
        else:
            print(f"未找到对应的工厂: {model_type}")
            return None
    
    def register_factory(self, model_type: str, factory_class: Type[BaseFactory]) -> None:
        """
        注册工厂类
        
        参数:
            model_type (str): 学习类型
            factory_class (Type[BaseFactory]): 工厂类
        """
        self._factories[model_type.lower()] = factory_class
        print(f"已注册工厂: {model_type} -> {factory_class.__name__}")
    
    def get_available_factories(self) -> list:
        """
        获取所有可用的工厂类型
        
        返回:
            list: 可用工厂类型列表
        """
        return list(self._factories.keys())