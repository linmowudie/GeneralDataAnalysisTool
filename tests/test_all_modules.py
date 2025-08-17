# tests/test_all_modules.py

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
from Src.data_analyzer import data_import, data_cleaning, data_analysis, data_visualization

def create_test_datasets():
    """创建用于测试不同类型模型的数据集"""
    np.random.seed(42)
    
    # 通用测试数据
    data = {
        'feature1': np.random.randn(50),
        'feature2': np.random.randn(50),
        'feature3': np.random.randn(50),
        'category': np.random.choice(['A', 'B', 'C'], 50),
        'target_reg': np.random.randn(50) * 10 + 5,  # 回归目标
        'target_class': np.random.randint(0, 2, 50)  # 分类目标
    }
    df = pd.DataFrame(data)
    
    return df

def test_data_import_module():
    """测试数据导入模块"""
    print("测试数据导入模块:")
    
    # 创建测试数据并保存为CSV
    df = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_import_data.csv")
    df.to_csv(test_file_path, index=False)
    
    try:
        # 测试文件导入
        importer = data_import.DataImport(
            file_resource=test_file_path,
            resource_type="csv"
        )
        imported_data = importer.import_data()
        
        assert imported_data is not None, "应成功导入数据"
        assert isinstance(imported_data, pd.DataFrame), "导入数据应为DataFrame类型"
        assert imported_data.shape == df.shape, "导入数据形状应与原数据一致"
        
        print(f"数据导入模块测试通过")
        print(f"- 导入数据形状: {imported_data.shape}")
        print(f"- 列名: {list(imported_data.columns)}")
        print("✅ 数据导入模块测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_data_cleaning_module():
    """测试数据清洗模块"""
    print("测试数据清洗模块:")
    
    # 创建带缺失值的测试数据
    df = create_test_datasets()
    # 添加一些缺失值用于测试清洗功能
    df.loc[0, 'feature1'] = np.nan
    df.loc[2, 'feature2'] = np.nan
    df.loc[5, 'category'] = np.nan
    
    test_file_path = os.path.join(PROJECT_ROOT, "test_cleaning_data.csv")
    df.to_csv(test_file_path, index=False)
    
    try:
        # 先导入数据
        importer = data_import.DataImport(
            file_resource=test_file_path,
            resource_type="csv"
        )
        imported_data = importer.import_data()
        
        # 测试数据清洗
        cleaner = data_cleaning.CleanDataMode(
            df=imported_data,
            select_mode="standard",
            params_list=[]
        )
        cleaned_data = cleaner.clean_data()
        
        assert cleaned_data is not None, "应成功清洗数据"
        assert isinstance(cleaned_data, pd.DataFrame), "清洗数据应为DataFrame类型"
        # 清洗后数据行数应该不变（因为standard模式不会删除行）
        assert cleaned_data.shape[0] == imported_data.shape[0], "清洗后行数应保持一致"
        
        print(f"数据清洗模块测试通过")
        print(f"- 原始数据形状: {imported_data.shape}")
        print(f"- 清洗数据形状: {cleaned_data.shape}")
        print("✅ 数据清洗模块测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_data_analysis_module():
    """测试数据分析模块"""
    print("测试数据分析模块:")
    
    # 创建测试数据
    df = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_analysis_data.csv")
    df.to_csv(test_file_path, index=False)
    
    try:
        # 先导入数据
        importer = data_import.DataImport(
            file_resource=test_file_path,
            resource_type="csv"
        )
        imported_data = importer.import_data()
        
        # 测试数据分析 - 使用逻辑回归
        analyzer = data_analysis.DataAnalyzer(
            df=imported_data,
            model="logisticregression",
            target_col="target_class",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True,
            metrics_list=["accuracy"]
        )
        analysis_result = analyzer.analyze()
        
        assert analysis_result is not None, "应成功分析数据"
        assert isinstance(analysis_result, dict), "分析结果应为字典类型"
        # 修复断言，根据实际返回的数据结构调整
        assert 'task_type' in analysis_result, "分析结果应包含任务类型"
        assert 'scores' in analysis_result, "分析结果应包含得分"
        
        print(f"数据分析模块测试通过")
        print(f"- 分析结果键: {list(analysis_result.keys())}")
        print(f"- 模型得分: {analysis_result.get('scores', {})}")
        print("✅ 数据分析模块测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_data_visualization_module():
    """测试数据可视化模块"""
    print("测试数据可视化模块:")
    
    # 创建测试数据
    df = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_visualization_data.csv")
    df.to_csv(test_file_path, index=False)
    
    try:
        # 先导入数据
        importer = data_import.DataImport(
            file_resource=test_file_path,
            resource_type="csv"
        )
        imported_data = importer.import_data()
        
        # 简单测试参数字典
        param_dict = {
            'task_type': 'classification',
            'model_name': 'logisticregression',
            'feature': imported_data[['feature1', 'feature2', 'feature3']],
            'target': imported_data['target_class'],
            'label_style': {'x': 'Feature', 'y': 'Target', 'title': 'Test Plot'},
        }
        
        # 测试数据可视化
        visualizer = data_visualization.DataVisualization(param_dict)
        # 注意：由于我们不测试实际绘图功能，这里只是测试对象创建和基本参数验证
        assert visualizer is not None, "应成功创建可视化对象"
        assert visualizer.param_dict == param_dict, "参数字典应正确设置"
        
        print(f"数据可视化模块测试通过")
        print(f"- 参数字典键: {list(param_dict.keys())}")
        print("✅ 数据可视化模块测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_core_engine_comprehensive():
    """综合测试核心引擎的所有功能"""
    print("综合测试核心引擎:")
    
    # 创建测试数据
    df = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_engine_data.csv")
    df.to_csv(test_file_path, index=False)
    
    try:
        # 初始化引擎
        engine = DataProcessingEngine()
        
        # 测试完整流程
        # 1. 数据导入
        engine.import_data(test_file_path, "csv")
        assert engine.imported_data is not None, "应成功导入数据"
        
        # 2. 数据清洗
        engine.clean_data(
            select_mode="standard",
            params_list=[]
        )
        assert engine.cleaned_data is not None, "应成功清洗数据"
        
        # 3. 数据分析
        engine.analyze_data(
            model="logisticregression",
            target_col="target_class",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True,
            metrics_list=["accuracy"]
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        
        # 4. 数据可视化
        engine.visualize_data()
        assert engine.visualized_plot is not None, "应成功可视化数据"
        
        # 5. 生成报告
        engine.generate_report()
        assert engine.report_data is not None, "应成功生成报告"
        
        print(f"核心引擎综合测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 分析结果键: {list(engine.analyzed_data.keys())}")
        print(f"- 可视化图表数: {len(engine.visualized_plot) if engine.visualized_plot else 0}")
        print(f"- 报告键: {list(engine.report_data.keys())}")
        print("✅ 核心引擎综合测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

# 测试代码
if __name__ == "__main__":
    print("开始测试所有模块\n")
    print("="*50 + "\n")
    
    # 运行各个模块测试
    test_data_import_module()
    test_data_cleaning_module()
    test_data_analysis_module()
    test_data_visualization_module()
    test_core_engine_comprehensive()
    
    print("="*50)
    print("所有模块测试完成!")