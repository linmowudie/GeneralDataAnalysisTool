"""
DL 工厂（预留）
"""

from typing import Dict, Any, Optional, Type
from ..Cores.base_factory import BaseFactory
from ..Cores.base_analyzer import BaseAnalyzer


class DLFactory(BaseFactory):
    """
    深度学习工厂类，专门负责根据 model_type 分发到各深度学习任务工厂
    目前预留接口，可用于扩展深度学习功能
    """
    
    # 深度学习任务工厂映射表（预留）
    _dl_task_factories: Dict[str, Type[BaseFactory]] = {}
    
    def create_analyzer(self, model_name: str, **kwargs) -> Optional[BaseAnalyzer]:
        """
        DL工厂不直接创建分析器实例，仅作分发使用
        
        参数:
            model_name (str): 模型类型
            **kwargs: 传递给分析器构造函数的参数
            
        返回:
            Optional[BaseAnalyzer]: 分析器实例，如果未找到则返回None
        """
        print("DL工厂不直接创建分析器，请使用get_factory方法获取对应的工厂实例")
        return None
    
    def register_analyzer(self, model_name: str, analyzer_class: Type[BaseAnalyzer]) -> None:
        """
        注册深度学习任务工厂类
        
        参数:
            model_name (str): 模型类型
            analyzer_class (Type[BaseAnalyzer]): 工厂类
        """
        self._dl_task_factories[model_name.lower()] = analyzer_class  # type: ignore
        print(f"已注册深度学习任务工厂: {model_name} -> {analyzer_class.__name__}")
    
    def get_available_analyzers(self) -> list:
        """
        获取所有可用的深度学习任务工厂类型
        
        返回:
            list: 可用工厂类型列表
        """
        return list(self._dl_task_factories.keys())
    
    def get_factory(self, model_type: str) -> Optional[BaseFactory]:
        """
        获取深度学习任务工厂实例
        
        参数:
            model_type (str): 模型类型
            
        返回:
            Optional[BaseFactory]: 工厂实例，如果未找到则返回None
        """
        factory_class = self._dl_task_factories.get(model_type.lower())
        if factory_class:
            return factory_class()
        else:
            print(f"未找到对应的深度学习任务工厂: {model_type}")
            return None
    
    def register_factory(self, model_type: str, factory_class: Type[BaseFactory]) -> None:
        """
        注册深度学习任务工厂类
        
        参数:
            model_type (str): 模型类型
            factory_class (Type[BaseFactory]): 工厂类
        """
        self._dl_task_factories[model_type.lower()] = factory_class
        print(f"已注册深度学习任务工厂: {model_type} -> {factory_class.__name__}")
    
    def get_available_factories(self) -> list:
        """
        获取所有可用的深度学习任务工厂类型
        
        返回:
            list: 可用工厂类型列表
        """
        return list(self._dl_task_factories.keys())