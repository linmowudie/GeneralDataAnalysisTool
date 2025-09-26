# examples/iris_comprehensive_analysis.py

import sys
import os
import pandas as pd
import numpy as np
import json

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==================================================

# 导入需要的模块
from Src.DataAnalyzer.analysis.analyzer import analyze_data

def load_iris_data():
    """加载iris数据集"""
    file_path = os.path.join(PROJECT_ROOT, 'Data', 'iris.csv')
    df = pd.read_csv(file_path)
    return df.drop('target_name', axis=1)  # 移除文本目标列

def comprehensive_classification_analysis():
    """综合分类分析"""
    print("=" * 60)
    print("综合分类分析报告")
    print("=" * 60)
    
    df = load_iris_data()
    
    models = ["logisticregression", "decisiontreeclassifier", "kneighborsclassifier", "svc"]
    
    results = {}
    
    for model in models:
        print(f"\n正在分析 {model}...")
        try:
            result = analyze_data(
                df=df,
                model=model,
                target_col="target",
                is_return_model_score=True,
                is_return_model_param=True,
                is_return_model_predicting_set=True,
                is_return_training_set=True
            )
            
            accuracy = result['scores']['accuracy']
            results[model] = {
                'accuracy': accuracy,
                'model_params_count': len(result['model_params']),
                'prediction_count': len(result['predictions']),
                'train_set_shape': result['X_train'].shape,
                'test_set_shape': result['X_test'].shape
            }
            
            print(f"  准确率: {accuracy:.4f}")
            print(f"  模型参数数量: {len(result['model_params'])}")
            print(f"  训练集大小: {result['X_train'].shape}")
            print(f"  测试集大小: {result['X_test'].shape}")
            
        except Exception as e:
            print(f"  分析失败: {e}")
            results[model] = None
    
    # 找出最佳模型
    valid_results = {k: v for k, v in results.items() if v is not None}
    if valid_results:
        best_model = max(valid_results, key=lambda x: valid_results[x]['accuracy'])
        print(f"\n🏆 最佳分类模型: {best_model}")
        print(f"   准确率: {valid_results[best_model]['accuracy']:.4f}")
    
    return results

def comprehensive_clustering_analysis():
    """综合聚类分析"""
    print("\n" + "=" * 60)
    print("综合聚类分析报告")
    print("=" * 60)
    
    df = load_iris_data()
    # 只使用特征列进行聚类
    df_features = df.drop('target', axis=1)
    
    models = ["kmeans", "meanshift", "dbscan"]
    
    results = {}
    
    for model in models:
        print(f"\n正在分析 {model}...")
        try:
            result = analyze_data(
                df=df_features,
                model=model,
                is_return_model_score=True,
                is_return_model_param=True
            )
            
            silhouette = result['scores'].get('silhouette', 'N/A')
            results[model] = {
                'silhouette': silhouette,
                'model_params_count': len(result['model_params']) if result['model_params'] else 0
            }
            
            print(f"  轮廓系数: {silhouette}")
            print(f"  模型参数数量: {len(result['model_params']) if result['model_params'] else 0}")
            
        except Exception as e:
            print(f"  分析失败: {e}")
            results[model] = None
    
    # 找出最佳模型（基于轮廓系数）
    valid_results = {k: v for k, v in results.items() if v is not None and v['silhouette'] != 'N/A'}
    if valid_results:
        best_model = max(valid_results, key=lambda x: valid_results[x]['silhouette'])
        print(f"\n🏆 最佳聚类模型: {best_model}")
        print(f"   轮廓系数: {valid_results[best_model]['silhouette']:.4f}")
    
    return results

def comprehensive_dimensionality_reduction_analysis():
    """综合降维分析"""
    print("\n" + "=" * 60)
    print("综合降维分析报告")
    print("=" * 60)
    
    df = load_iris_data()
    df_features = df.drop('target', axis=1)
    
    models = ["pca", "standardscaler", "minmaxscaler"]
    
    results = {}
    
    for model in models:
        print(f"\n正在分析 {model}...")
        try:
            result = analyze_data(
                df=df_features,
                model=model,
                is_return_model_param=True,
                is_return_training_set=True
            )
            
            original_shape = df_features.shape
            reduced_shape = result['X_train'].shape
            results[model] = {
                'original_shape': original_shape,
                'reduced_shape': reduced_shape,
                'model_params_count': len(result['model_params']) if result['model_params'] else 0
            }
            
            print(f"  原始维度: {original_shape}")
            print(f"  降维后维度: {reduced_shape}")
            print(f"  模型参数数量: {len(result['model_params']) if result['model_params'] else 0}")
            
        except Exception as e:
            print(f"  分析失败: {e}")
            results[model] = None
    
    return results

def comprehensive_regression_analysis():
    """综合回归分析"""
    print("\n" + "=" * 60)
    print("综合回归分析报告")
    print("=" * 60)
    
    df = load_iris_data()
    
    # 选择一个特征作为目标变量
    target_col = "sepal length (cm)"
    feature_cols = ['sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    
    models = ["linearregression", "ridge", "lasso"]
    
    results = {}
    
    for model in models:
        print(f"\n正在分析 {model}...")
        try:
            result = analyze_data(
                df=df,
                model=model,
                target_col=target_col,
                feature_cols=feature_cols,
                is_return_model_score=True,
                is_return_model_param=True
            )
            
            r2 = result['scores']['r2']
            mse = result['scores']['mse']
            results[model] = {
                'r2': r2,
                'mse': mse,
                'model_params_count': len(result['model_params'])
            }
            
            print(f"  R² 分数: {r2:.4f}")
            print(f"  均方误差: {mse:.4f}")
            print(f"  模型参数数量: {len(result['model_params'])}")
            
        except Exception as e:
            print(f"  分析失败: {e}")
            results[model] = None
    
    # 找出最佳模型（基于R²分数）
    valid_results = {k: v for k, v in results.items() if v is not None}
    if valid_results:
        best_model = max(valid_results, key=lambda x: valid_results[x]['r2'])
        print(f"\n🏆 最佳回归模型: {best_model}")
        print(f"   R² 分数: {valid_results[best_model]['r2']:.4f}")
        print(f"   均方误差: {valid_results[best_model]['mse']:.4f}")
    
    return results

def generate_summary_report(classification_results, clustering_results, dim_reduction_results, regression_results):
    """生成总结报告"""
    print("\n" + "=" * 60)
    print("数据分析总结报告")
    print("=" * 60)
    
    print("\n📊 分类模型性能:")
    valid_class_results = {k: v for k, v in classification_results.items() if v is not None}
    if valid_class_results:
        best_class_model = max(valid_class_results, key=lambda x: valid_class_results[x]['accuracy'])
        print(f"  最佳模型: {best_class_model} (准确率: {valid_class_results[best_class_model]['accuracy']:.4f})")
    
    print("\n🔍 聚类模型性能:")
    valid_cluster_results = {k: v for k, v in clustering_results.items() if v is not None and v['silhouette'] != 'N/A'}
    if valid_cluster_results:
        best_cluster_model = max(valid_cluster_results, key=lambda x: valid_cluster_results[x]['silhouette'])
        print(f"  最佳模型: {best_cluster_model} (轮廓系数: {valid_cluster_results[best_cluster_model]['silhouette']:.4f})")
    
    print("\n📈 回归模型性能:")
    valid_reg_results = {k: v for k, v in regression_results.items() if v is not None}
    if valid_reg_results:
        best_reg_model = max(valid_reg_results, key=lambda x: valid_reg_results[x]['r2'])
        print(f"  最佳模型: {best_reg_model} (R²: {valid_reg_results[best_reg_model]['r2']:.4f})")
    
    print("\n🧰 降维模型:")
    valid_dim_results = {k: v for k, v in dim_reduction_results.items() if v is not None}
    for model, result in valid_dim_results.items():
        print(f"  {model}: {result['original_shape']} → {result['reduced_shape']}")

def main():
    """主函数"""
    print("Iris 数据集综合分析")
    print("使用新的数据分析模块接口")
    
    try:
        # 执行各种分析
        classification_results = comprehensive_classification_analysis()
        clustering_results = comprehensive_clustering_analysis()
        dim_reduction_results = comprehensive_dimensionality_reduction_analysis()
        regression_results = comprehensive_regression_analysis()
        
        # 生成总结报告
        generate_summary_report(
            classification_results, 
            clustering_results, 
            dim_reduction_results, 
            regression_results
        )
        
        print("\n✅ 所有分析完成!")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()