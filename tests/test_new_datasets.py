# tests/test_new_datasets.py

import sys
import os
import pandas as pd
import numpy as np

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==================================================

# 导入需要的模块
from Src.data_analyzer.analysis.analyzer import analyze_data

def test_wine_dataset():
    """测试Wine数据集"""
    print("=" * 50)
    print("测试 Wine 数据集")
    print("=" * 50)
    
    # 加载数据
    file_path = os.path.join(PROJECT_ROOT, 'Data', 'wine.csv')
    df = pd.read_csv(file_path)
    
    print(f"数据集形状: {df.shape}")
    print(f"目标值分布:\n{df['target'].value_counts()}")
    
    # 测试分类模型
    models = ["logisticregression", "decisiontreeclassifier"]
    
    for model in models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df,
                model=model,
                target_col="target",
                is_return_model_score=True,
                is_return_model_param=True
            )
            
            print(f"  准确率: {result['scores']['accuracy']:.4f}")
            print(f"  模型类型: {result['task_type']}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def test_breast_cancer_dataset():
    """测试Breast Cancer数据集"""
    print("\n" + "=" * 50)
    print("测试 Breast Cancer 数据集")
    print("=" * 50)
    
    # 加载数据
    file_path = os.path.join(PROJECT_ROOT, 'Data', 'breast_cancer.csv')
    df = pd.read_csv(file_path)
    
    print(f"数据集形状: {df.shape}")
    print(f"目标值分布:\n{df['target'].value_counts()}")
    
    # 测试分类模型
    models = ["logisticregression", "kneighborsclassifier"]
    
    for model in models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df,
                model=model,
                target_col="target",
                is_return_model_score=True
            )
            
            print(f"  准确率: {result['scores']['accuracy']:.4f}")
            print(f"  模型类型: {result['task_type']}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def test_diabetes_dataset():
    """测试Diabetes数据集"""
    print("\n" + "=" * 50)
    print("测试 Diabetes 数据集")
    print("=" * 50)
    
    # 加载数据
    file_path = os.path.join(PROJECT_ROOT, 'Data', 'diabetes.csv')
    df = pd.read_csv(file_path)
    
    print(f"数据集形状: {df.shape}")
    print(f"目标变量统计:\n{df['target'].describe()}")
    
    # 测试回归模型
    models = ["linearregression", "ridge"]
    
    for model in models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df,
                model=model,
                target_col="target",
                is_return_model_score=True
            )
            
            print(f"  R² 分数: {result['scores']['r2']:.4f}")
            print(f"  均方误差: {result['scores']['mse']:.4f}")
            print(f"  模型类型: {result['task_type']}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def test_california_housing_dataset():
    """测试California Housing数据集"""
    print("\n" + "=" * 50)
    print("测试 California Housing 数据集")
    print("=" * 50)
    
    # 加载数据
    file_path = os.path.join(PROJECT_ROOT, 'Data', 'california_housing.csv')
    df = pd.read_csv(file_path)
    
    print(f"数据集形状: {df.shape}")
    print(f"目标变量统计:\n{df['target'].describe()}")
    
    # 为了加快测试速度，只使用部分数据
    df_sample = df.sample(n=1000, random_state=42)
    
    # 测试回归模型
    models = ["linearregression", "ridge"]
    
    for model in models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df_sample,
                model=model,
                target_col="target",
                is_return_model_score=True
            )
            
            print(f"  R² 分数: {result['scores']['r2']:.4f}")
            print(f"  均方误差: {result['scores']['mse']:.4f}")
            print(f"  模型类型: {result['task_type']}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def test_linnerud_dataset():
    """测试Linnerud数据集"""
    print("\n" + "=" * 50)
    print("测试 Linnerud 数据集")
    print("=" * 50)
    
    # 加载数据
    file_path = os.path.join(PROJECT_ROOT, 'Data', 'linnerud.csv')
    df = pd.read_csv(file_path)
    
    print(f"数据集形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    
    # 测试降维模型
    models = ["pca", "standardscaler"]
    
    for model in models:
        print(f"\n测试 {model} 模型:")
        try:
            result = analyze_data(
                df=df,
                model=model,
                is_return_model_param=True,
                is_return_training_set=True
            )
            
            print(f"  原始维度: {df.shape}")
            print(f"  处理后维度: {result['X_train'].shape}")
            print(f"  模型类型: {result['task_type']}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")

def main():
    """主函数"""
    print("测试新生成的数据集与分析模块的兼容性")
    
    try:
        test_wine_dataset()
        test_breast_cancer_dataset()
        test_diabetes_dataset()
        test_california_housing_dataset()
        test_linnerud_dataset()
        
        print("\n" + "=" * 50)
        print("所有数据集测试完成!")
        print("=" * 50)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()