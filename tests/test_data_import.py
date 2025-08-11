# tests/test_data_import.py

import sys
import os

# 获取项目根目录（tests 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ==================================================

# 现在可以正常导入 Src 下的模块
from Src.data_analyzer.data_import import DataImport

# 测试代码
if __name__ == "__main__":
    # 测试 CSV 文件导入
    print("测试 CSV 文件导入:")
    data_import_csv = DataImport(
        file_resource=os.path.join(PROJECT_ROOT, "Data", "iris.csv"),
        resource_type="csv"
    )

    df_csv = data_import_csv.import_data()

    if df_csv is not None:
        print("✅ CSV 数据导入成功")
        print(df_csv.head())
    else:
        print("❌ CSV 数据导入失败")
    
    print("\n" + "="*50 + "\n")
    
    # 测试 XLSX 文件导入
    print("测试 XLSX 文件导入:")
    data_import_xlsx = DataImport(
        file_resource=os.path.join(PROJECT_ROOT, "Data", "iris.xlsx"),
        resource_type="xlsx"
    )

    df_xlsx = data_import_xlsx.import_data()

    if df_xlsx is not None:
        print("✅ XLSX 数据导入成功")
        print(df_xlsx.head())
    else:
        print("❌ XLSX 数据导入失败")
        
    print("\n" + "="*50 + "\n")
    
    # 测试 JSON 文件导入
    print("测试 JSON 文件导入:")
    data_import_json = DataImport(
        file_resource=os.path.join(PROJECT_ROOT, "Data", "iris.json"),
        resource_type="json"
    )

    df_json = data_import_json.import_data()

    if df_json is not None:
        print("✅ JSON 数据导入成功")
        print(df_json.head())
    else:
        print("❌ JSON 数据导入失败")
        
    print("\n" + "="*50 + "\n")
    
    # 测试 HTML 文件导入
    print("测试 HTML 文件导入:")
    data_import_html = DataImport(
        file_resource=os.path.join(PROJECT_ROOT, "Data", "iris.html"),
        resource_type="html"
    )

    df_html = data_import_html.import_data()

    if df_html is not None:
        # read_html 返回的是一个包含DataFrame的列表，我们取第一个
        df = df_html[0] if isinstance(df_html, list) else df_html
        print("✅ HTML 数据导入成功")
        print(df.head())
    else:
        print("❌ HTML 数据导入失败")