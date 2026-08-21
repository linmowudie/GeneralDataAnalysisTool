"""
测试改进后的策略类
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.Models.analysis.upgrade.Strategy.classification_strategy import ClassificationStrategy
from backend.Models.analysis.upgrade.Strategy.regression_strategy import RegressionStrategy
from backend.Models.analysis.upgrade.Strategy.clustering_strategy import ClusteringStrategy


def test_classification_strategy():
    """测试分类策略"""
    print("=== 测试分类策略 ===")
    strategy = ClassificationStrategy()
    
    # 创建测试数据
    np.random.seed(42)
    X = np.random.rand(100, 4)
    y = (X[:, 0] + X[:, 1] > 1).astype(int)
    df = pd.DataFrame(X)
    df['feature1'] = df[0]
    df['feature2'] = df[1]
    df['feature3'] = df[2]
    df['feature4'] = df[3]
    df.drop(columns=[0, 1, 2, 3], inplace=True)
    df['target'] = y
    
    # 验证参数
    params = {
        "df": df,
        "feature_cols": ['feature1', 'feature2', 'feature3', 'feature4'],
        "target_col": 'target'
    }
    
    is_valid = strategy.validate_params(params)
    print(f"参数验证结果: {is_valid}")
    
    # 执行策略（使用简单模型）
    from sklearn.dummy import DummyClassifier
    model = DummyClassifier(strategy="most_frequent")
    
    result = strategy.execute(
        df=df,
        feature_cols=['feature1', 'feature2', 'feature3', 'feature4'],
        target_col='target',
        model=model,
        metrics_list=['accuracy', 'precision', 'recall', 'f1']
    )
    
    print(f"分类策略执行结果: {list(result.keys())}")
    if 'metrics' in result:
        print(f"评估指标: {result['metrics']}")


def test_regression_strategy():
    """测试回归策略"""
    print("\n=== 测试回归策略 ===")
    strategy = RegressionStrategy()
    
    # 创建测试数据
    np.random.seed(42)
    X = np.random.rand(100, 4)
    y = X[:, 0] + X[:, 1] + np.random.normal(0, 0.1, 100)
    df = pd.DataFrame(X)
    df['feature1'] = df[0]
    df['feature2'] = df[1]
    df['feature3'] = df[2]
    df['feature4'] = df[3]
    df.drop(columns=[0, 1, 2, 3], inplace=True)
    df['target'] = y
    
    # 验证参数
    params = {
        "df": df,
        "feature_cols": ['feature1', 'feature2', 'feature3', 'feature4'],
        "target_col": 'target'
    }
    
    is_valid = strategy.validate_params(params)
    print(f"参数验证结果: {is_valid}")
    
    # 执行策略
    model = LinearRegression()
    
    result = strategy.execute(
        df=df,
        feature_cols=['feature1', 'feature2', 'feature3', 'feature4'],
        target_col='target',
        model=model,
        metrics_list=['mse', 'rmse', 'mae', 'r2']
    )
    
    print(f"回归策略执行结果: {list(result.keys())}")
    if 'metrics' in result:
        print(f"评估指标: {result['metrics']}")


def test_clustering_strategy():
    """测试聚类策略"""
    print("\n=== 测试聚类策略 ===")
    strategy = ClusteringStrategy()
    
    # 创建测试数据
    np.random.seed(42)
    X = np.random.rand(100, 4)
    df = pd.DataFrame(X)
    df['feature1'] = df[0]
    df['feature2'] = df[1]
    df['feature3'] = df[2]
    df['feature4'] = df[3]
    df.drop(columns=[0, 1, 2, 3], inplace=True)
    
    # 验证参数
    params = {
        "df": df,
        "feature_cols": ['feature1', 'feature2', 'feature3', 'feature4']
    }
    
    is_valid = strategy.validate_params(params)
    print(f"参数验证结果: {is_valid}")
    
    # 执行策略
    model = KMeans(n_clusters=3, random_state=42)
    
    result = strategy.execute(
        df=df,
        feature_cols=['feature1', 'feature2', 'feature3', 'feature4'],
        model=model,
        metrics_list=['silhouette', 'calinski_harabasz', 'davies_bouldin']
    )
    
    print(f"聚类策略执行结果: {list(result.keys())}")
    if 'metrics' in result:
        print(f"评估指标: {result['metrics']}")


if __name__ == "__main__":
    print("开始测试改进后的策略类...")
    
    try:
        test_classification_strategy()
        test_regression_strategy()
        test_clustering_strategy()
        
        print("\n=== 测试完成 ===")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()