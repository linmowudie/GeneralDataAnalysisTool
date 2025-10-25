"""
ML 工厂：创建任务分析器 + 策略
"""

from typing import Dict, Any, Optional, Type


class MLFactory:
    """
    机器学习工厂类，负责创建各类机器学习分析器实例
    """
    
    _ml_analyzers: Dict[str, Type[Any]] = {}
    
    @classmethod
    def register_ml_analyzer(cls, model_type: str, analyzer_class: Type[Any]) -> None:
        """
        注册机器学习分析器类
        
        参数:
            model_type (str): 模型类型
            analyzer_class (Type[Any]): 分析器类
        """
        cls._ml_analyzers[model_type] = analyzer_class
        print(f"已注册机器学习分析器: {model_type}")
    
    @classmethod
    def create_ml_analyzer(cls, model_type: str, **kwargs) -> Optional[Any]:
        """
        创建机器学习分析器实例
        
        参数:
            model_type (str): 模型类型
            **kwargs: 传递给分析器构造函数的参数
            
        返回:
            Optional[Any]: 分析器实例，如果未找到则返回None
        """
        analyzer_class = cls._ml_analyzers.get(model_type)
        if analyzer_class:
            try:
                analyzer = analyzer_class(**kwargs)
                print(f"成功创建机器学习分析器实例: {model_type}")
                return analyzer
            except Exception as e:
                print(f"创建机器学习分析器实例失败: {model_type}, 错误: {e}")
                return None
        else:
            print(f"未找到对应的机器学习分析器: {model_type}")
            return None