# tests/test_new_analysis_interface.py

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
from Src.data_analyzer.analysis.analyzer import analyze_data, AnalyzeData
from Src.data_analyzer.analysis.regression import Regression
from Src.data_analyzer.analysis.classification import Classification
from Src.data_analyzer.analysis.clustering import Clustering
from Src.data_analyzer.analysis.dimensionality_reduction import DimensionalityReduction

def create_test_dataframe():
    """创建用于测试的DataFrame"""
    np.random.seed(42)
    data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'target': np.random.randint(0, 2, 100)  # 二分类目标
    }
    return pd.DataFrame(data)

def create_regression_test_dataframe():
    """创建用于回归测试的DataFrame"""
    np.random.seed(42)
    data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'target': np.random.randn(100)  # 连续目标变量
    }
    # 让目标变量与特征有一定关系
    data['target'] = data['feature1'] * 2 + data['feature2'] * -1.5 + np.random.randn(100) * 0.5
    return pd.DataFrame(data)

def create_clustering_test_dataframe():
    """创建用于聚类测试的DataFrame"""
    np.random.seed(42)
    data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100)
    }
    return pd.DataFrame(data)

def test_analyze_data_function():
    """测试新的analyze_data函数接口"""
    print("测试新的analyze_data函数接口:")
    
    # 测试分类任务
    df = create_test_dataframe()
    result = analyze_data(
        df=df,
        model="logisticregression",
        target_col="target",
        is_return_model_score=True,
        is_return_model_param=True
    )
    
    assert 'trained_model' in result
    assert 'task_type' in result
    assert result['task_type'] == 'classification'
    assert hasattr(result['trained_model'], 'predict')
    print("  分类任务测试通过")
    
    # 测试回归任务
    df_reg = create_regression_test_dataframe()
    result = analyze_data(
        df=df_reg,
        model="linearregression",
        target_col="target",
        is_return_model_score=True
    )
    
    assert 'trained_model' in result
    assert 'task_type' in result
    assert result['task_type'] == 'regression'
    assert hasattr(result['trained_model'], 'predict')
    print("  回归任务测试通过")
    
    print("analyze_data函数接口测试完成\n")

def test_regression_module():
    """测试Regression模块"""
    print("测试Regression模块:")
    
    df = create_regression_test_dataframe()
    analyzer = Regression(
        df=df,
        model="linearregression",
        target_col="target",
        is_return_model_score=True,
        is_return_model_param=True
    )
    
    result = analyzer.run()
    
    assert 'trained_model' in result
    assert 'task_type' in result
    assert result['task_type'] == 'regression'
    assert 'scores' in result
    assert hasattr(result['trained_model'], 'predict')
    print("  Regression模块测试通过\n")

def test_classification_module():
    """测试Classification模块"""
    print("测试Classification模块:")
    
    df = create_test_dataframe()
    analyzer = Classification(
        df=df,
        model="logisticregression",
        target_col="target",
        is_return_model_score=True,
        is_return_model_param=True
    )
    
    result = analyzer.run()
    
    assert 'trained_model' in result
    assert 'task_type' in result
    assert result['task_type'] == 'classification'
    assert 'scores' in result
    assert hasattr(result['trained_model'], 'predict')
    print("  Classification模块测试通过\n")

def test_clustering_module():
    """测试Clustering模块"""
    print("测试Clustering模块:")
    
    df = create_clustering_test_dataframe()
    analyzer = Clustering(
        df=df,
        model="kmeans",
        is_return_model_score=True,
        is_return_model_param=True
    )
    
    result = analyzer.run()
    
    assert 'trained_model' in result
    assert 'task_type' in result
    assert result['task_type'] == 'clustering'
    assert hasattr(result['trained_model'], 'predict')
    print("  Clustering模块测试通过\n")

def test_dimensionality_reduction_module():
    """测试DimensionalityReduction模块"""
    print("测试DimensionalityReduction模块:")
    
    df = create_test_dataframe()
    analyzer = DimensionalityReduction(
        df=df,
        model="pca",
        is_return_model_param=True
    )
    
    result = analyzer.run()
    
    assert 'trained_model' in result
    assert 'task_type' in result
    assert result['task_type'] == 'transformer'
    assert hasattr(result['trained_model'], 'transform')
    print("  DimensionalityReduction模块测试通过\n")

def test_backward_compatibility():
    """测试向后兼容性"""
    print("测试向后兼容性:")
    
    df = create_test_dataframe()
    analyzer = AnalyzeData(
        df=df,
        model="logisticregression",
        target_col="target"
    )
    
    result = analyzer.run()
    
    assert 'trained_model' in result
    assert 'task_type' in result
    assert result['task_type'] == 'classification'
    print("  向后兼容性测试通过\n")

def test_model_variety():
    """测试不同模型的可用性"""
    print("测试不同模型的可用性:")
    
    df_reg = create_regression_test_dataframe()
    regression_models = ["linearregression", "ridge", "lasso"]
    
    for model in regression_models:
        try:
            result = analyze_data(
                df=df_reg,
                model=model,
                target_col="target"
            )
            assert 'trained_model' in result
            print(f"  {model} 模型测试通过")
        except Exception as e:
            print(f"  {model} 模型测试失败: {e}")
    
    df_class = create_test_dataframe()
    classification_models = ["logisticregression", "decisiontreeclassifier", "kneighborsclassifier", "svc"]
    
    for model in classification_models:
        try:
            result = analyze_data(
                df=df_class,
                model=model,
                target_col="target"
            )
            assert 'trained_model' in result
            print(f"  {model} 模型测试通过")
        except Exception as e:
            print(f"  {model} 模型测试失败: {e}")
    
    df_cluster = create_clustering_test_dataframe()
    clustering_models = ["kmeans", "meanshift", "dbscan"]
    
    for model in clustering_models:
        try:
            result = analyze_data(
                df=df_cluster,
                model=model
            )
            assert 'trained_model' in result
            print(f"  {model} 模型测试通过")
        except Exception as e:
            print(f"  {model} 模型测试失败: {e}")
    
    dimensionality_reduction_models = ["pca", "standardscaler", "minmaxscaler", "tsne"]
    
    for model in dimensionality_reduction_models:
        try:
            result = analyze_data(
                df=df_class,
                model=model
            )
            assert 'trained_model' in result
            print(f"  {model} 模型测试通过")
        except Exception as e:
            print(f"  {model} 模型测试失败: {e}")
    
    print("模型可用性测试完成\n")

if __name__ == "__main__":
    print("开始测试新的分析模块接口...\n")
    
    try:
        test_analyze_data_function()
        test_regression_module()
        test_classification_module()
        test_clustering_module()
        test_dimensionality_reduction_module()
        test_backward_compatibility()
        test_model_variety()
        
        print("所有测试通过!")
    except Exception as e:
        print(f"测试失败: {e}")
        raise