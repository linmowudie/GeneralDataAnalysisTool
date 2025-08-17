# tests/test_all_analysis_models.py

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
    
    # 创建分类数据
    classification_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'target_class': np.random.randint(0, 2, 100)  # 二分类目标
    }
    classification_df = pd.DataFrame(classification_data)
    
    # 创建回归数据
    regression_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'target_reg': np.random.randn(100) * 10 + 5  # 连续目标
    }
    regression_df = pd.DataFrame(regression_data)
    
    # 创建聚类数据
    clustering_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
    }
    clustering_df = pd.DataFrame(clustering_data)
    
    return classification_df, regression_df, clustering_df

def test_linear_regression():
    """测试线性回归模型"""
    print("测试线性回归模型:")
    
    # 创建测试数据并保存为CSV
    _, regression_df, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_linear_regression_data.csv")
    regression_df.to_csv(test_file_path, index=False)
    
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
            target_col="target_reg",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True,
            metrics_list=["mse", "r2"]
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'regression', "任务类型应为回归"
        
        print(f"线性回归模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 任务类型: {engine.analyzed_data.get('task_type')}")
        print(f"- 模型得分: {engine.analyzed_data.get('scores', {})}")
        print("✅ 线性回归模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_logistic_regression():
    """测试逻辑回归模型"""
    print("测试逻辑回归模型:")
    
    # 创建测试数据并保存为CSV
    classification_df, _, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_logistic_regression_data.csv")
    classification_df.to_csv(test_file_path, index=False)
    
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
            target_col="target_class",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True,
            metrics_list=["accuracy"]
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'classification', "任务类型应为分类"
        
        print(f"逻辑回归模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 任务类型: {engine.analyzed_data.get('task_type')}")
        print(f"- 模型得分: {engine.analyzed_data.get('scores', {})}")
        print("✅ 逻辑回归模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_decision_tree_classifier():
    """测试决策树分类器模型"""
    print("测试决策树分类器模型:")
    
    # 创建测试数据并保存为CSV
    classification_df, _, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_decision_tree_data.csv")
    classification_df.to_csv(test_file_path, index=False)
    
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
        
        # 3. 数据分析 - 决策树分类器
        engine.analyze_data(
            model="decisiontreeclassifier",
            target_col="target_class",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True,
            metrics_list=["accuracy"]
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'classification', "任务类型应为分类"
        
        print(f"决策树分类器模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 任务类型: {engine.analyzed_data.get('task_type')}")
        print(f"- 模型得分: {engine.analyzed_data.get('scores', {})}")
        print("✅ 决策树分类器模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_kneighbors_classifier():
    """测试K近邻分类器模型"""
    print("测试K近邻分类器模型:")
    
    # 创建测试数据并保存为CSV
    classification_df, _, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_kneighbors_data.csv")
    classification_df.to_csv(test_file_path, index=False)
    
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
        
        # 3. 数据分析 - K近邻分类器
        engine.analyze_data(
            model="kneighborsclassifier",
            target_col="target_class",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True,
            metrics_list=["accuracy"]
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'classification', "任务类型应为分类"
        
        print(f"K近邻分类器模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 任务类型: {engine.analyzed_data.get('task_type')}")
        print(f"- 模型得分: {engine.analyzed_data.get('scores', {})}")
        print("✅ K近邻分类器模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_kmeans():
    """测试KMeans聚类模型"""
    print("测试KMeans聚类模型:")
    
    # 创建测试数据并保存为CSV
    _, _, clustering_df = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_kmeans_data.csv")
    clustering_df.to_csv(test_file_path, index=False)
    
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
            is_return_model_score=True
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'clustering', "任务类型应为聚类"
        
        print(f"KMeans聚类模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 任务类型: {engine.analyzed_data.get('task_type')}")
        print(f"- 模型得分: {engine.analyzed_data.get('scores', {})}")
        print("✅ KMeans聚类模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_meanshift():
    """测试MeanShift聚类模型"""
    print("测试MeanShift聚类模型:")
    
    # 创建测试数据并保存为CSV
    _, _, clustering_df = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_meanshift_data.csv")
    clustering_df.to_csv(test_file_path, index=False)
    
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
        
        # 3. 数据分析 - MeanShift聚类
        engine.analyze_data(
            model="meanshift",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=True
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'clustering', "任务类型应为聚类"
        
        print(f"MeanShift聚类模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 任务类型: {engine.analyzed_data.get('task_type')}")
        print(f"- 模型得分: {engine.analyzed_data.get('scores', {})}")
        print("✅ MeanShift聚类模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_standard_scaler():
    """测试StandardScaler标准化模型"""
    print("测试StandardScaler标准化模型:")
    
    # 创建测试数据并保存为CSV
    _, regression_df, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_standard_scaler_data.csv")
    regression_df.to_csv(test_file_path, index=False)
    
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
        
        # 3. 数据分析 - StandardScaler标准化
        engine.analyze_data(
            model="standardscaler",
            feature_cols=["feature1", "feature2", "feature3"]
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'transformer', "任务类型应为变换器"
        
        print(f"StandardScaler标准化模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 任务类型: {engine.analyzed_data.get('task_type')}")
        print("✅ StandardScaler标准化模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_pca():
    """测试PCA降维模型"""
    print("测试PCA降维模型:")
    
    # 创建测试数据并保存为CSV
    _, regression_df, _ = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_pca_data.csv")
    regression_df.to_csv(test_file_path, index=False)
    
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
        
        # 3. 数据分析 - PCA降维
        engine.analyze_data(
            model="pca",
            feature_cols=["feature1", "feature2", "feature3"],
            is_return_model_score=False
        )
        assert engine.analyzed_data is not None, "应成功分析数据"
        assert engine.analyzed_data.get('task_type') == 'transformer', "任务类型应为变换器"
        
        print(f"PCA降维模型测试通过")
        print(f"- 导入数据形状: {engine.imported_data.shape}")
        print(f"- 清洗数据形状: {engine.cleaned_data.shape}")
        print(f"- 任务类型: {engine.analyzed_data.get('task_type')}")
        print("✅ PCA降维模型测试通过\n")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_model_comparison():
    """测试所有模型的比较"""
    print("测试所有模型比较:")
    
    # 使用分类数据测试所有模型
    classification_df, regression_df, clustering_df = create_test_datasets()
    test_file_path = os.path.join(PROJECT_ROOT, "test_compare_data.csv")
    classification_df.to_csv(test_file_path, index=False)
    
    # 定义所有支持的模型及其配置
    models_config = [
        {
            'name': 'linearregression',
            'type': 'regression',
            'target': 'target_reg',
            'data': regression_df
        },
        {
            'name': 'logisticregression',
            'type': 'classification',
            'target': 'target_class',
            'data': classification_df
        },
        {
            'name': 'decisiontreeclassifier',
            'type': 'classification',
            'target': 'target_class',
            'data': classification_df
        },
        {
            'name': 'kneighborsclassifier',
            'type': 'classification',
            'target': 'target_class',
            'data': classification_df
        },
        {
            'name': 'kmeans',
            'type': 'clustering',
            'target': None,
            'data': clustering_df
        },
        {
            'name': 'meanshift',
            'type': 'clustering',
            'target': None,
            'data': clustering_df
        },
        {
            'name': 'standardscaler',
            'type': 'transformer',
            'target': None,
            'data': regression_df
        },
        {
            'name': 'pca',
            'type': 'transformer',
            'target': None,
            'data': regression_df
        }
    ]
    
    results = {}
    
    for model_config in models_config:
        model_name = model_config['name']
        model_type = model_config['type']
        target_col = model_config['target']
        data = model_config['data']
        
        # 为每个模型创建单独的测试文件
        model_test_file = os.path.join(PROJECT_ROOT, f"test_{model_name}_data.csv")
        data.to_csv(model_test_file, index=False)
        
        try:
            # 初始化引擎
            engine = DataProcessingEngine()
            
            # 1. 数据导入
            engine.import_data(model_test_file, "csv")
            
            # 2. 数据清洗
            engine.clean_data(
                select_mode="standard",
                params_list=[]
            )
            
            # 3. 数据分析
            if model_type in ['clustering', 'transformer']:
                # 聚类和变换器模型不需要目标列
                engine.analyze_data(
                    model=model_name,
                    feature_cols=["feature1", "feature2", "feature3"],
                    is_return_model_score=(model_type != 'transformer')  # transformer通常不返回得分
                )
            else:
                # 分类和回归模型需要目标列
                engine.analyze_data(
                    model=model_name,
                    target_col=target_col,
                    feature_cols=["feature1", "feature2", "feature3"],
                    is_return_model_score=True
                )
            
            # 保存结果
            results[model_name] = {
                'success': True,
                'task_type': engine.analyzed_data.get('task_type', 'Unknown'),
                'scores': engine.analyzed_data.get('scores', {})
            }
            print(f"模型 {model_name} 执行成功")
            
        except Exception as e:
            results[model_name] = {
                'success': False,
                'error': str(e)
            }
            print(f"模型 {model_name} 执行失败: {str(e)}")
        finally:
            # 清理测试文件
            if os.path.exists(model_test_file):
                os.remove(model_test_file)
    
    print("\n模型比较结果:")
    for model_name, result in results.items():
        if result['success']:
            print(f"  {model_name}: 成功 (任务类型: {result['task_type']})")
            if result['scores']:
                print(f"    得分: {result['scores']}")
        else:
            print(f"  {model_name}: 失败 ({result['error']})")
    
    print("✅ 模型比较测试完成\n")

# 测试代码
if __name__ == "__main__":
    print("开始测试所有数据分析模型\n")
    print("="*60 + "\n")
    
    # 运行各种模型测试
    test_linear_regression()
    test_logistic_regression()
    test_decision_tree_classifier()
    test_kneighbors_classifier()
    test_kmeans()
    test_meanshift()
    test_standard_scaler()
    test_pca()
    test_model_comparison()
    
    print("="*60)
    print("所有数据分析模型测试完成!")