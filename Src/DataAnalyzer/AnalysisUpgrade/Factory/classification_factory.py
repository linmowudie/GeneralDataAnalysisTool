"""
分类任务工厂
"""

from typing import Dict, Any, Optional, Type
from ..Cores.base_analyzer import BaseAnalyzer
from ..Cores.base_factory import BaseFactory


class ClassificationFactory(BaseFactory):
    """
    分类任务工厂类，负责创建各类分类分析器实例
    """
    
    _classification_analyzers: Dict[str, Type[BaseAnalyzer]] = {}
    
    def create_analyzer(self, model_name: str, **kwargs) -> Optional[BaseAnalyzer]:
        """
        创建分类分析器实例
        
        参数:
            model_name (str): 模型名称
            **kwargs: 传递给分析器构造函数的参数
            
        返回:
            Optional[BaseAnalyzer]: 分析器实例，如果未找到则返回None
        """
        analyzer_class = self._classification_analyzers.get(model_name)
        if analyzer_class:
            try:
                analyzer = analyzer_class(**kwargs)
                print(f"成功创建分类分析器实例: {model_name}")
                return analyzer
            except Exception as e:
                print(f"创建分类分析器实例失败: {model_name}, 错误: {e}")
                return None
        else:
            print(f"未找到对应的分类分析器: {model_name}")
            return None
    
    def register_analyzer(self, model_name: str, analyzer_class: Type[BaseAnalyzer]) -> None:
        """
        注册分类分析器类
        
        参数:
            model_name (str): 模型名称
            analyzer_class (Type[BaseAnalyzer]): 分析器类
        """
        self._classification_analyzers[model_name] = analyzer_class
        print(f"已注册分类分析器: {model_name}")
    
    def get_available_analyzers(self) -> list:
        """
        获取所有可用的分类分析器类型
        
        返回:
            list: 可用分析器类型列表
        """
        return list(self._classification_analyzers.keys())