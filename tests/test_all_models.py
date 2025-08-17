# tests/test_all_models.py

import sys
import os
import pandas as pd
import numpy as np

# 获取项目根目录（tests 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 导入需要测试的模块
from Src.data_analyzer.core import DataProcessingEngine

def create_test_datasets():
    """创建用于测试不同类型模型的数据集"""
    np.random.seed(42)
    
    # 逻辑回归数据 (二分类)
    logistic_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'target': np.random.randint(0, 2, 100)  # 二分类目标
    }
    logistic_df = pd.DataFrame(logistic_data)
    
    # 线性回归数据 (回归)
    linear_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'target': np.random.randn(100) * 10 + 5  # 连续目标
    }
    linear_df = pd.DataFrame(linear_data)
    
    # KMeans聚类数据 (聚类)
    kmeans_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
    }
    kmeans_df = pd.DataFrame(kmeans_data)
    
    return logistic_df, linear_df, kmeans_df

def test_logistic_regression_model():
    """测试逻辑回归模型"""
    print("测试逻辑回归模型:")
    
    # 创建测试数据并保存为CSV
    logistic_df, _, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_logistic_data.csv")
    logistic_df.to_csv(test_file_path, index=False)
    
    try:
        # 初始化引擎
        engine = DataProcessingEngine()
        
        # 1. 数据导入
        engine.import_data(test_file_path, "csv")
        assert engine.imported_data is not None, "应成功导入数据"
        
        # 2. 数据清洗
        engine.clean_data(
            select_mode="standard",
            params_list=[]
        )
        assert engine.cleaned_data is not None, "应成功清洗数据"
        
        # 3. 数据分析 - 逻辑回归
        engine.analyze_data(
            model="logisticregression",
            target_col="target",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True,
            metrics_list=["accuracy"]
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'classification', "任务类型应为分类"
        
        # 4. 数据可视化
        engine.visualize_data()
        
        # 5. 生成报告
        engine.generate_report()
        assert engine.report_data is not None, "应成功生成报告"
        
        print(f"逻辑回归模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 模型得分: {engine.analyzed_data.get('scores', {})}")
        print(f"- 报告键: {list(engine.report_data.keys())}")
        print("✅ 逻辑回归模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_linear_regression_model():
    """测试线性回归模型"""
    print("测试线性回归模型:")
    
    # 创建测试数据并保存为CSV
    _, linear_df, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_linear_data.csv")
    linear_df.to_csv(test_file_path, index=False)
    
    try:
        # 初始化引擎
        engine = DataProcessingEngine()
        
        # 1. 数据导入
        engine.import_data(test_file_path, "csv")
        assert engine.imported_data is not None, "应成功导入数据"
        
        # 2. 数据清洗
        engine.clean_data(
            select_mode="standard",
            params_list=[]
        )
        assert engine.cleaned_data is not None, "应成功清洗数据"
        
        # 3. 数据分析 - 线性回归
        engine.analyze_data(
            model="linearregression",
            target_col="target",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True,
            metrics_list=["mse", "r2"]
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'regression', "任务类型应为回归"
        
        # 4. 数据可视化
        engine.visualize_data()
        
        # 5. 生成报告
        engine.generate_report()
        assert engine.report_data is not None, "应成功生成报告"
        
        print(f"线性回归模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 模型得分: {engine.analyzed_data.get('scores', {})}")
        print(f"- 报告键: {list(engine.report_data.keys())}")
        print("✅ 线性回归模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_kmeans_model():
    """测试KMeans聚类模型"""
    print("测试KMeans聚类模型:")
    
    # 创建测试数据并保存为CSV
    _, _, kmeans_df = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_kmeans_data.csv")
    kmeans_df.to_csv(test_file_path, index=False)
    
    try:
        # 初始化引擎
        engine = DataProcessingEngine()
        
        # 1. 数据导入
        engine.import_data(test_file_path, "csv")
        assert engine.imported_data is not None, "应成功导入数据"
        
        # 2. 数据清洗
        engine.clean_data(
            select_mode="standard",
            params_list=[]
        )
        assert engine.cleaned_data is not None, "应成功清洗数据"
        
        # 3. 数据分析 - KMeans聚类
        engine.analyze_data(
            model="kmeans",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=False  # 聚类通常不返回传统意义上的得分
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'clustering', "任务类型应为聚类"
        
        # 4. 数据可视化
        engine.visualize_data()
        
        # 5. 生成报告
        engine.generate_report()
        assert engine.report_data is not None, "应成功生成报告"
        
        print(f"KMeans聚类模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 报告键: {list(engine.report_data.keys())}")
        print("✅ KMeans聚类模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_model_comparison():
    """测试多个模型的比较"""
    print("测试多个模型比较:")
    
    # 使用逻辑回归数据测试多个模型
    logistic_df, _, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_compare_data.csv")
    logistic_df.to_csv(test_file_path, index=False)
    
    try:
        models_to_test = ["logisticregression", "linearregression", "kmeans"]
        results = {}
        
        for model in models_to_test:
            try:
                # 初始化引擎
                engine = DataProcessingEngine()
                
                # 1. 数据导入
                engine.import_data(test_file_path, "csv")
                
                # 2. 数据清洗
                engine.clean_data(
                    select_mode="standard",
                    params_list=[]
                )
                
                # 3. 数据分析
                if model == "kmeans":
                    engine.analyze_data(
                        model=model,
                        feature_cols=["feature1", "feature2", "feature3"]
                    )
                else:
                    engine.analyze_data(
                        model=model,
                        target_col="target",
                        feature_cols=["feature1", "feature2", "feature3"],
                        is_return_model_score=True
                    )
                
                # 保存结果
                results[model] = {
                    'success': True,
                    'task_type': engine.analyzed_data.get('task_type', 'Unknown'),
                    'scores': engine.analyzed_data.get('scores', {})
                }
                print(f"模型 {model} 执行成功")
                
            except Exception as e:
                results[model] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"模型 {model} 执行失败: {str(e)}")
        
        print("模型比较结果:")
        for model, result in results.items():
            if result['success']:
                print(f"  {model}: 成功 (任务类型: {result['task_type']})")
                if result['scores']:
                    print(f"    得分: {result['scores']}")
            else:
                print(f"  {model}: 失败 ({result['error']})")
        
        print("✅ 模型比较测试完成\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

# 测试代码
if __name__ == "__main__":
    print("开始测试所有模型\n")
    print("="*50 + "\n")
    
    # 运行各种模型测试
    test_logistic_regression_model()
    test_linear_regression_model()
    test_kmeans_model()
    test_model_comparison()
    
    print("="*50)
    print("所有模型测试完成!")