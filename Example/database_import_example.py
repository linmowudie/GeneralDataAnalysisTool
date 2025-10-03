"""
examples/database_import_example.py
数据库导入功能示例

该脚本演示如何使用扩展的数据库导入功能。
"""

import pandas as pd
from Src.DataAnalyzer.core import DataProcessingEngine

def mongodb_import_example():
    """MongoDB导入示例"""
    print("MongoDB导入示例")
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    try:
        # 从MongoDB导入数据
        # 注意：需要先确保MongoDB服务正在运行，并且有相应的数据
        engine.import_data(
            resource_path="iris",  # 集合名称
            resource_type="mongodb",
            db_connection_string="mongodb://localhost:27017/sklearn_datasets",
            is_database=True
        )
        
        if engine.imported_data is not None:
            print(f"成功从MongoDB导入数据，共 {len(engine.imported_data)} 行")
            print("前5行数据：")
            print(engine.imported_data.head())
        else:
            print("从MongoDB导入数据失败")
            
    except Exception as e:
        print(f"MongoDB导入过程中出现错误: {e}")

def redis_import_example():
    """Redis导入示例"""
    print("\nRedis导入示例")
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    try:
        # 从Redis导入数据
        # 注意：需要先确保Redis服务正在运行，并且有相应的数据
        engine.import_data(
            resource_path="sample_data",  # 键名
            resource_type="redis",
            db_connection_string="redis://localhost:6379/0",
            is_database=True
        )
        
        if engine.imported_data is not None:
            print(f"成功从Redis导入数据，共 {len(engine.imported_data)} 行")
            print("数据内容：")
            print(engine.imported_data)
        else:
            print("从Redis导入数据失败")
            
    except Exception as e:
        print(f"Redis导入过程中出现错误: {e}")

def traditional_db_import_example():
    """传统数据库导入示例"""
    print("\n传统数据库导入示例")
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    try:
        # 从SQLite导入数据（示例）
        engine.import_data(
            resource_path="SELECT * FROM iris LIMIT 10",  # SQL查询
            resource_type="sqlite",
            db_connection_string="Data/iris_test.db",
            is_database=True
        )
        
        if engine.imported_data is not None:
            print(f"成功从SQLite导入数据，共 {len(engine.imported_data)} 行")
            print("前5行数据：")
            print(engine.imported_data.head())
        else:
            print("从SQLite导入数据失败")
            
    except Exception as e:
        print(f"SQLite导入过程中出现错误: {e}")

if __name__ == "__main__":
    print("=== 数据库导入功能演示 ===")
    
    # 运行示例
    mongodb_import_example()
    redis_import_example()
    traditional_db_import_example()
    
    print("\n=== 演示完成 ===")