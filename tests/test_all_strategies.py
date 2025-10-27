"""
测试所有改进后的策略类
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Src.DataAnalyzer.AnalysisUpgrade.Strategy.classification_strategy import ClassificationStrategy
from Src.DataAnalyzer.AnalysisUpgrade.Strategy.regression_strategy import RegressionStrategy
from Src.DataAnalyzer.AnalysisUpgrade.Strategy.clustering_strategy import ClusteringStrategy
from Src.DataAnalyzer.AnalysisUpgrade.Strategy.dimensionality_reduction_strategy import DimensionalityReductionStrategy
from Src.DataAnalyzer.AnalysisUpgrade.Strategy.anomaly_detection_strategy import AnomalyDetectionStrategy
from Src.DataAnalyzer.AnalysisUpgrade.Strategy.transformer_strategy import TransformerStrategy


def create_test_data():
    """创建测试数据"""
    np.random.seed(42)
    X = np.random.rand(100, 4)
    
    # 分类数据
    y_class = (X[:, 0] + X[:, 1] > 1).astype(int)
    
    # 回归数据
    y_reg = X[:, 0] + X[:, 1] + np.random.normal(0, 0.1, 100)
    
    # 异常检测数据（添加一些异常点）
    y_anomaly = np.ones(100)
    y_anomaly[90:95] = -1  # 标记一些异常点
    
    df = pd.DataFrame(X, columns=['feature1', 'feature2', 'feature3', 'feature4'])
    df['class_target'] = y_class
    df['reg_target'] = y_reg
    df['anomaly_target'] = y_anomaly
    
    return df


def test_classification_strategy(df):
    """测试分类策略"""
    print("=== 测试分类策略 ===")
    strategy = ClassificationStrategy()
    
    # 验证参数
    params = {
        "df": df,
        "feature_cols": ['feature1', 'feature2', 'feature3', 'feature4'],
        "target_col": 'class_target'
    }
    
    is_valid = strategy.validate_params(params)
    print(f"参数验证结果: {is_valid}")
    
    # 执行策略（使用简单模型）
    from sklearn.dummy import DummyClassifier
    model = DummyClassifier(strategy="most_frequent")
    
    result = strategy.execute(
        df=df,
        feature_cols=['feature1', 'feature2', 'feature3', 'feature4'],
        target_col='class_target',
        model=model,
        metrics_list=['accuracy', 'precision', 'recall', 'f1']
    )
    
    print(f"分类策略执行结果键: {list(result.keys())}")
    if 'metrics' in result:
        print(f"评估指标: {result['metrics']}")


def test_regression_strategy(df):
    """测试回归策略"""
    print("\n=== 测试回归策略 ===")
    strategy = RegressionStrategy()
    
    # 验证参数
    params = {
        "df": df,
        "feature_cols": ['feature1', 'feature2', 'feature3', 'feature4'],
        "target_col": 'reg_target'
    }
    
    is_valid = strategy.validate_params(params)
    print(f"参数验证结果: {is_valid}")
    
    # 执行策略
    model = LinearRegression()
    
    result = strategy.execute(
        df=df,
        feature_cols=['feature1', 'feature2', 'feature3', 'feature4'],
        target_col='reg_target',
        model=model,
        metrics_list=['mse', 'rmse', 'mae', 'r2']
    )
    
    print(f"回归策略执行结果键: {list(result.keys())}")
    if 'metrics' in result:
        print(f"评估指标: {result['metrics']}")


def test_clustering_strategy(df):
    """测试聚类策略"""
    print("\n=== 测试聚类策略 ===")
    strategy = ClusteringStrategy()
    
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
    
    print(f"聚类策略执行结果键: {list(result.keys())}")
    if 'metrics' in result:
        print(f"评估指标: {result['metrics']}")


def test_dimensionality_reduction_strategy(df):
    """测试降维策略"""
    print("\n=== 测试降维策略 ===")
    strategy = DimensionalityReductionStrategy()
    
    # 验证参数
    params = {
        "df": df,
        "feature_cols": ['feature1', 'feature2', 'feature3', 'feature4']
    }
    
    is_valid = strategy.validate_params(params)
    print(f"参数验证结果: {is_valid}")
    
    # 执行策略
    model = PCA(n_components=2)
    
    result = strategy.execute(
        df=df,
        feature_cols=['feature1', 'feature2', 'feature3', 'feature4'],
        model=model,
        metrics_list=['explained_variance_ratio']
    )
    
    print(f"降维策略执行结果键: {list(result.keys())}")
    if 'metrics' in result:
        print(f"评估指标: {result['metrics']}")


def test_anomaly_detection_strategy(df):
    """测试异常检测策略"""
    print("\n=== 测试异常检测策略 ===")
    strategy = AnomalyDetectionStrategy()
    
    # 验证参数
    params = {
        "df": df,
        "feature_cols": ['feature1', 'feature2', 'feature3', 'feature4']
    }
    
    is_valid = strategy.validate_params(params)
    print(f"参数验证结果: {is_valid}")
    
    # 执行策略
    model = IsolationForest(contamination=0.1, random_state=42)
    
    result = strategy.execute(
        df=df,
        feature_cols=['feature1', 'feature2', 'feature3', 'feature4'],
        model=model,
        true_labels=df['anomaly_target'].values,
        metrics_list=['precision', 'recall', 'f1']
    )
    
    print(f"异常检测策略执行结果键: {list(result.keys())}")
    if 'metrics' in result:
        print(f"评估指标: {result['metrics']}")


def test_transformer_strategy(df):
    """测试数据转换策略"""
    print("\n=== 测试数据转换策略 ===")
    strategy = TransformerStrategy()
    
    # 验证参数
    params = {
        "df": df,
        "feature_cols": ['feature1', 'feature2', 'feature3', 'feature4']
    }
    
    is_valid = strategy.validate_params(params)
    print(f"参数验证结果: {is_valid}")
    
    # 执行策略
    model = StandardScaler()
    
    result = strategy.execute(
        df=df,
        feature_cols=['feature1', 'feature2', 'feature3', 'feature4'],
        model=model
    )
    
    print(f"数据转换策略执行结果键: {list(result.keys())}")
    if 'transform_stats' in result:
        print(f"转换统计信息: {result['transform_stats']}")


if __name__ == "__main__":
    print("开始测试所有改进后的策略类...")
    
    try:
        df = create_test_data()
        test_classification_strategy(df)
        test_regression_strategy(df)
        test_clustering_strategy(df)
        test_dimensionality_reduction_strategy(df)
        test_anomaly_detection_strategy(df)
        test_transformer_strategy(df)
        
        print("\n=== 所有测试完成 ===")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()