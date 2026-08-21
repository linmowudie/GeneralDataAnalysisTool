"""
策略执行上下文
"""

from typing import Dict, Any, Optional
from .base_strategy import BaseStrategy


class AnalysisContext:
    """
    分析上下文，用于管理策略的执行流程
    """
    
    def __init__(self, strategy: Optional[BaseStrategy] = None):
        """
        初始化分析上下文
        
        参数:
            strategy (Optional[BaseStrategy]): 策略实例
        """
        self._strategy = strategy

    @property
    def strategy(self) -> Optional[BaseStrategy]:
        """
        获取当前策略
        
        返回:
            Optional[BaseStrategy]: 当前策略实例
        """
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: BaseStrategy) -> None:
        """
        设置策略
        
        参数:
            strategy (BaseStrategy): 策略实例
        """
        self._strategy = strategy

    def execute_strategy(self, **kwargs) -> Dict[str, Any]:
        """
        执行策略
        
        参数:
            **kwargs: 执行参数
            
        返回:
            Dict[str, Any]: 执行结果
        """
        if self._strategy is not None:
            return self._strategy.execute(**kwargs)
        else:
            raise ValueError("未设置策略")