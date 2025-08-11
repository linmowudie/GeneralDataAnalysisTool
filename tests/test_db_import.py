# tests/test_db_import.py
"""
测试数据库导入功能
"""

import sys
import os
import sqlite3
import pandas as pd
from pathlib import Path

# 获取项目根目录（tests 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.data_analyzer.data_import import DataImport

def create_test_sqlite_db():
    """
    创建一个测试用的 SQLite 数据库，并插入 iris 数据
    """
    # 从 CSV 文件读取数据
    csv_path = os.path.join(PROJECT_ROOT, "Data", "iris.csv")
    df = pd.read_csv(csv_path)
    
    # 创建 SQLite 数据库
    db_path = os.path.join(PROJECT_ROOT, "Data", "iris_test.db")
    conn = sqlite3.connect(db_path)
    
    # 将数据写入数据库
    df.to_sql("iris", conn, if_exists="replace", index=False)
    
    # 验证数据是否正确写入
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM iris")
    count = cursor.fetchone()[0]
    print(f"✅ 成功创建 SQLite 数据库，共写入 {count} 条记录")
    
    conn.close()
    return db_path

def test_sqlite_import():
    """
    测试 SQLite 数据库导入功能
    """
    print("测试 SQLite 数据库导入:")
    
    # 创建测试数据库
    db_path = create_test_sqlite_db()
    
    try:
        # 使用 DataImport 类导入数据
        data_import = DataImport(
            file_resource="iris",  # 表名
            resource_type="sqlite",
            db_connection_string=db_path,  # SQLite 数据库路径
            is_database=True
        )
        
        # 导入数据，使用 query 参数执行 SQL 查询
        df = data_import.import_data(query="SELECT * FROM iris LIMIT 5")
        
        if df is not None:
            print("✅ SQLite 数据导入成功")
            print(df)
        else:
            print("❌ SQLite 数据导入失败")
            
    except Exception as e:
        print(f"❌ SQLite 数据导入出错: {e}")
    finally:
        # 清理：关闭数据库连接
        if 'data_import' in locals():
            data_import.close_connection()

def test_sqlite_import_with_context_manager():
    """
    测试使用上下文管理器的 SQLite 数据库导入功能
    """
    print("\n" + "="*50 + "\n")
    print("测试使用上下文管理器的 SQLite 数据库导入:")
    
    # 创建测试数据库
    db_path = create_test_sqlite_db()
    
    try:
        # 使用上下文管理器方式导入数据
        with DataImport(
            file_resource="iris",
            resource_type="sqlite",
            db_connection_string=db_path,
            is_database=True
        ) as data_import:
            # 导入数据
            df = data_import.import_data(query="SELECT * FROM iris WHERE target = 1 LIMIT 3")
            
            if df is not None:
                print("✅ 使用上下文管理器的 SQLite 数据导入成功")
                print(df)
            else:
                print("❌ 使用上下文管理器的 SQLite 数据导入失败")
                
    except Exception as e:
        print(f"❌ 使用上下文管理器的 SQLite 数据导入出错: {e}")

def test_direct_table_import():
    """
    测试直接表名导入功能
    """
    print("\n" + "="*50 + "\n")
    print("测试直接表名导入:")
    
    # 创建测试数据库
    db_path = create_test_sqlite_db()
    
    try:
        # 使用 DataImport 类导入数据
        data_import = DataImport(
            file_resource="iris",  # 表名
            resource_type="sqlite",
            db_connection_string=db_path,  # SQLite 数据库路径
            is_database=True
        )
        
        # 直接使用表名导入数据
        df = data_import.import_data(query="iris")  # 表名作为查询参数
        
        if df is not None:
            print("✅ 直接表名导入成功")
            print(f"导入数据形状: {df.shape}")
            print(df.head())
        else:
            print("❌ 直接表名导入失败")
            
    except Exception as e:
        print(f"❌ 直接表名导入出错: {e}")
    finally:
        # 清理：关闭数据库连接
        if 'data_import' in locals():
            data_import.close_connection()

def main():
    """
    主测试函数
    """
    print("开始测试数据库导入功能...\n")
    
    test_sqlite_import()
    test_sqlite_import_with_context_manager()
    test_direct_table_import()
    
    print("\n数据库导入测试完成。")

if __name__ == "__main__":
    main()