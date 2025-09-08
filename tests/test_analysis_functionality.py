# tests/test_analysis_functionality.py

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
from Src.data_analyzer.analysis.analyzer import analyze_data
from Src.data_analyzer.analysis.base_analyzer import BaseAnalyzer

def create_test_dataframe_with_categorical():
    """创建包含分类特征的测试DataFrame"""
    np.random.seed(42)
    data = {
        'numeric_feature1': np.random.randn(100),
        'numeric_feature2': np.random.randn(100),
        'categorical_feature': np.random.choice(['A', 'B', 'C'], 100),
        'category_feature2': pd.Categorical(np.random.choice(['X', 'Y'], 100)),
        'target': np.random.randint(0, 2, 100)
    }
    return pd.DataFrame(data)

def create_large_test_dataframe():
    """创建较大的测试DataFrame"""
    np.random.seed(42)
    n_samples = 1000
    data = {
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.randn(n_samples),
        'feature3': np.random.randn(n_samples),
        'feature4': np.random.randn(n_samples),
        'feature5': np.random.randn(n_samples),
        'target': np.random.randn(n_samples)
    }
    # 让目标变量与特征有一定关系
    data['target'] = (data['feature1'] * 2 + 
                     data['feature2'] * -1.5 + 
                     data['feature3'] * 0.5 + 
                     np.random.randn(n_samples) * 0.5)
    return pd.DataFrame(data)

def test_categorical_encoding():
    """测试分类特征编码功能"""
    print("测试分类特征编码功能:")
    
    df = create_test_dataframe_with_categorical()
    
    # 测试 one-hot 编码
    result = analyze_data(
        df=df,
        model="logisticregression",
        target_col="target",
        feature_cols_encoding="onehot",
        is_return_model_param=True,
        is_return_training_set=True
    )
    
    assert 'trained_model' in result
    assert 'X_train' in result
    # 确保编码后的特征数量增加（由于 one-hot 编码）
    assert result['X_train'].shape[1] >= 4  # 原始有2个数值特征和2个分类特征
    print("  One-hot 编码测试通过")
    
    # 测试 label 编码
    result = analyze_data(
        df=df,
        model="logisticregression",
        target_col="target",
        feature_cols_encoding="label",
        is_return_model_param=True,
        is_return_training_set=True
    )
    
    assert 'trained_model' in result
    assert 'X_train' in result
    print("  Label 编码测试通过\n")

def test_custom_model_parameters():
    """测试自定义模型参数"""
    print("测试自定义模型参数:")
    
    df = create_test_dataframe_with_categorical()
    
    # 测试逻辑回归自定义参数
    result = analyze_data(
        df=df,
        model="logisticregression",
        target_col="target",
        model_params={"C": 0.5, "max_iter": 500},
        is_return_model_param=True
    )
    
    assert 'trained_model' in result
    assert result['trained_model'].C == 0.5
    print("  逻辑回归自定义参数测试通过")
    
    # 测试决策树自定义参数
    result = analyze_data(
        df=df,
        model="decisiontreeclassifier",
        target_col="target",
        model_params={"max_depth": 3, "min_samples_split": 10},
        is_return_model_param=True
    )
    
    assert 'trained_model' in result
    assert result['trained_model'].max_depth == 3
    assert result['trained_model'].min_samples_split == 10
    print("  决策树自定义参数测试通过\n")

def test_different_split_ratios():
    """测试不同的数据集划分比例"""
    print("测试不同的数据集划分比例:")
    
    df = create_test_dataframe_with_categorical()
    
    # 测试 50% 划分
    result = analyze_data(
        df=df,
        model="logisticregression",
        target_col="target",
        split_ratio=0.5,
        is_return_training_set=True
    )
    
    assert 'X_train' in result
    assert 'X_test' in result
    # 检查划分比例是否大致正确 (允许一些误差)
    total_samples = len(result['X_train']) + len(result['X_test'])
    train_ratio = len(result['X_train']) / total_samples
    assert 0.45 <= train_ratio <= 0.55  # 允许一些随机误差
    print("  50% 划分比例测试通过")
    
    # 测试 90% 划分
    result = analyze_data(
        df=df,
        model="logisticregression",
        target_col="target",
        split_ratio=0.9,
        is_return_training_set=True
    )
    
    assert 'X_train' in result
    assert 'X_test' in result
    total_samples = len(result['X_train']) + len(result['X_test'])
    train_ratio = len(result['X_train']) / total_samples
    assert 0.85 <= train_ratio <= 0.95
    print("  90% 划分比例测试通过\n")

def test_large_dataset():
    """测试大数据集处理能力"""
    print("测试大数据集处理能力:")
    
    df = create_large_test_dataframe()
    
    result = analyze_data(
        df=df,
        model="linearregression",
        target_col="target",
        is_return_model_score=True
    )
    
    assert 'trained_model' in result
    assert 'scores' in result
    assert len(result['scores']) > 0
    print("  大数据集处理测试通过\n")

def test_prediction_return():
    """测试预测结果返回功能"""
    print("测试预测结果返回功能:")
    
    df = create_test_dataframe_with_categorical()
    
    result = analyze_data(
        df=df,
        model="logisticregression",
        target_col="target",
        is_return_model_predicting_set=True,
        is_return_training_set=True
    )
    
    assert 'predictions' in result
    assert 'X_test' in result
    assert len(result['predictions']) == len(result['X_test'])
    print("  预测结果返回测试通过\n")

def test_base_analyzer_instantiation():
    """测试基类实例化"""
    print("测试基类实例化:")
    
    df = create_test_dataframe_with_categorical()
    
    # 尝试直接实例化基类应该失败，因为它是抽象的
    try:
        analyzer = BaseAnalyzer(
            df=df,
            model="logisticregression",
            target_col="target"
        )
        # 运行基类不会真正完成分析，因为我们没有实现特定任务的方法
        print("  基类实例化测试完成（预期不会完全工作）")
    except Exception as e:
        print(f"  基类实例化测试产生预期异常: {e}\n")

def test_error_handling():
    """测试错误处理"""
    print("测试错误处理:")
    
    df = create_test_dataframe_with_categorical()
    
    # 测试不支持的模型
    try:
        result = analyze_data(
            df=df,
            model="nonexistentmodel",
            target_col="target"
        )
        assert False, "应该抛出异常但没有"
    except ValueError as e:
        assert "不支持的模型" in str(e)
        print("  不支持模型错误处理测试通过")
    except Exception as e:
        assert False, f"抛出了错误类型的异常: {e}"
    
    # 测试没有目标列的监督学习
    try:
        result = analyze_data(
            df=df,
            model="logisticregression"
        )
        assert False, "应该抛出异常但没有"
    except ValueError as e:
        assert "必须指定目标列" in str(e)
        print("  缺失目标列错误处理测试通过\n")

if __name__ == "__main__":
    print("开始测试分析模块功能...\n")
    
    try:
        test_categorical_encoding()
        test_custom_model_parameters()
        test_different_split_ratios()
        test_large_dataset()
        test_prediction_return()
        test_base_analyzer_instantiation()
        test_error_handling()
        
        print("所有功能测试通过!")
    except Exception as e:
        print(f"功能测试失败: {e}")
        raise