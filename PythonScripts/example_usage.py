#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据转换脚本使用示例
展示如何使用数据转换脚本进行各种格式转换
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def show_script_usage():
    """显示脚本使用示例"""
    print("=== 脚本使用示例 ===\n")
    
    # 数据转换脚本
    print("1. 数据转换脚本:")
    print("   将CSV文件转换为JSON格式:")
    print('   python PythonScripts/data_converter.py Data/iris.csv -o iris.json -f json\n')
    
    # 批量转换脚本
    print("2. 批量转换脚本:")
    print("   批量转换Data目录下的文件:")
    print('   python PythonScripts/batch_converter.py Data ScriptsOutput/Batch -f csv json xlsx\n')
    
    # 模型提取脚本
    print("3. 模型提取脚本:")
    print("   从数据训练模型并保存:")
    print('   python PythonScripts/model_extractor.py Data/iris.csv -m LogisticRegression --target-col target -o Models/iris_model.pkl\n')
    
    # 数据生成脚本
    print("4. 数据生成脚本:")
    print("   生成示例数据:")
    print('   python PythonScripts/generator.py -n 100 -o sample_data.csv\n')
    
    # MongoDB导入脚本
    print("5. MongoDB导入脚本:")
    print("   将CSV文件导入MongoDB:")
    print('   python PythonScripts/import_to_mongodb.py Data/iris.csv --db mydb --collection iris\n')


def example_single_conversion():
    """
    单文件转换示例
    """
    print("=== 单文件转换示例 ===")
    
    # 使用项目中的 iris.csv 作为示例
    input_file = "Data/iris.csv"
    
    if not os.path.exists(input_file):
        print(f"示例文件 {input_file} 不存在")
        return
    
    try:
        # 创建转换器
        converter = DataConverter(input_file)
        
        # 转换为不同格式
        print("\n1. 转换为 CSV 格式:")
        converter.to_csv("ScriptsOutput/iris_converted.csv")
        
        print("\n2. 转换为 Excel 格式:")
        converter.to_excel("ScriptsOutput/iris_converted.xlsx")
        
        print("\n3. 转换为 JSON 格式:")
        converter.to_json("ScriptsOutput/iris_converted.json")
        
        print("\n4. 转换为 HTML 格式:")
        converter.to_html("ScriptsOutput/iris_converted.html")
        
        print("\n5. 转换为 SQLite 数据库:")
        converter.to_sqlite("ScriptsOutput/iris_converted.db", "iris_data")
        
        print("\n单文件转换示例完成！")
        
    except Exception as e:
        print(f"单文件转换示例过程中发生错误: {e}")


def example_batch_conversion():
    """
    批量转换示例
    """
    print("\n=== 批量转换示例 ===")
    
    try:
        # 运行批量转换脚本
        import subprocess
        
        # 创建输出目录
        os.makedirs("ScriptsOutput/Batch", exist_ok=True)
        
        # 执行批量转换命令
        cmd = [
            "python", 
            "PythonScripts/batch_converter.py", 
            "Data", 
            "ScriptsOutput/Batch", 
            "-f", "csv", "json", "xlsx"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("批量转换执行成功:")
            print(result.stdout)
        else:
            print("批量转换执行失败:")
            print(result.stderr)
            
        print("批量转换示例完成！")
        
    except Exception as e:
        print(f"批量转换示例过程中发生错误: {e}")


def example_model_extraction():
    """
    模型提取示例
    """
    print("\n=== 模型提取示例 ===")
    
    try:
        # 运行模型提取脚本
        import subprocess
        
        # 创建输出目录
        os.makedirs("ScriptsOutput/Models", exist_ok=True)
        
        # 执行模型提取命令
        cmd = [
            "python",
            "PythonScripts/model_extractor.py",
            "Data/iris.csv",
            "-m", "LogisticRegression",
            "--target-col", "target",
            "-o", "ScriptsOutput/Models/iris_model.pkl"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("模型提取执行成功:")
            print(result.stdout)
        else:
            print("模型提取执行失败:")
            print(result.stderr)
            
        print("模型提取示例完成！")
        
    except Exception as e:
        print(f"模型提取示例过程中发生错误: {e}")


def create_sample_data():
    """
    创建示例数据文件用于测试
    """
    print("\n=== 创建示例数据 ===")
    
    # 创建示例数据目录
    os.makedirs("ScriptsOutput", exist_ok=True)
    
    # 创建示例数据
    sample_data = {
        'name': ['张三', '李四', '王五', '赵六'],
        'age': [25, 30, 35, 28],
        'city': ['北京', '上海', '广州', '深圳'],
        'salary': [8000, 12000, 15000, 10000]
    }
    
    df = pd.DataFrame(sample_data)
    
    # 保存为 CSV
    df.to_csv("ScriptsOutput/sample_data.csv", index=False)
    print("已创建示例数据文件: ScriptsOutput/sample_data.csv")


def main():
    """
    主函数
    """
    print("数据转换脚本使用示例")
    print("=" * 30)
    
    try:
        # 创建示例数据
        create_sample_data()
        
        # 运行单文件转换示例
        example_single_conversion()
        
        # 运行批量转换示例
        example_batch_conversion()
        
        # 运行模型提取示例
        example_model_extraction()
        
        print("\n所有示例运行完成！")
        print("\n输出文件保存在 ScriptsOutput 目录中")
        
    except Exception as e:
        print(f"示例运行过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()