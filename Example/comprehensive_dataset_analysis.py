# examples/comprehensive_dataset_analysis.py

import sys
import os
import pandas as pd
import numpy as np

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==================================================

# 导入需要的模块
from Src.DataAnalyzer.AnalysisModule.analyzer import analyze_data

def load_dataset(filename):
    """加载数据集"""
    file_path = os.path.join(PROJECT_ROOT, 'Data', filename)
    return pd.read_csv(file_path)

def analyze_dataset(name, df, task_type, target_col=None, feature_cols=None):
    """分析数据集"""
    print(f"\n{'='*60}")
    print(f"分析 {name} 数据集")
    print(f"{'='*60}")
    print(f"数据形状: {df.shape}")
    
    if target_col and task_type in ['classification', 'regression']:
        print(f"目标变量分布:\n{df[target_col].value_counts() if df[target_col].dtype == 'int64' else df[target_col].describe()}")
    
    models = []
    if task_type == 'classification':
        models = ["logisticregression", "decisiontreeclassifier"]
    elif task_type == 'regression':
        models = ["linearregression", "ridge"]
    elif task_type == 'transformer':
        models = ["pca", "standardscaler"]
    
    results = {}
    for model in models:
        print(f"\n测试 {model} 模型:")
        try:
            if task_type == 'transformer':
                result = analyze_data(
                    df=df,
                    model=model,
                    is_return_model_score=False,
                    is_return_training_set=True
                )
                print(f"  原始维度: {df.shape}")
                print(f"  处理后维度: {result['X_train'].shape}")
            else:
                result = analyze_data(
                    df=df,
                    model=model,
                    target_col=target_col,
                    feature_cols=feature_cols,
                    is_return_model_score=True
                )
                
                if task_type == 'classification':
                    accuracy = result['scores']['accuracy']
                    results[model] = accuracy
                    print(f"  准确率: {accuracy:.4f}")
                elif task_type == 'regression':
                    r2 = result['scores']['r2']
                    mse = result['scores']['mse']
                    results[model] = {'r2': r2, 'mse': mse}
                    print(f"  R² 分数: {r2:.4f}")
                    print(f"  均方误差: {mse:.4f}")
            
            print(f"  模型类型: {result['task_type']}")
            print("  测试通过")
            
        except Exception as e:
            print(f"  测试失败: {e}")
            results[model] = None
    
    return results

def main():
    """主函数"""
    print("综合数据集分析报告")
    print("使用新的数据分析模块接口")
    
    all_results = {}
    
    try:
        # 1. Iris数据集
        df_iris = load_dataset('iris_sklearn.csv')
        all_results['Iris'] = analyze_dataset(
            'Iris', 
            df_iris, 
            'classification', 
            target_col='target'
        )
        
        # 2. Wine数据集
        df_wine = load_dataset('wine.csv')
        all_results['Wine'] = analyze_dataset(
            'Wine', 
            df_wine, 
            'classification', 
            target_col='target'
        )
        
        # 3. Breast Cancer数据集
        df_cancer = load_dataset('breast_cancer.csv')
        all_results['Breast Cancer'] = analyze_dataset(
            'Breast Cancer', 
            df_cancer, 
            'classification', 
            target_col='target'
        )
        
        # 4. Diabetes数据集
        df_diabetes = load_dataset('diabetes.csv')
        all_results['Diabetes'] = analyze_dataset(
            'Diabetes', 
            df_diabetes, 
            'regression', 
            target_col='target'
        )
        
        # 5. California Housing数据集 (采样以加快速度)
        df_housing = load_dataset('california_housing.csv').sample(n=2000, random_state=42)
        all_results['California Housing'] = analyze_dataset(
            'California Housing', 
            df_housing, 
            'regression', 
            target_col='target'
        )
        
        # 6. Linnerud数据集
        df_linnerud = load_dataset('linnerud.csv')
        all_results['Linnerud'] = analyze_dataset(
            'Linnerud', 
            df_linnerud, 
            'transformer'
        )
        
        # 生成总结报告
        print(f"\n{'='*60}")
        print("综合分析总结")
        print(f"{'='*60}")
        
        for dataset_name, results in all_results.items():
            if results:  # 如果有结果
                print(f"\n{dataset_name} 数据集:")
                valid_results = {k: v for k, v in results.items() if v is not None}
                if valid_results:
                    if isinstance(list(valid_results.values())[0], dict):  # 回归结果
                        best_model = max(valid_results, key=lambda x: valid_results[x]['r2'])
                        best_r2 = valid_results[best_model]['r2']
                        print(f"  最佳模型: {best_model} (R²: {best_r2:.4f})")
                    else:  # 分类结果
                        best_model = max(valid_results, key=valid_results.get)
                        best_accuracy = valid_results[best_model]
                        print(f"  最佳模型: {best_model} (准确率: {best_accuracy:.4f})")
        
        print(f"\n{'='*60}")
        print("所有数据集分析完成!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()