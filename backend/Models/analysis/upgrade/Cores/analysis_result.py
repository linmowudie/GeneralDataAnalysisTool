"""
统一结果封装类
"""

from typing import Dict, Any, Optional, Union
import pandas as pd


class AnalysisResult:
    """
    分析结果封装类，用于统一各种分析任务的返回结果格式
    """
    
    def __init__(self, 
                 model: Optional[Any] = None,
                 model_score: Optional[Union[Dict[str, float], list]] = None,
                 train_set: Optional[pd.DataFrame] = None,
                 test_set: Optional[pd.DataFrame] = None,
                 feature_cols: Optional[list] = None,
                 encoding_method: Optional[Dict[str, str]] = None,
                 additional_info: Optional[Dict[str, Any]] = None):
        """
        初始化分析结果
        
        参数:
            model (Optional[Any]): 训练完成的模型对象
            model_score (Optional[Union[Dict[str, float], list]]): 模型评估得分
            train_set (Optional[pd.DataFrame]): 训练数据集
            test_set (Optional[pd.DataFrame]): 测试数据集
            feature_cols (Optional[list]): 特征列名列表
            encoding_method (Optional[Dict[str, str]]): 编码方式
            additional_info (Optional[Dict[str, Any]]): 额外信息
        """
        self.model = model
        self.model_score = model_score
        self.train_set = train_set
        self.test_set = test_set
        self.feature_cols = feature_cols
        self.encoding_method = encoding_method
        self.additional_info = additional_info or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        将结果转换为字典格式
        
        返回:
            Dict[str, Any]: 结果字典
        """
        return {
            "model": self.model,
            "model_score": self.model_score,
            "train_set": self.train_set,
            "test_set": self.test_set,
            "feature_cols": self.feature_cols,
            "encoding_method": self.encoding_method,
            **self.additional_info
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """
        从字典创建分析结果实例
        
        参数:
            data (Dict[str, Any]): 数据字典
            
        返回:
            AnalysisResult: 分析结果实例
        """
        return cls(**data)