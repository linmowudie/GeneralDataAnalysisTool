# tests/test_iris_dataset.py

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

def load_iris_data():
    """加载iris数据集"""
    file_path = os.path.join(PROJECT_ROOT, 'Data', 'iris.csv')
    df = pd.read_csv(file_path)
    print(f"数据集形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    print(f"目标值分布:\n{df['target'].value_counts()}")
    print(f"目标名称分布:\n{df['target_name'].value_counts()}")
    return df

def test_classification_models():
    """测试分类模型在iris数据集上的表现"""
    print("=== 测试分类模型 ===")
    df = load_iris_data()
    
    # 移除target_name列，只保留数值型目标变量
    df_numeric = df.drop('target_name', axis=1)
    
    classification_models = [
        "logisticregression",
        "decisiontreeclassifier", 
        "kneighborsclassifier",
        "svc"
    ]
    
    for model in classification_models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df_numeric,
                model=model,
                target_col="target",
                is_return_model_score=True,
                is_return_model_param=True,
                is_return_model_predicting_set=True
            )
            
            print(f"  模型类型: {result['task_type']}")
            print(f"  评估指标: {result['scores']}")
            print(f"  预测结果数量: {len(result['predictions'])}")
            print(f"  模型参数数量: {len(result['model_params'])}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def test_clustering_models():
    """测试聚类模型在iris数据集上的表现"""
    print("\n=== 测试聚类模型 ===")
    df = load_iris_data()
    
    # 移除目标列，仅使用特征进行聚类
    df_features = df.drop(['target', 'target_name'], axis=1)
    
    clustering_models = [
        "kmeans",
        "meanshift"
    ]
    
    for model in clustering_models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df_features,
                model=model,
                is_return_model_score=True,
                is_return_model_param=True
            )
            
            print(f"  模型类型: {result['task_type']}")
            print(f"  评估指标: {result['scores']}")
            print(f"  模型参数数量: {len(result['model_params'])}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def test_dimensionality_reduction_models():
    """测试降维模型在iris数据集上的表现"""
    print("\n=== 测试降维模型 ===")
    df = load_iris_data()
    
    # 移除目标列，仅使用特征进行降维
    df_features = df.drop(['target', 'target_name'], axis=1)
    
    dim_reduction_models = [
        "pca",
        "standardscaler",
        "minmaxscaler"
    ]
    
    for model in dim_reduction_models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df_features,
                model=model,
                is_return_model_param=True,
                is_return_training_set=True
            )
            
            print(f"  模型类型: {result['task_type']}")
            if 'X_train' in result:
                print(f"  原始特征维度: {df_features.shape}")
                print(f"  降维后特征维度: {result['X_train'].shape}")
            print(f"  模型参数数量: {len(result['model_params'])}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def test_regression_models():
    """测试回归模型在iris数据集上的表现（将分类任务转换为回归）"""
    print("\n=== 测试回归模型 ===")
    df = load_iris_data()
    
    # 使用一个特征列作为目标，其他特征列作为输入
    df_regression = df.drop('target_name', axis=1)
    
    regression_models = [
        "linearregression",
        "ridge",
        "lasso"
    ]
    
    # 使用sepal length作为目标，其他特征作为输入
    feature_cols = ['sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    
    for model in regression_models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df_regression,
                model=model,
                target_col="sepal length (cm)",
                feature_cols=feature_cols,
                is_return_model_score=True,
                is_return_model_param=True
            )
            
            print(f"  模型类型: {result['task_type']}")
            print(f"  评估指标: {result['scores']}")
            print(f"  模型参数数量: {len(result['model_params'])}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def test_model_comparison():
    """比较不同模型在iris数据集上的表现"""
    print("\n=== 模型性能比较 ===")
    df = load_iris_data()
    df_numeric = df.drop('target_name', axis=1)
    
    models = [
        "logisticregression",
        "decisiontreeclassifier", 
        "kneighborsclassifier"
    ]
    
    results = {}
    
    for model in models:
        try:
            result = analyze_data(
                df=df_numeric,
                model=model,
                target_col="target",
                is_return_model_score=True
            )
            accuracy = result['scores'].get('accuracy', 'N/A')
            results[model] = accuracy
            print(f"{model}: accuracy = {accuracy}")
        except Exception as e:
            print(f"{model}: 测试失败 - {e}")
            results[model] = None
    
    # 找出最佳模型
    valid_results = {k: v for k, v in results.items() if v is not None}
    if valid_results:
        best_model = max(valid_results, key=valid_results.get)
        print(f"\n最佳模型: {best_model} (准确率: {valid_results[best_model]})")

if __name__ == "__main__":
    print("开始使用Iris数据集测试模型...\n")
    
    try:
        test_classification_models()
        test_clustering_models()
        test_dimensionality_reduction_models()
        test_regression_models()
        test_model_comparison()
        
        print("\n所有测试完成!")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        raise