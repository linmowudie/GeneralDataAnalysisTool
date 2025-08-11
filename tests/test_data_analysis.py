# tests/test_data_analysis.py

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
from Src.data_analyzer.data_analysis import DataAnalyzer

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

def test_logistic_regression_analysis():
    """测试逻辑回归分析"""
    print("测试逻辑回归分析:")
    df = create_test_dataframe()
    print(f"数据形状: {df.shape}")
    print(f"目标列分布:\n{df['target'].value_counts()}")
    
    # 使用逻辑回归进行分析
    analyzer = DataAnalyzer(
        df=df,
        model="logisticregression",
        target_col="target",
        feature_cols=["feature1", "feature2", "feature3"],
        is_return_model_score=True,
        metrics_list=["accuracy"]
    )
    
    result = analyzer.analyze()
    
    print(f"模型得分: {result.get('scores', {})}")
    print(f"任务类型: {result.get('task_type', 'Unknown')}")
    print("✅ 逻辑回归分析测试完成\n")

def test_linear_regression_analysis():
    """测试线性回归分析"""
    print("测试线性回归分析:")
    df = create_regression_test_dataframe()
    print(f"数据形状: {df.shape}")
    print(f"目标列统计信息:\n{df['target'].describe()}")
    
    # 使用线性回归进行分析
    analyzer = DataAnalyzer(
        df=df,
        model="linearregression",
        target_col="target",
        feature_cols=["feature1", "feature2", "feature3"],
        is_return_model_score=True,
        metrics_list=["mse", "r2"]
    )
    
    result = analyzer.analyze()
    
    print(f"模型得分: {result.get('scores', {})}")
    print(f"任务类型: {result.get('task_type', 'Unknown')}")
    print("✅ 线性回归分析测试完成\n")

def test_decision_tree_analysis():
    """测试决策树分析"""
    print("测试决策树分析:")
    df = create_test_dataframe()
    print(f"数据形状: {df.shape}")
    
    # 使用决策树进行分析
    analyzer = DataAnalyzer(
        df=df,
        model="decisiontreeclassifier",
        target_col="target",
        feature_cols=["feature1", "feature2", "feature3"],
        is_return_model_score=True,
        metrics_list=["accuracy"]
    )
    
    result = analyzer.analyze()
    
    print(f"模型得分: {result.get('scores', {})}")
    print(f"任务类型: {result.get('task_type', 'Unknown')}")
    print("✅ 决策树分析测试完成\n")

def test_kmeans_analysis():
    """测试KMeans聚类分析"""
    print("测试KMeans聚类分析:")
    df = create_test_dataframe()[["feature1", "feature2", "feature3"]]
    print(f"数据形状: {df.shape}")
    
    # 使用KMeans进行分析
    analyzer = DataAnalyzer(
        df=df,
        model="kmeans",
        is_return_model_score=True
    )
    
    result = analyzer.analyze()
    
    print(f"任务类型: {result.get('task_type', 'Unknown')}")
    print("✅ KMeans聚类分析测试完成\n")

def test_invalid_model():
    """测试无效模型"""
    print("测试无效模型:")
    df = create_test_dataframe()
    
    try:
        analyzer = DataAnalyzer(
            df=df,
            model="invalid_model",
            target_col="target"
        )
        result = analyzer.analyze()
        print("❌ 无效模型测试失败 - 应该抛出异常")
    except Exception as e:
        print(f"✅ 无效模型测试通过 - 正确捕获异常: {str(e)}\n")

# 测试代码
if __name__ == "__main__":
    print("开始测试 data_analysis 模块\n")
    print("="*50 + "\n")
    
    # 运行各种测试
    test_logistic_regression_analysis()
    test_linear_regression_analysis()
    test_decision_tree_analysis()
    test_kmeans_analysis()
    test_invalid_model()
    
    print("="*50)
    print("所有测试完成!")