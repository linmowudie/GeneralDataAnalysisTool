# examples/mongodb_data_analysis_example.py

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
        print("✓ 成功连接到MongoDB")
        return client
    except Exception as e:
        print(f"✗ 连接MongoDB失败: {e}")
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
        
        print(f"✓ 从 {db_name}.{collection_name} 成功读取 {len(df)} 条记录")
        return df
        
    except Exception as e:
        print(f"✗ 从 {db_name}.{collection_name} 读取数据失败: {e}")
        return None
    finally:
        client.close()

def analyze_dataset_from_mongodb(name, db_name, collection_name, task_type, target_col=None, query=None):
    """
    从MongoDB读取数据集并进行分析
    """
    print(f"\n{'='*60}")
    print(f"分析 {name} 数据集")
    print(f"{'='*60}")
    
    # 从MongoDB读取数据
    df = mongodb_to_dataframe(db_name, collection_name, query)
    if df is None:
        print(f"✗ 无法从MongoDB读取 {name} 数据")
        return None
    
    print(f"数据形状: {df.shape}")
    
    # 显示数据基本信息
    print(f"\n数据基本信息:")
    print(f"  - 行数: {df.shape[0]}")
    print(f"  - 列数: {df.shape[1]}")
    
    if target_col:
        print(f"  - 目标列: {target_col}")
        if target_col in df.columns:
            if df[target_col].dtype in ['int64', 'float64']:
                print(f"  - 目标列统计:\n{df[target_col].describe()}")
            else:
                print(f"  - 目标列分布:\n{df[target_col].value_counts()}")
    
    # 根据任务类型选择合适的模型
    models = []
    if task_type == 'classification':
        models = ["logisticregression", "decisiontreeclassifier"]
    elif task_type == 'regression':
        models = ["linearregression", "ridge"]
    elif task_type == 'transformer':
        models = ["pca", "standardscaler"]
    
    results = {}
    for model in models:
        print(f"\n测试 {model} 模型:")
        try:
            if task_type == 'transformer':
                result = analyze_data(
                    df=df,
                    model=model,
                    is_return_model_score=False,
                    is_return_training_set=True
                )
                print(f"  - 原始维度: {df.shape}")
                print(f"  - 处理后维度: {result['X_train'].shape}")
            else:
                result = analyze_data(
                    df=df,
                    model=model,
                    target_col=target_col,
                    is_return_model_score=True
                )
                
                if task_type == 'classification':
                    accuracy = result['scores']['accuracy']
                    results[model] = accuracy
                    print(f"  - 准确率: {accuracy:.4f}")
                elif task_type == 'regression':
                    r2 = result['scores']['r2']
                    mse = result['scores']['mse']
                    results[model] = {'r2': r2, 'mse': mse}
                    print(f"  - R² 分数: {r2:.4f}")
                    print(f"  - 均方误差: {mse:.4f}")
            
            print(f"  - 模型类型: {result['task_type']}")
            print(f"  - 状态: 测试通过 ✓")
            
        except Exception as e:
            print(f"  - 状态: 测试失败 ✗ ({e})")
            results[model] = None
    
    return results

def main():
    """
    主函数 - 展示完整的MongoDB数据分析工作流程
    """
    print("MongoDB数据分析示例")
    print("展示如何从MongoDB读取数据并使用分析模块进行分析")
    print("\n注意: 请确保MongoDB服务正在运行")
    
    # 存储所有结果
    all_results = {}
    
    try:
        # 1. 分析Iris数据集
        all_results['Iris'] = analyze_dataset_from_mongodb(
            name='Iris',
            db_name='sklearn_datasets',
            collection_name='iris',
            task_type='classification',
            target_col='target'
        )
        
        # 2. 分析Wine数据集
        all_results['Wine'] = analyze_dataset_from_mongodb(
            name='Wine',
            db_name='sklearn_datasets',
            collection_name='wine',
            task_type='classification',
            target_col='target'
        )
        
        # 3. 分析Diabetes数据集
        all_results['Diabetes'] = analyze_dataset_from_mongodb(
            name='Diabetes',
            db_name='sklearn_datasets',
            collection_name='diabetes',
            task_type='regression',
            target_col='target'
        )
        
        # 4. 分析California Housing数据集 (采样以提高速度)
        print(f"\n{'='*60}")
        print(f"分析 California Housing 数据集 (采样版)")
        print(f"{'='*60}")
        
        df_housing = mongodb_to_dataframe('sklearn_datasets', 'california_housing')
        if df_housing is not None:
            # 采样以提高分析速度
            df_housing_sample = df_housing.sample(n=2000, random_state=42)
            print(f"数据形状: {df_housing_sample.shape}")
            
            models = ["linearregression", "ridge"]
            housing_results = {}
            for model in models:
                print(f"\n测试 {model} 模型:")
                try:
                    result = analyze_data(
                        df=df_housing_sample,
                        model=model,
                        target_col='target',
                        is_return_model_score=True
                    )
                    
                    r2 = result['scores']['r2']
                    mse = result['scores']['mse']
                    housing_results[model] = {'r2': r2, 'mse': mse}
                    print(f"  - R² 分数: {r2:.4f}")
                    print(f"  - 均方误差: {mse:.4f}")
                    print(f"  - 模型类型: {result['task_type']}")
                    print(f"  - 状态: 测试通过 ✓")
                    
                except Exception as e:
                    print(f"  - 状态: 测试失败 ✗ ({e})")
                    housing_results[model] = None
            
            all_results['California Housing'] = housing_results
        
        # 5. 分析Linnerud数据集
        all_results['Linnerud'] = analyze_dataset_from_mongodb(
            name='Linnerud',
            db_name='sklearn_datasets',
            collection_name='linnerud',
            task_type='transformer'
        )
        
        # 生成总结报告
        print(f"\n{'='*60}")
        print("综合分析总结")
        print(f"{'='*60}")
        
        for dataset_name, results in all_results.items():
            if results:  # 如果有结果
                print(f"\n{dataset_name} 数据集:")
                valid_results = {k: v for k, v in results.items() if v is not None}
                if valid_results:
                    if dataset_name in ['Iris', 'Wine']:  # 分类结果
                        best_model = max(valid_results, key=valid_results.get)
                        best_accuracy = valid_results[best_model]
                        print(f"  - 最佳模型: {best_model} (准确率: {best_accuracy:.4f})")
                    elif dataset_name in ['Diabetes', 'California Housing']:  # 回归结果
                        best_model = max(valid_results, key=lambda x: valid_results[x]['r2'])
                        best_r2 = valid_results[best_model]['r2']
                        print(f"  - 最佳模型: {best_model} (R²: {best_r2:.4f})")
                    elif dataset_name == 'Linnerud':  # 降维结果
                        print(f"  - 成功应用了降维技术")
        
        print(f"\n{'='*60}")
        print("所有数据分析完成!")
        print("您现在可以使用MongoDB中的数据进行各种分析任务了!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"✗ 分析过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()