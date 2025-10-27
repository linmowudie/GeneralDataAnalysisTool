"""
数据转换任务策略
"""

from ..Cores.base_strategy import BaseStrategy
from typing import Dict, Any
import pandas as pd
import numpy as np


class TransformerStrategy(BaseStrategy):
    """
    数据转换任务策略类，控制数据转换分析流程的执行顺序和逻辑
    """
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行数据转换分析策略
        
        参数:
            **kwargs: 分析参数
                - df: 数据集
                - feature_cols: 特征列名列表
                - model: 模型实例
                
        返回:
            Dict[str, Any]: 分析结果
        """
        try:
            df = kwargs.get("df")
            feature_cols = kwargs.get("feature_cols", [])
            model = kwargs.get("model")
            
            if df is None or not feature_cols or model is None:
                return {"error": "缺少必要的参数: df, feature_cols, model"}
            
            # 准备数据
            X = df[feature_cols]
            
            # 执行数据转换
            X_transformed = model.fit_transform(X)
            
            # 计算统计信息
            results = {
                "model": model,
                "transformed_data": X_transformed.tolist(),
                "original_shape": X.shape if hasattr(X, 'shape') else None,
                "transformed_shape": X_transformed.shape if hasattr(X_transformed, 'shape') else None
            }
            
            # 如果是标准化或归一化转换，可以提供一些统计信息
            if hasattr(model, 'scale_') or hasattr(model, 'var_'):
                stats = {}
                if hasattr(model, 'mean_'):
                    stats['mean'] = model.mean_.tolist() if hasattr(model.mean_, 'tolist') else model.mean_
                if hasattr(model, 'scale_'):
                    stats['scale'] = model.scale_.tolist() if hasattr(model.scale_, 'tolist') else model.scale_
                if hasattr(model, 'var_'):
                    stats['var'] = model.var_.tolist() if hasattr(model.var_, 'tolist') else model.var_
                
                if stats:
                    results['transform_stats'] = stats
            
            return results
            
        except Exception as e:
            return {"error": f"执行数据转换分析策略时出错: {str(e)}"}

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        验证数据转换任务参数
        
        参数:
            params (Dict[str, Any]): 参数字典
            
        返回:
            bool: 验证是否通过
        """
        # 实现数据转换任务特定的参数验证逻辑
        required_params = ["df", "feature_cols"]
        for param in required_params:
            if param not in params:
                print(f"缺少必要参数: {param}")
                return False
        
        # 验证数据类型
        df = params["df"]
        if not isinstance(df, pd.DataFrame):
            print("df必须是pandas DataFrame类型")
            return False
            
        feature_cols = params["feature_cols"]
        if not isinstance(feature_cols, list):
            print("feature_cols必须是列表类型")
            return False
            
        # 检查列是否存在
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            print(f"以下特征列在数据中不存在: {missing_cols}")
            return False
            
        return True