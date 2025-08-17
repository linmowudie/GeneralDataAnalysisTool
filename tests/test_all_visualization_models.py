# tests/test_all_visualization_models.py

import sys
import os
import pandas as pd
import numpy as np
import warnings

# 抑制可能的警告信息
warnings.filterwarnings("ignore")

# 获取项目根目录（tests 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 导入需要测试的模块
from Src.data_analyzer.data_visualization import DataVisualization

def create_test_datasets():
    """创建用于测试不同类型模型的数据集"""
    np.random.seed(42)
    
    # 创建分类数据
    classification_data = {
        'feature1': np.random.randn(50),
        'feature2': np.random.randn(50),
        'feature3': np.random.randn(50),
        'target': np.random.randint(0, 2, 50),  # 二分类目标
        'predict': np.random.randint(0, 2, 50)  # 二分类预测
    }
    classification_df = pd.DataFrame(classification_data)
    
    # 创建回归数据
    regression_data = {
        'feature1': np.random.randn(50),
        'feature2': np.random.randn(50),
        'feature3': np.random.randn(50),
        'target': np.random.randn(50) * 10 + 5,  # 连续目标
        'predict': np.random.randn(50) * 10 + 5  # 连续预测
    }
    regression_df = pd.DataFrame(regression_data)
    
    # 创建聚类数据
    clustering_data = {
        'feature1': np.random.randn(50),
        'feature2': np.random.randn(50),
        'feature3': np.random.randn(50),
    }
    clustering_df = pd.DataFrame(clustering_data)
    
    # 创建变换器数据
    transformer_data = {
        'feature1': np.random.randn(50),
        'feature2': np.random.randn(50),
        'feature3': np.random.randn(50),
    }
    transformer_df = pd.DataFrame(transformer_data)
    
    return classification_df, regression_df, clustering_df, transformer_df

def test_linear_regression_visualization():
    """测试线性回归可视化"""
    print("测试线性回归可视化:")
    
    _, regression_df, _, _ = create_test_datasets()
    
    # 构造参数字典
    viz_params = {
        "task_type": "regression",
        "model_name": "linearregression",
        "feature": regression_df[["feature1", "feature2", "feature3"]],
        "target": regression_df["target"],
        "predict": regression_df["predict"],
        "label_style": {
            "title": "线性回归结果",
            "x": "真实值",
            "y": "预测值"
        },
        "shape_style": {
            "points": {
                "size": 50,
                "colors": ["blue"]
            }
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    assert figures is not None, "应成功生成图表"
    assert len(figures) > 0, "应生成至少一个图表"
    assert "pred_vs_actual" in figures, "应包含真实值vs预测值图表"
    assert "residual_plot" in figures, "应包含残差图"
    
    print(f"线性回归可视化测试通过")
    print(f"- 生成图表数量: {len(figures)}")
    print(f"- 图表类型: {list(figures.keys())}")
    print("✅ 线性回归可视化测试通过\n")

def test_logistic_regression_visualization():
    """测试逻辑回归可视化"""
    print("测试逻辑回归可视化:")
    
    classification_df, _, _, _ = create_test_datasets()
    
    # 构造参数字典
    viz_params = {
        "task_type": "classification",
        "model_name": "logisticregression",
        "feature": classification_df[["feature1", "feature2", "feature3"]],
        "target": classification_df["target"],
        "predict": classification_df["predict"],
        "model_specific": {
            "y_score": np.random.rand(50)  # 模拟预测概率
        },
        "label_style": {
            "title": "逻辑回归结果"
        },
        "shape_style": {
            "points": {
                "colors": ["green"]
            }
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    assert figures is not None, "应成功生成图表"
    assert len(figures) >= 2, "应生成至少两个图表"
    assert "confusion_matrix" in figures, "应包含混淆矩阵图表"
    assert "roc_curve" in figures, "应包含ROC曲线图表"
    
    print(f"逻辑回归可视化测试通过")
    print(f"- 生成图表数量: {len(figures)}")
    print(f"- 图表类型: {list(figures.keys())}")
    print("✅ 逻辑回归可视化测试通过\n")

def test_decision_tree_visualization():
    """测试决策树分类器可视化"""
    print("测试决策树分类器可视化:")
    
    classification_df, _, _, _ = create_test_datasets()
    
    # 构造参数字典
    viz_params = {
        "task_type": "classification",
        "model_name": "decisiontreeclassifier",
        "feature": classification_df[["feature1", "feature2", "feature3"]],
        "target": classification_df["target"],
        "predict": classification_df["predict"],
        "label_style": {
            "title": "决策树分类结果"
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    assert figures is not None, "应成功生成图表"
    assert len(figures) >= 1, "应生成至少一个图表"
    assert "confusion_matrix" in figures, "应包含混淆矩阵图表"
    
    print(f"决策树分类器可视化测试通过")
    print(f"- 生成图表数量: {len(figures)}")
    print(f"- 图表类型: {list(figures.keys())}")
    print("✅ 决策树分类器可视化测试通过\n")

def test_kneighbors_visualization():
    """测试K近邻分类器可视化"""
    print("测试K近邻分类器可视化:")
    
    classification_df, _, _, _ = create_test_datasets()
    
    # 构造参数字典
    viz_params = {
        "task_type": "classification",
        "model_name": "kneighborsclassifier",
        "feature": classification_df[["feature1", "feature2"]],  # 仅使用两维特征用于决策边界
        "target": classification_df["target"],
        "predict": classification_df["predict"],
        "model_specific": {
            "y_score": np.random.rand(50)  # 模拟预测概率
        },
        "label_style": {
            "title": "K近邻分类结果"
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    assert figures is not None, "应成功生成图表"
    assert len(figures) >= 2, "应生成至少两个图表"
    assert "confusion_matrix" in figures, "应包含混淆矩阵图表"
    assert "roc_curve" in figures, "应包含ROC曲线图表"
    
    print(f"K近邻分类器可视化测试通过")
    print(f"- 生成图表数量: {len(figures)}")
    print(f"- 图表类型: {list(figures.keys())}")
    print("✅ K近邻分类器可视化测试通过\n")

def test_kmeans_visualization():
    """测试KMeans聚类可视化"""
    print("测试KMeans聚类可视化:")
    
    _, _, clustering_df, _ = create_test_datasets()
    
    # 构造参数字典
    viz_params = {
        "task_type": "clustering",
        "model_name": "kmeans",
        "feature": clustering_df[["feature1", "feature2", "feature3"]],
        "label_style": {
            "title": "KMeans聚类结果"
        },
        "shape_style": {
            "points": {
                "size": 50
            }
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    assert figures is not None, "应成功生成图表"
    assert len(figures) >= 1, "应生成至少一个图表"
    
    print(f"KMeans聚类可视化测试通过")
    print(f"- 生成图表数量: {len(figures)}")
    print(f"- 图表类型: {list(figures.keys())}")
    print("✅ KMeans聚类可视化测试通过\n")

def test_meanshift_visualization():
    """测试MeanShift聚类可视化"""
    print("测试MeanShift聚类可视化:")
    
    _, _, clustering_df, _ = create_test_datasets()
    
    # 构造参数字典
    viz_params = {
        "task_type": "clustering",
        "model_name": "meanshift",
        "feature": clustering_df[["feature1", "feature2", "feature3"]],
        "label_style": {
            "title": "MeanShift聚类结果"
        },
        "shape_style": {
            "points": {
                "size": 30
            }
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    assert figures is not None, "应成功生成图表"
    assert len(figures) >= 1, "应生成至少一个图表"
    
    print(f"MeanShift聚类可视化测试通过")
    print(f"- 生成图表数量: {len(figures)}")
    print(f"- 图表类型: {list(figures.keys())}")
    print("✅ MeanShift聚类可视化测试通过\n")

def test_pca_visualization():
    """测试PCA降维可视化"""
    print("测试PCA降维可视化:")
    
    _, _, _, transformer_df = create_test_datasets()
    
    # 构造参数字典
    viz_params = {
        "task_type": "transformer",
        "model_name": "pca",
        "feature": transformer_df[["feature1", "feature2", "feature3"]],
        "model_specific": {
            "explained_variance_ratio": np.random.rand(3)  # 模拟解释方差比率
        },
        "label_style": {
            "title": "PCA降维结果"
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    assert figures is not None, "应成功生成图表"
    
    print(f"PCA降维可视化测试通过")
    print(f"- 生成图表数量: {len(figures)}")
    print(f"- 图表类型: {list(figures.keys())}")
    print("✅ PCA降维可视化测试通过\n")

def test_standard_scaler_visualization():
    """测试StandardScaler标准化可视化"""
    print("测试StandardScaler标准化可视化:")
    
    _, _, _, transformer_df = create_test_datasets()
    
    # 构造参数字典
    viz_params = {
        "task_type": "transformer",
        "model_name": "standardscaler",
        "feature": transformer_df[["feature1", "feature2", "feature3"]],
        "model_specific": {
            "transformed": np.random.randn(50, 3)  # 模拟标准化后的数据
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    assert figures is not None, "应成功生成图表"
    
    print(f"StandardScaler标准化可视化测试通过")
    print(f"- 生成图表数量: {len(figures)}")
    print(f"- 图表类型: {list(figures.keys())}")
    print("✅ StandardScaler标准化可视化测试通过\n")

def test_visualization_comparison():
    """测试所有可视化模块的比较"""
    print("测试所有可视化模块比较:")
    
    classification_df, regression_df, clustering_df, transformer_df = create_test_datasets()
    
    # 定义所有支持的可视化模型及其配置
    visualization_configs = [
        {
            'name': 'linearregression',
            'type': 'regression',
            'data': {
                "task_type": "regression",
                "model_name": "linearregression",
                "feature": regression_df[["feature1", "feature2", "feature3"]],
                "target": regression_df["target"],
                "predict": regression_df["predict"]
            }
        },
        {
            'name': 'logisticregression',
            'type': 'classification',
            'data': {
                "task_type": "classification",
                "model_name": "logisticregression",
                "feature": classification_df[["feature1", "feature2", "feature3"]],
                "target": classification_df["target"],
                "predict": classification_df["predict"],
                "model_specific": {
                    "y_score": np.random.rand(50)
                }
            }
        },
        {
            'name': 'decisiontreeclassifier',
            'type': 'classification',
            'data': {
                "task_type": "classification",
                "model_name": "decisiontreeclassifier",
                "feature": classification_df[["feature1", "feature2", "feature3"]],
                "target": classification_df["target"],
                "predict": classification_df["predict"]
            }
        },
        {
            'name': 'kneighborsclassifier',
            'type': 'classification',
            'data': {
                "task_type": "classification",
                "model_name": "kneighborsclassifier",
                "feature": classification_df[["feature1", "feature2"]],
                "target": classification_df["target"],
                "predict": classification_df["predict"],
                "model_specific": {
                    "y_score": np.random.rand(50)
                }
            }
        },
        {
            'name': 'kmeans',
            'type': 'clustering',
            'data': {
                "task_type": "clustering",
                "model_name": "kmeans",
                "feature": clustering_df[["feature1", "feature2", "feature3"]]
            }
        },
        {
            'name': 'meanshift',
            'type': 'clustering',
            'data': {
                "task_type": "clustering",
                "model_name": "meanshift",
                "feature": clustering_df[["feature1", "feature2", "feature3"]]
            }
        },
        {
            'name': 'pca',
            'type': 'transformer',
            'data': {
                "task_type": "transformer",
                "model_name": "pca",
                "feature": transformer_df[["feature1", "feature2", "feature3"]],
                "model_specific": {
                    "explained_variance_ratio": np.random.rand(3)
                }
            }
        },
        {
            'name': 'standardscaler',
            'type': 'transformer',
            'data': {
                "task_type": "transformer",
                "model_name": "standardscaler",
                "feature": transformer_df[["feature1", "feature2", "feature3"]],
                "model_specific": {
                    "transformed": np.random.randn(50, 3)
                }
            }
        }
    ]
    
    results = {}
    
    for config in visualization_configs:
        model_name = config['name']
        viz_params = config['data']
        
        try:
            # 创建可视化对象并生成图表
            visualizer = DataVisualization(viz_params)
            figures = visualizer.plot_chart()
            
            # 保存结果
            results[model_name] = {
                'success': True,
                'figures_count': len(figures),
                'figure_types': list(figures.keys())
            }
            print(f"可视化模型 {model_name} 执行成功，生成 {len(figures)} 个图表")
            
        except Exception as e:
            results[model_name] = {
                'success': False,
                'error': str(e)
            }
            print(f"可视化模型 {model_name} 执行失败: {str(e)}")
    
    print("\n可视化模型比较结果:")
    for model_name, result in results.items():
        if result['success']:
            print(f"  {model_name}: 成功 (生成 {result['figures_count']} 个图表)")
            print(f"    图表类型: {result['figure_types']}")
        else:
            print(f"  {model_name}: 失败 ({result['error']})")
    
    print("✅ 可视化模型比较测试完成\n")

# 测试代码
if __name__ == "__main__":
    print("开始测试所有模型对应的可视化模块\n")
    print("="*60 + "\n")
    
    # 运行各种可视化测试
    test_linear_regression_visualization()
    test_logistic_regression_visualization()
    test_decision_tree_visualization()
    test_kneighbors_visualization()
    test_kmeans_visualization()
    test_meanshift_visualization()
    test_pca_visualization()
    test_standard_scaler_visualization()
    test_visualization_comparison()
    
    print("="*60)
    print("所有模型对应的可视化模块测试完成!")