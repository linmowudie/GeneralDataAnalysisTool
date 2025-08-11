# tests/test_mysql_import.py
"""
测试MySQL数据库导入功能，特别是book表
"""

import sys
import os

# 获取项目根目录（tests 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.data_analyzer.data_import import DataImport

def test_mysql_book_import():
    """
    测试从MySQL数据库导入book表
    """
    print("测试 MySQL 数据库 book 表导入:")
    
    try:
        # 使用 DataImport 类导入数据
        # 根据提供的数据库配置信息构造连接字符串
        # 格式: username:password@host:port/database
        connection_string = "root:LMWDhcmy1973113@localhost:3306/library_db_new"
        
        data_import = DataImport(
            file_resource="book",  # 表名
            resource_type="mysql",
            db_connection_string=connection_string,
            is_database=True
        )
        
        # 导入book表的数据
        df = data_import.import_data(query="SELECT * FROM book LIMIT 10")
        
        if df is not None:
            print("✅ MySQL book 表数据导入成功")
            print(f"数据形状: {df.shape}")
            print("前几行数据:")
            print(df)
        else:
            print("❌ MySQL book 表数据导入失败")
            
    except Exception as e:
        print(f"❌ MySQL book 表数据导入出错: {e}")
    finally:
        # 清理：关闭数据库连接
        if 'data_import' in locals():
            data_import.close_connection()

def test_mysql_book_count():
    """
    测试获取MySQL数据库book表的记录数
    """
    print("\n" + "="*50 + "\n")
    print("测试获取 MySQL 数据库 book 表记录数:")
    
    try:
        # 使用 DataImport 类导入数据
        connection_string = "root:LMWDhcmy1973113@localhost:3306/library_db_new"
        
        data_import = DataImport(
            file_resource="book",  # 表名
            resource_type="mysql",
            db_connection_string=connection_string,
            is_database=True
        )
        
        # 查询book表的记录数
        df = data_import.import_data(query="SELECT COUNT(*) as total FROM book")
        
        if df is not None:
            print("✅ MySQL book 表记录数查询成功")
            print(f"book表总记录数: {df.iloc[0, 0]}")
        else:
            print("❌ MySQL book 表记录数查询失败")
            
    except Exception as e:
        print(f"❌ MySQL book 表记录数查询出错: {e}")
    finally:
        # 清理：关闭数据库连接
        if 'data_import' in locals():
            data_import.close_connection()

def main():
    """
    主测试函数
    """
    print("开始测试 MySQL 数据库 book 表导入功能...\n")
    
    test_mysql_book_import()
    test_mysql_book_count()
    
    print("\nMySQL 数据库 book 表导入测试完成。")

if __name__ == "__main__":
    main()