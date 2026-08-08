"""
抽象策略基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    抽象策略基类，定义策略类的基本接口
    """
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行策略
        
        参数:
            **kwargs: 执行参数
            
        返回:
            Dict[str, Any]: 执行结果
        """
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        验证参数
        
        参数:
            params (Dict[str, Any]): 参数字典
            
        返回:
            bool: 验证是否通过
        """
        pass