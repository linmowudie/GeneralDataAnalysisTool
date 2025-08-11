# tests/test_data_cleaning.py

import sys
import os
import pandas as pd
import numpy as np

# 获取项目根目录（tests 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==================================================

# 导入需要测试的模块
from Src.data_analyzer.data_cleaning import CleanDataMode

def create_test_dataframe():
    """创建用于测试的DataFrame"""
    data = {
        'A': [1, 2, np.nan, 4, 5, 2],  # 包含缺失值和重复值
        'B': ['x', 'y', 'z', 'x', 'y', 'y'],  # 包含重复值
        'C': [10, 20, 30, np.nan, 50, 20],  # 包含缺失值和重复值
        'D': [100, 200, 300, 400, 500, 200]  # 包含重复值
    }
    return pd.DataFrame(data)

def test_standard_mode():
    """测试标准清洗模式"""
    print("测试标准清洗模式 (standard):")
    df = create_test_dataframe()
    print("清洗前数据:")
    print(df)
    print(f"形状: {df.shape}")
    
    # 使用标准模式清洗数据
    cleaner = CleanDataMode(df, "standard", [])
    cleaned_df = cleaner.clean_data()
    
    print("\n清洗后数据:")
    print(cleaned_df)
    print(f"形状: {cleaned_df.shape}")
    
    # 验证清洗结果
    assert isinstance(cleaned_df, pd.DataFrame), "返回值应该是一个DataFrame"
    assert len(cleaned_df) <= len(df), "清洗后的数据行数应该小于或等于原始数据"
    assert not cleaned_df.duplicated().any(), "清洗后的数据不应该有重复行"
    print("✅ 标准模式测试通过\n")

def test_strict_mode():
    """测试严格清洗模式"""
    print("测试严格清洗模式 (strict):")
    df = create_test_dataframe()
    print("清洗前数据:")
    print(df)
    print(f"形状: {df.shape}")
    
    # 使用严格模式清洗数据
    cleaner = CleanDataMode(df, "strict", [])
    cleaned_df = cleaner.clean_data()
    
    print("\n清洗后数据:")
    print(cleaned_df)
    print(f"形状: {cleaned_df.shape}")
    
    # 验证清洗结果
    assert isinstance(cleaned_df, pd.DataFrame), "返回值应该是一个DataFrame"
    assert len(cleaned_df) <= len(df), "清洗后的数据行数应该小于或等于原始数据"
    assert not cleaned_df.isnull().any().any(), "清洗后的数据不应该有缺失值"
    assert not cleaned_df.duplicated().any(), "清洗后的数据不应该有重复行"
    print("✅ 严格模式测试通过\n")

def test_relaxed_mode():
    """测试宽松清洗模式"""
    print("测试宽松清洗模式 (relaxed):")
    df = create_test_dataframe()
    print("清洗前数据:")
    print(df)
    print(f"形状: {df.shape}")
    
    # 使用宽松模式清洗数据
    cleaner = CleanDataMode(df, "relaxed", [])
    cleaned_df = cleaner.clean_data()
    
    print("\n清洗后数据:")
    print(cleaned_df)
    print(f"形状: {cleaned_df.shape}")
    
    # 验证清洗结果
    assert isinstance(cleaned_df, pd.DataFrame), "返回值应该是一个DataFrame"
    assert len(cleaned_df) <= len(df), "清洗后的数据行数应该小于或等于原始数据"
    assert not cleaned_df.duplicated().any(), "清洗后的数据不应该有重复行"
    print("✅ 宽松模式测试通过\n")

def test_custom_mode():
    """测试自定义清洗模式"""
    print("测试自定义清洗模式 (custom):")
    df = create_test_dataframe()
    print("清洗前数据:")
    print(df)
    print(f"形状: {df.shape}")
    
    # 使用自定义参数清洗数据
    params = [
        "drop_duplicates=True",
        "handle_missing='fill'",
        "fill_method='mean'"
    ]
    cleaner = CleanDataMode(df, "custom", params, is_freedom_params=True)
    cleaned_df = cleaner.clean_data()
    
    print("\n清洗后数据:")
    print(cleaned_df)
    print(f"形状: {cleaned_df.shape}")
    
    # 验证清洗结果
    assert isinstance(cleaned_df, pd.DataFrame), "返回值应该是一个DataFrame"
    assert len(cleaned_df) <= len(df), "清洗后的数据行数应该小于或等于原始数据"
    assert not cleaned_df.duplicated().any(), "清洗后的数据不应该有重复行"
    print("✅ 自定义模式测试通过\n")

def test_invalid_mode():
    """测试无效模式"""
    print("测试无效清洗模式:")
    df = create_test_dataframe()
    
    try:
        cleaner = CleanDataMode(df, "invalid_mode", [])
        cleaned_df = cleaner.clean_data()
        # 如果没有抛出异常，则测试失败
        print("❌ 无效模式测试失败 - 应该抛出异常")
    except ValueError as e:
        print(f"✅ 无效模式测试通过 - 正确捕获异常: {e}\n")
    except Exception as e:
        print(f"❌ 无效模式测试失败 - 捕获到意外异常: {e}\n")

# 测试代码
if __name__ == "__main__":
    print("开始测试 data_cleaning 模块\n")
    print("="*50 + "\n")
    
    # 运行各种测试
    test_standard_mode()
    test_strict_mode()
    test_relaxed_mode()
    test_custom_mode()
    test_invalid_mode()
    
    print("="*50)
    print("所有测试完成!")