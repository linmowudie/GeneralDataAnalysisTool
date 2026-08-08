"""
Example/database_import_example.py
数据库导入功能示例

该脚本演示如何使用 Infrastructures 层的数据库读取器（DbImporter）。
（原 DataProcessingEngine 已删除；导入能力现由
 backend.Infrastructures.importers.DbImporter 提供）
"""

import sys
import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录添加到系统路径
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.Infrastructures.importers import DbImporter


def mongodb_import_example():
    """MongoDB导入示例"""
    print("MongoDB导入示例")

    importer = DbImporter()

    try:
        # 从MongoDB导入数据
        # 注意：需要先确保MongoDB服务正在运行，并且有相应的数据
        df = importer.read(
            source="iris",  # 集合名称
            db_type="mongodb",
            db_connection_string="mongodb://localhost:27017/sklearn_datasets",
        )
        print(f"成功从MongoDB导入数据，共 {len(df)} 行")
        print("前5行数据：")
        print(df.head())

    except Exception as e:
        print(f"MongoDB导入过程中出现错误: {e}")


def redis_import_example():
    """Redis导入示例"""
    print("\nRedis导入示例")

    importer = DbImporter()

    try:
        # 从Redis导入数据
        # 注意：需要先确保Redis服务正在运行，并且有相应的数据
        df = importer.read(
            source="sample_data",  # 键名
            db_type="redis",
            db_connection_string="redis://localhost:6379/0",
        )
        print(f"成功从Redis导入数据，共 {len(df)} 行")
        print("数据内容：")
        print(df)

    except Exception as e:
        print(f"Redis导入过程中出现错误: {e}")


def traditional_db_import_example():
    """传统数据库导入示例"""
    print("\n传统数据库导入示例")

    importer = DbImporter()

    try:
        db_path = os.path.join(PROJECT_ROOT, "Data", "iris_test.db")
        # 从SQLite导入数据（示例）
        df = importer.read(
            source="iris",
            db_type="sqlite",
            db_connection_string=f"sqlite:///{db_path}",
            query="SELECT * FROM iris LIMIT 10",  # SQL查询
        )
        print(f"成功从SQLite导入数据，共 {len(df)} 行")
        print("前5行数据：")
        print(df.head())

    except Exception as e:
        print(f"SQLite导入过程中出现错误: {e}")


if __name__ == "__main__":
    print("=== 数据库导入功能演示 ===")

    # 运行示例
    mongodb_import_example()
    redis_import_example()
    traditional_db_import_example()

    print("\n=== 演示完成 ===")
