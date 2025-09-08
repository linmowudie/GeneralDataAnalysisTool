# tests/test_mongodb_analysis.py

import sys
import os
import pandas as pd
import numpy as np
from pymongo import MongoClient

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==================================================

# 导入需要的模块
from Src.data_analyzer.analysis.analyzer import analyze_data

def connect_to_mongodb():
    """
    连接到MongoDB数据库
    """
    try:
        # 连接到本地MongoDB实例（无密码）
        client = MongoClient('localhost', 27017)
        # 测试连接
        client.admin.command('ping')
        print("成功连接到MongoDB")
        return client
    except Exception as e:
        print(f"连接MongoDB失败: {e}")
        return None

def mongodb_to_dataframe(db_name, collection_name, query=None):
    """
    从MongoDB读取数据并转换为DataFrame
    """
    client = connect_to_mongodb()
    if not client:
        return None
    
    try:
        db = client[db_name]
        collection = db[collection_name]
        
        # 如果提供了查询条件，则使用它
        if query:
            cursor = collection.find(query)
        else:
            cursor = collection.find()
        
        # 转换为DataFrame
        df = pd.DataFrame(list(cursor))
        
        # 删除MongoDB的_id列
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        print(f"从 {db_name}.{collection_name} 成功读取 {len(df)} 条记录")
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"从 {db_name}.{collection_name} 读取数据失败: {e}")
        return None
    finally:
        client.close()

def test_iris_analysis_from_mongodb():
    """
    测试从MongoDB读取Iris数据并进行分析
    """
    print("=" * 60)
    print("测试从MongoDB读取Iris数据并进行分析")
    print("=" * 60)
    
    # 从MongoDB读取数据
    df = mongodb_to_dataframe('sklearn_datasets', 'iris')
    if df is None:
        print("无法从MongoDB读取Iris数据")
        return
    
    # 进行分类分析
    print("\n进行分类分析...")
    try:
        result = analyze_data(
            df=df,
            model="logisticregression",
            target_col="target",
            is_return_model_score=True,
            is_return_model_param=True
        )
        
        print(f"模型类型: {result['task_type']}")
        print(f"准确率: {result['scores']['accuracy']:.4f}")
        print(f"模型参数数量: {len(result['model_params'])}")
        print("分类分析测试通过")
        
    except Exception as e:
        print(f"分类分析失败: {e}")

def test_wine_analysis_from_mongodb():
    """
    测试从MongoDB读取Wine数据并进行分析
    """
    print("\n" + "=" * 60)
    print("测试从MongoDB读取Wine数据并进行分析")
    print("=" * 60)
    
    # 从MongoDB读取数据
    df = mongodb_to_dataframe('sklearn_datasets', 'wine')
    if df is None:
        print("无法从MongoDB读取Wine数据")
        return
    
    # 进行分类分析
    print("\n进行分类分析...")
    try:
        result = analyze_data(
            df=df,
            model="decisiontreeclassifier",
            target_col="target",
            is_return_model_score=True
        )
        
        print(f"模型类型: {result['task_type']}")
        print(f"准确率: {result['scores']['accuracy']:.4f}")
        print("分类分析测试通过")
        
    except Exception as e:
        print(f"分类分析失败: {e}")

def test_diabetes_analysis_from_mongodb():
    """
    测试从MongoDB读取Diabetes数据并进行分析
    """
    print("\n" + "=" * 60)
    print("测试从MongoDB读取Diabetes数据并进行分析")
    print("=" * 60)
    
    # 从MongoDB读取数据
    df = mongodb_to_dataframe('sklearn_datasets', 'diabetes')
    if df is None:
        print("无法从MongoDB读取Diabetes数据")
        return
    
    # 进行回归分析
    print("\n进行回归分析...")
    try:
        result = analyze_data(
            df=df,
            model="linearregression",
            target_col="target",
            is_return_model_score=True
        )
        
        print(f"模型类型: {result['task_type']}")
        print(f"R² 分数: {result['scores']['r2']:.4f}")
        print(f"均方误差: {result['scores']['mse']:.4f}")
        print("回归分析测试通过")
        
    except Exception as e:
        print(f"回归分析失败: {e}")

def test_california_housing_analysis_from_mongodb():
    """
    测试从MongoDB读取California Housing数据并进行分析
    """
    print("\n" + "=" * 60)
    print("测试从MongoDB读取California Housing数据并进行分析")
    print("=" * 60)
    
    # 从MongoDB读取数据（只取一部分以加快测试速度）
    df = mongodb_to_dataframe('sklearn_datasets', 'california_housing')
    if df is None:
        print("无法从MongoDB读取California Housing数据")
        return
    
    # 采样以加快测试速度
    df_sample = df.sample(n=1000, random_state=42)
    
    # 进行回归分析
    print("\n进行回归分析...")
    try:
        result = analyze_data(
            df=df_sample,
            model="ridge",
            target_col="target",
            is_return_model_score=True
        )
        
        print(f"模型类型: {result['task_type']}")
        print(f"R² 分数: {result['scores']['r2']:.4f}")
        print(f"均方误差: {result['scores']['mse']:.4f}")
        print("回归分析测试通过")
        
    except Exception as e:
        print(f"回归分析失败: {e}")

def test_linnerud_analysis_from_mongodb():
    """
    测试从MongoDB读取Linnerud数据并进行分析
    """
    print("\n" + "=" * 60)
    print("测试从MongoDB读取Linnerud数据并进行分析")
    print("=" * 60)
    
    # 从MongoDB读取数据
    df = mongodb_to_dataframe('sklearn_datasets', 'linnerud')
    if df is None:
        print("无法从MongoDB读取Linnerud数据")
        return
    
    # 进行降维分析
    print("\n进行降维分析...")
    try:
        result = analyze_data(
            df=df,
            model="pca",
            is_return_model_param=True,
            is_return_training_set=True
        )
        
        print(f"模型类型: {result['task_type']}")
        print(f"原始维度: {df.shape}")
        print(f"降维后维度: {result['X_train'].shape}")
        print("降维分析测试通过")
        
    except Exception as e:
        print(f"降维分析失败: {e}")

def main():
    """
    主函数
    """
    print("测试从MongoDB读取数据并使用分析模块进行分析")
    
    try:
        test_iris_analysis_from_mongodb()
        test_wine_analysis_from_mongodb()
        test_diabetes_analysis_from_mongodb()
        test_california_housing_analysis_from_mongodb()
        test_linnerud_analysis_from_mongodb()
        
        print("\n" + "=" * 60)
        print("所有MongoDB数据分析测试完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()