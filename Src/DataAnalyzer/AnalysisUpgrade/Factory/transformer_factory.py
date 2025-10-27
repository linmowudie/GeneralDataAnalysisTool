"""
数据转换任务工厂
"""

from typing import Dict, Any, Optional, Type
from ..Cores.base_analyzer import BaseAnalyzer
from ..Cores.base_factory import BaseFactory


class TransformerFactory(BaseFactory):
    """
    数据转换任务工厂类，负责创建各类数据转换分析器实例
    """
    
    _transformer_analyzers: Dict[str, Type[BaseAnalyzer]] = {}
    
    def create_analyzer(self, model_name: str, **kwargs) -> Optional[BaseAnalyzer]:
        """
        创建数据转换分析器实例
        
        参数:
            model_name (str): 模型名称
            **kwargs: 传递给分析器构造函数的参数
            
        返回:
            Optional[BaseAnalyzer]: 分析器实例，如果未找到则返回None
        """
        analyzer_class = self._transformer_analyzers.get(model_name)
        if analyzer_class:
            try:
                analyzer = analyzer_class(**kwargs)
                print(f"成功创建数据转换分析器实例: {model_name}")
                return analyzer
            except Exception as e:
                print(f"创建数据转换分析器实例失败: {model_name}, 错误: {e}")
                return None
        else:
            print(f"未找到对应的数据转换分析器: {model_name}")
            return None
    
    def register_analyzer(self, model_name: str, analyzer_class: Type[BaseAnalyzer]) -> None:
        """
        注册数据转换分析器类
        
        参数:
            model_name (str): 模型名称
            analyzer_class (Type[BaseAnalyzer]): 分析器类
        """
        self._transformer_analyzers[model_name] = analyzer_class
        print(f"已注册数据转换分析器: {model_name}")
    
    def get_available_analyzers(self) -> list:
        """
        获取所有可用的数据转换分析器类型
        
        返回:
            list: 可用分析器类型列表
        """
        return list(self._transformer_analyzers.keys())