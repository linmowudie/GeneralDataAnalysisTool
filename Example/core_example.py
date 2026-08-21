# Example/core_example.py
"""
Services 工作流使用示例
展示如何使用 ManualWorkflow 进行完整的数据分析流程
（原 DataProcessingEngine 已删除，由 ManualWorkflow + 部件体系取代）
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

from backend.Services import ManualWorkflow
from backend.Services.workflows.context import WorkflowContext
from backend.shared.types import StepName


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
    print("=== ManualWorkflow 使用示例 ===\n")

    # 1. 创建示例数据并保存为CSV
    print("1. 创建示例数据...")
    df = create_sample_data()
    sample_data_path = os.path.join(PROJECT_ROOT, "Data", "sample_data.csv")
    df.to_csv(sample_data_path, index=False)
    print(f"   数据已保存到: {sample_data_path}")
    print(f"   数据形状: {df.shape}")
    print(f"   缺失值:\n{df.isnull().sum()}")
    print()

    # 2. 初始化工作流与会话上下文
    print("2. 初始化工作流...")
    workflow = ManualWorkflow()
    context = WorkflowContext("core_example_session")
    print("   工作流初始化完成\n")

    try:
        # 3. 数据导入
        print("3. 导入数据...")
        import_artifact = workflow.execute_step(context, StepName.IMPORT, {
            "resource_path": sample_data_path,
            "resource_type": "csv",
        })
        print(f"   成功导入 {import_artifact.shape[0]} 行, {import_artifact.shape[1]} 列数据\n")

        # 4. 数据清洗
        print("4. 清洗数据...")
        cleaned_artifact = workflow.execute_step(context, StepName.CLEANING, {
            "select_mode": "standard",
            "params_list": [],
        })
        print(f"   清洗后数据形状: {cleaned_artifact.shape[0]} 行, {cleaned_artifact.shape[1]} 列\n")

        # 5. 数据分析
        print("5. 执行数据分析...")
        analysis_artifact = workflow.execute_step(context, StepName.ANALYSIS, {
            "model_type": "logisticregression",
            "target_col": "high_income",
            "feature_cols": ["age", "income", "education_years", "work_experience"],
            "is_return_model_score": True,
            "metrics_list": ["accuracy"],
            "split_ratio": 0.8,
        })
        print(f"   分析任务类型: {analysis_artifact.task_type.value}")
        print(f"   模型得分: {analysis_artifact.metrics}")
        print("   数据分析完成\n")

        # 6. 生成报告
        print("6. 生成分析报告...")
        report_artifact = workflow.execute_step(context, StepName.REPORT, {})
        print(f"   报告 ID: {report_artifact.report_id}")
        print(f"   报告内容键: {list(report_artifact.content.keys())}")
        print("   报告生成完成\n")

        print("=== 所有步骤执行完成 ===")

    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        raise

    finally:
        # 清理会话临时数据与示例文件
        context.get_temp_storage().clear_session(context.session_id)
        if os.path.exists(sample_data_path):
            os.remove(sample_data_path)
            print(f"已清理临时文件: {sample_data_path}")


if __name__ == "__main__":
    main()
