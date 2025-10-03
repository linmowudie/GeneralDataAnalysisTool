# PythonScripts/generator.py
"""
用于生成和保存sklearn自带数据集到Data文件夹
"""

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris, load_wine, load_breast_cancer, load_diabetes, load_linnerud
from sklearn.datasets import fetch_california_housing
import os

def save_dataset_as_csv(data, target, feature_names, target_names, filename):
    """
    将数据集保存为CSV文件
    """
    # 创建特征数据框
    df = pd.DataFrame(data, columns=feature_names)
    
    # 添加目标变量
    df['target'] = target
    
    # 如果有目标名称，也添加进去
    if target_names is not None:
        if len(target_names) > 1 and len(target_names) == len(target):
            df['target_name'] = [target_names[i] for i in target]
        elif len(target_names) > 1:
            df['target_name'] = [target_names[int(i)] for i in target]
        else:
            df['target_name'] = target
    
    # 确保Data目录存在
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 保存为CSV
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"数据集已保存到: {filepath}")
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")

def generate_all_datasets():
    """
    生成所有sklearn自带数据集并保存为CSV文件
    """
    print("开始生成sklearn数据集...")
    
    # 1. Iris数据集 (已经存在)
    print("\n1. Iris数据集")
    try:
        iris = load_iris()
        save_dataset_as_csv(
            iris.data, 
            iris.target, 
            iris.feature_names, 
            iris.target_names, 
            'iris_sklearn.csv'
        )
    except Exception as e:
        print(f"生成Iris数据集时出错: {e}")
    
    # 2. Wine数据集
    print("\n2. Wine数据集")
    try:
        wine = load_wine()
        save_dataset_as_csv(
            wine.data, 
            wine.target, 
            wine.feature_names, 
            wine.target_names, 
            'wine.csv'
        )
    except Exception as e:
        print(f"生成Wine数据集时出错: {e}")
    
    # 3. Breast Cancer数据集
    print("\n3. Breast Cancer数据集")
    try:
        cancer = load_breast_cancer()
        save_dataset_as_csv(
            cancer.data, 
            cancer.target, 
            cancer.feature_names, 
            cancer.target_names, 
            'breast_cancer.csv'
        )
    except Exception as e:
        print(f"生成Breast Cancer数据集时出错: {e}")
    
    # 4. Diabetes数据集
    print("\n4. Diabetes数据集")
    try:
        diabetes = load_diabetes()
        save_dataset_as_csv(
            diabetes.data, 
            diabetes.target, 
            diabetes.feature_names, 
            None, 
            'diabetes.csv'
        )
    except Exception as e:
        print(f"生成Diabetes数据集时出错: {e}")
    
    # 5. California Housing数据集
    print("\n5. California Housing数据集")
    try:
        housing = fetch_california_housing()
        save_dataset_as_csv(
            housing.data, 
            housing.target, 
            housing.feature_names, 
            None, 
            'california_housing.csv'
        )
    except Exception as e:
        print(f"生成California Housing数据集时出错: {e}")
    
    # 6. Linnerud数据集 (多输出回归)
    print("\n6. Linnerud数据集")
    try:
        linnerud = load_linnerud()
        # 这是一个多输出数据集，需要特殊处理
        df = pd.DataFrame(linnerud.data, columns=linnerud.feature_names)
        # 添加目标变量（多个）
        for i, name in enumerate(linnerud.target_names):
            df[name] = linnerud.target[:, i]
        
        # 确保Data目录存在
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Data')
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, 'linnerud.csv')
        df.to_csv(filepath, index=False)
        print(f"Linnerud数据集已保存到: {filepath}")
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
    except Exception as e:
        print(f"生成Linnerud数据集时出错: {e}")
    
    print("\n所有数据集生成完成!")

if __name__ == "__main__":
    generate_all_datasets()