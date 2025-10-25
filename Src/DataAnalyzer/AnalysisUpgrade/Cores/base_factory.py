"""
抽象工厂基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, Any, Optional
from .base_analyzer import BaseAnalyzer


class BaseFactory(ABC):
    """
    抽象工厂基类，定义工厂类的基本接口
    """
    
    @abstractmethod
    def create_analyzer(self, model_name: str, **kwargs) -> Optional[BaseAnalyzer]:
        """
        创建分析器实例
        
        参数:
            model_name (str): 模型名称
            **kwargs: 传递给分析器构造函数的参数
            
        返回:
            Optional[BaseAnalyzer]: 分析器实例，如果未找到则返回None
        """
        pass

    @abstractmethod
    def register_analyzer(self, model_name: str, analyzer_class: Type[BaseAnalyzer]) -> None:
        """
        注册分析器类
        
        参数:
            model_name (str): 模型名称
            analyzer_class (Type[BaseAnalyzer]): 分析器类
        """
        pass

    @abstractmethod
    def get_available_analyzers(self) -> list:
        """
        获取所有可用的分析器类型
        
        返回:
            list: 可用分析器类型列表
        """
        pass