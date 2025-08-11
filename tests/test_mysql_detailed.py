# tests/test_mysql_detailed.py
"""
详细测试MySQL数据库导入功能
"""

import sys
import os

# 获取项目根目录（tests 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.data_analyzer.data_import import DataImport

def get_table_info():
    """
    获取book表的详细信息
    """
    print("获取 book 表结构信息:")
    
    try:
        connection_string = "root:LMWDhcmy1973113@localhost:3306/library_db_new"
        
        data_import = DataImport(
            file_resource="book",
            resource_type="mysql",
            db_connection_string=connection_string,
            is_database=True
        )
        
        # 获取表结构信息
        df = data_import.import_data(query="DESCRIBE book")
        
        if df is not None:
            print("✅ 获取 book 表结构成功")
            print(df)
        else:
            print("❌ 获取 book 表结构失败")
            
    except Exception as e:
        print(f"❌ 获取 book 表结构出错: {e}")
    finally:
        if 'data_import' in locals():
            data_import.close_connection()

def get_category_statistics():
    """
    获取书籍分类统计信息
    """
    print("\n" + "="*50 + "\n")
    print("获取书籍分类统计信息:")
    
    try:
        connection_string = "root:LMWDhcmy1973113@localhost:3306/library_db_new"
        
        data_import = DataImport(
            file_resource="book",
            resource_type="mysql",
            db_connection_string=connection_string,
            is_database=True
        )
        
        # 获取分类统计
        df = data_import.import_data(query="""
            SELECT category_id, COUNT(*) as count 
            FROM book 
            GROUP BY category_id
            ORDER BY category_id
        """)
        
        if df is not None:
            print("✅ 获取分类统计信息成功")
            print(df)
        else:
            print("❌ 获取分类统计信息失败")
            
    except Exception as e:
        print(f"❌ 获取分类统计信息出错: {e}")
    finally:
        if 'data_import' in locals():
            data_import.close_connection()

def get_publication_year_statistics():
    """
    获取出版年份统计信息
    """
    print("\n" + "="*50 + "\n")
    print("获取出版年份统计信息:")
    
    try:
        connection_string = "root:LMWDhcmy1973113@localhost:3306/library_db_new"
        
        data_import = DataImport(
            file_resource="book",
            resource_type="mysql",
            db_connection_string=connection_string,
            is_database=True
        )
        
        # 获取出版年份统计（按十年分组）
        df = data_import.import_data(query="""
            SELECT 
                FLOOR(YEAR(pub_date)/10)*10 as decade,
                COUNT(*) as count
            FROM book 
            WHERE pub_date IS NOT NULL
            GROUP BY FLOOR(YEAR(pub_date)/10)*10
            ORDER BY decade
        """)
        
        if df is not None:
            print("✅ 获取出版年份统计信息成功")
            print(df)
        else:
            print("❌ 获取出版年份统计信息失败")
            
    except Exception as e:
        print(f"❌ 获取出版年份统计信息出错: {e}")
    finally:
        if 'data_import' in locals():
            data_import.close_connection()

def get_sample_books_with_publisher():
    """
    获取包含出版社信息的书籍样本
    """
    print("\n" + "="*50 + "\n")
    print("获取包含出版社信息的书籍样本:")
    
    try:
        connection_string = "root:LMWDhcmy1973113@localhost:3306/library_db_new"
        
        data_import = DataImport(
            file_resource="book",
            resource_type="mysql",
            db_connection_string=connection_string,
            is_database=True
        )
        
        # 获取包含出版社信息的书籍样本
        df = data_import.import_data(query="""
            SELECT 
                b.book_id,
                b.title,
                b.pub_date,
                p.pub_name as publisher
            FROM book b
            LEFT JOIN publisher p ON b.pub_id = p.pub_id
            ORDER BY b.book_id
            LIMIT 15
        """)
        
        if df is not None:
            print("✅ 获取包含出版社信息的书籍样本成功")
            print(df)
        else:
            print("❌ 获取包含出版社信息的书籍样本失败")
            
    except Exception as e:
        print(f"❌ 获取包含出版社信息的书籍样本出错: {e}")
    finally:
        if 'data_import' in locals():
            data_import.close_connection()

def main():
    """
    主测试函数
    """
    print("开始详细测试 MySQL 数据库...\n")
    
    get_table_info()
    get_category_statistics()
    get_publication_year_statistics()
    get_sample_books_with_publisher()
    
    print("\nMySQL 数据库详细测试完成。")

if __name__ == "__main__":
    main()