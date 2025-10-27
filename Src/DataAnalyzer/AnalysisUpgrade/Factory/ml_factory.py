"""
ML 工厂：根据 model_type 分发到各任务工厂
"""

from typing import Dict, Any, Optional, Type
from ..Cores.base_factory import BaseFactory
from ..Cores.base_analyzer import BaseAnalyzer
from .classification_factory import ClassificationFactory
from .regression_factory import RegressionFactory
from .clustering_factory import ClusteringFactory
from .dimensionality_reduction_factory import DimensionalityReductionFactory
from .anomaly_detection_factory import AnomalyDetectionFactory
from .transformer_factory import TransformerFactory


class MLFactory(BaseFactory):
    """
    机器学习工厂类，负责根据 model_type 分发到各任务工厂
    """
    
    # 任务工厂映射表
    _task_factories: Dict[str, Type[BaseFactory]] = {
        "classification": ClassificationFactory,
        "regression": RegressionFactory,
        "clustering": ClusteringFactory,
        "dimensionality_reduction": DimensionalityReductionFactory,
        "anomaly_detection": AnomalyDetectionFactory,
        "transformer": TransformerFactory
    }
    
    def create_analyzer(self, model_name: str, **kwargs) -> Optional[BaseAnalyzer]:
        """
        ML工厂不直接创建分析器实例，仅作分发使用
        
        参数:
            model_name (str): 模型类型
            **kwargs: 传递给分析器构造函数的参数
            
        返回:
            Optional[BaseAnalyzer]: 分析器实例，如果未找到则返回None
        """
        print("ML工厂不直接创建分析器，请使用get_factory方法获取对应的工厂实例")
        return None
    
    def register_analyzer(self, model_name: str, analyzer_class: Type[BaseAnalyzer]) -> None:
        """
        注册任务工厂类
        
        参数:
            model_name (str): 模型类型
            analyzer_class (Type[BaseAnalyzer]): 工厂类
        """
        self._task_factories[model_name.lower()] = analyzer_class  # type: ignore
        print(f"已注册任务工厂: {model_name} -> {analyzer_class.__name__}")
    
    def get_available_analyzers(self) -> list:
        """
        获取所有可用的任务工厂类型
        
        返回:
            list: 可用工厂类型列表
        """
        return list(self._task_factories.keys())
    
    def get_factory(self, model_type: str) -> Optional[BaseFactory]:
        """
        获取任务工厂实例
        
        参数:
            model_type (str): 模型类型
            
        返回:
            Optional[BaseFactory]: 工厂实例，如果未找到则返回None
        """
        factory_class = self._task_factories.get(model_type.lower())
        if factory_class:
            return factory_class()
        else:
            print(f"未找到对应的工厂: {model_type}")
            return None
    
    def register_factory(self, model_type: str, factory_class: Type[BaseFactory]) -> None:
        """
        注册任务工厂类
        
        参数:
            model_type (str): 模型类型
            factory_class (Type[BaseFactory]): 工厂类
        """
        self._task_factories[model_type.lower()] = factory_class
        print(f"已注册任务工厂: {model_type} -> {factory_class.__name__}")
    
    def get_available_factories(self) -> list:
        """
        获取所有可用的任务工厂类型
        
        返回:
            list: 可用工厂类型列表
        """
        return list(self._task_factories.keys())