# scripts/import_to_mongodb.py
"""
将Data文件夹中的CSV数据导入到MongoDB中
"""

import pandas as pd
import numpy as np
from pymongo import MongoClient
import os
import json
import sys

# 添加项目根目录到sys.path，以便导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def csv_to_mongodb(csv_file, db_name, collection_name, client):
    """
    将CSV文件导入到MongoDB集合中
    """
    try:
        # 读取CSV文件
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Data', csv_file)
        df = pd.read_csv(file_path)
        
        # 处理NaN值，将其替换为None以便MongoDB处理
        df = df.where(pd.notnull(df), None)
        
        # 获取数据库
        db = client[db_name]
        
        # 获取集合
        collection = db[collection_name]
        
        # 清空现有数据
        collection.delete_many({})
        
        # 将DataFrame转换为字典列表
        records = df.to_dict('records')
        
        # 插入数据
        if records:
            collection.insert_many(records)
            print(f"成功导入 {len(records)} 条记录到 {db_name}.{collection_name}")
        else:
            print(f"没有数据需要导入到 {db_name}.{collection_name}")
            
        # 显示集合信息
        count = collection.count_documents({})
        print(f"集合 {collection_name} 中现有 {count} 条记录")
        
        # 显示第一条记录作为示例
        if count > 0:
            sample = collection.find_one()
            print(f"示例记录: {json.dumps(sample, default=str, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"导入 {csv_file} 到 {collection_name} 失败: {e}")
        return False

def import_all_datasets():
    """
    导入所有数据集到MongoDB
    """
    print("开始导入数据集到MongoDB...")
    
    # 连接MongoDB
    client = connect_to_mongodb()
    if not client:
        return
    
    # 定义要导入的数据集
    datasets = [
        ('iris_sklearn.csv', 'sklearn_datasets', 'iris'),
        ('wine.csv', 'sklearn_datasets', 'wine'),
        ('breast_cancer.csv', 'sklearn_datasets', 'breast_cancer'),
        ('diabetes.csv', 'sklearn_datasets', 'diabetes'),
        ('california_housing.csv', 'sklearn_datasets', 'california_housing'),
        ('linnerud.csv', 'sklearn_datasets', 'linnerud'),
        ('iris.csv', 'original_datasets', 'iris')
    ]
    
    # 导入每个数据集
    for csv_file, db_name, collection_name in datasets:
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Data', csv_file)
        if os.path.exists(file_path):
            print(f"\n正在导入 {csv_file}...")
            csv_to_mongodb(csv_file, db_name, collection_name, client)
        else:
            print(f"文件 {csv_file} 不存在，跳过")
    
    # 关闭连接
    client.close()
    print("\n所有数据集导入完成!")

def list_mongodb_collections():
    """
    列出MongoDB中的所有集合
    """
    print("\n列出MongoDB中的所有集合:")
    
    client = connect_to_mongodb()
    if not client:
        return
    
    try:
        # 列出所有数据库
        databases = client.list_database_names()
        print(f"数据库列表: {databases}")
        
        # 列出每个数据库中的集合
        for db_name in databases:
            if db_name not in ['admin', 'config', 'local']:  # 排除系统数据库
                db = client[db_name]
                collections = db.list_collection_names()
                print(f"数据库 {db_name} 中的集合: {collections}")
                
                # 显示每个集合的记录数
                for collection_name in collections:
                    collection = db[collection_name]
                    count = collection.count_documents({})
                    print(f"  - {collection_name}: {count} 条记录")
                    
    except Exception as e:
        print(f"列出集合时出错: {e}")
    finally:
        client.close()

def query_example_data():
    """
    查询示例数据以验证导入是否成功
    """
    print("\n查询示例数据:")
    
    client = connect_to_mongodb()
    if not client:
        return
    
    try:
        # 查询示例数据
        db = client['sklearn_datasets']
        
        # 从iris集合中查询一条记录
        iris_collection = db['iris']
        iris_record = iris_collection.find_one()
        if iris_record:
            print("Iris集合示例记录:")
            print(json.dumps(iris_record, default=str, indent=2))
        
        # 统计每个集合的记录数
        collections = ['iris', 'wine', 'breast_cancer', 'diabetes', 'california_housing', 'linnerud']
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"{collection_name} 集合记录数: {count}")
            
    except Exception as e:
        print(f"查询示例数据时出错: {e}")
    finally:
        client.close()

def main():
    """
    主函数
    """
    print("MongoDB数据导入工具")
    print("将Data文件夹中的CSV数据导入到MongoDB中")
    
    try:
        # 导入所有数据集
        import_all_datasets()
        
        # 列出所有集合
        list_mongodb_collections()
        
        # 查询示例数据
        query_example_data()
        
        print("\nMongoDB数据导入完成!")
        
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()