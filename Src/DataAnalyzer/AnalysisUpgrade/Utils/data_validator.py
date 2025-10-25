"""
数据校验工具
"""

import pandas as pd
from typing import List, Any


def validate_dataframe(df: pd.DataFrame, name: str = "DataFrame") -> bool:
    """
    验证DataFrame是否有效
    
    参数:
        df (pd.DataFrame): 待验证的DataFrame
        name (str): DataFrame名称，用于错误消息
        
    返回:
        bool: 验证是否通过
    """
    if df is None:
        print(f"错误: {name} 不能为 None")
        return False
        
    if not isinstance(df, pd.DataFrame):
        print(f"错误: {name} 必须是 pandas.DataFrame 类型")
        return False
        
    if df.empty:
        print(f"错误: {name} 不能为空")
        return False
        
    return True


def validate_columns_exist(df: pd.DataFrame, columns: List[str], name: str = "DataFrame") -> bool:
    """
    验证DataFrame中是否存在指定列
    
    参数:
        df (pd.DataFrame): DataFrame
        columns (List[str]): 列名列表
        name (str): DataFrame名称，用于错误消息
        
    返回:
        bool: 验证是否通过
    """
    if not validate_dataframe(df, name):
        return False
        
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        print(f"错误: {name} 中缺少列: {missing_cols}")
        return False
        
    return True