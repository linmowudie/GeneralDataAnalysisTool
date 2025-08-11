# examples/core_example.py
"""
Core模块使用示例
展示如何使用DataProcessingEngine进行完整的数据分析流程
"""

import sys
import os
import pandas as pd
import numpy as np

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录添加到系统路径
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.data_analyzer.core import DataProcessingEngine

def create_sample_data():
    """创建示例数据集"""
    np.random.seed(42)
    
    # 创建示例数据
    data = {
        'age': np.random.randint(18, 80, 1000),
        'income': np.random.normal(50000, 15000, 1000),
        'education_years': np.random.randint(8, 20, 1000),
        'work_experience': np.random.randint(0, 40, 1000),
    }
    
    # 创建目标变量（是否高收入）
    # 假设高收入与年龄、教育年限和工作经验正相关
    linear_combination = (
        0.01 * data['age'] +
        0.0001 * data['income'] +
        0.05 * data['education_years'] +
        0.03 * data['work_experience'] +
        np.random.normal(0, 0.5, 1000)
    )
    data['high_income'] = (linear_combination > np.median(linear_combination)).astype(int)
    
    df = pd.DataFrame(data)
    
    # 添加一些缺失值以演示清洗功能
    missing_indices = np.random.choice(df.index, size=50, replace=False)
    df.loc[missing_indices[:25], 'income'] = np.nan
    df.loc[missing_indices[25:], 'education_years'] = np.nan
    
    # 添加一些重复行以演示清洗功能
    duplicate_rows = df.sample(20)
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    return df

def main():
    """主函数，演示完整的数据分析流程"""
    print("=== DataProcessingEngine 使用示例 ===\n")
    
    # 1. 创建示例数据并保存为CSV
    print("1. 创建示例数据...")
    df = create_sample_data()
    sample_data_path = os.path.join(PROJECT_ROOT, "Data", "sample_data.csv")
    df.to_csv(sample_data_path, index=False)
    print(f"   数据已保存到: {sample_data_path}")
    print(f"   数据形状: {df.shape}")
    print(f"   缺失值:\n{df.isnull().sum()}")
    print()
    
    try:
        # 2. 初始化数据处理引擎
        print("2. 初始化数据处理引擎...")
        engine = DataProcessingEngine()
        print("   引擎初始化完成\n")
        
        # 3. 数据导入
        print("3. 导入数据...")
        engine.import_data(
            resource_path=sample_data_path,
            resource_type="csv"
        )
        print(f"   成功导入 {engine.imported_data.shape[0]} 行, {engine.imported_data.shape[1]} 列数据\n")
        
        # 4. 数据清洗
        print("4. 清洗数据...")
        engine.clean_data(
            select_mode="standard",  # 使用标准清洗模式
            params_list=[]  # 不使用自定义参数
        )
        print(f"   清洗后数据形状: {engine.cleaned_data.shape[0]} 行, {engine.cleaned_data.shape[1]} 列\n")
        
        # 5. 数据分析
        print("5. 执行数据分析...")
        engine.analyze_data(
            model="logisticregression",
            target_col="high_income",
            feature_cols=["age", "income", "education_years", "work_experience"],
            is_return_model_score=True,
            metrics_list=["accuracy"],
            split_ratio=0.8
        )
        print(f"   分析任务类型: {engine.analyzed_data.get('task_type', 'N/A')}")
        print(f"   模型得分: {engine.analyzed_data.get('scores', 'N/A')}")
        print("   数据分析完成\n")
        
        # 6. 生成报告
        print("6. 生成分析报告...")
        engine.generate_report()
        report_keys = list(engine.report_data.keys()) if engine.report_data else []
        print(f"   报告内容包含: {report_keys}")
        print("   报告生成完成\n")
        
        # 7. 获取最终报告
        print("7. 获取最终报告...")
        final_report = engine.get_report()
        if final_report:
            print(f"   报告键: {list(final_report.keys())}")
            if 'model_scores' in final_report:
                print(f"   模型得分: {final_report['model_scores']}")
            print("   成功获取分析报告\n")
        
        print("=== 所有步骤执行完成 ===")
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        raise
        
    finally:
        # 清理示例文件
        if os.path.exists(sample_data_path):
            os.remove(sample_data_path)
            print(f"已清理临时文件: {sample_data_path}")

if __name__ == "__main__":
    main()