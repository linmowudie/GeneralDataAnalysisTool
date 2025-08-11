import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

# 获取项目根目录（tests 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录插入到 sys.path 最前面
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 导入需要测试的模块
from Src.data_analyzer.data_visualization import DataVisualization
from Src.data_analyzer.analysis.analyzer import AnalyzeData
from Src.data_analyzer.visualization.registry import plot_registry

def create_test_data():
    """创建用于测试的数据"""
    np.random.seed(42)
    
    # 创建回归测试数据
    regression_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'target': np.random.randn(100)
    }
    # 让目标变量与特征有一定关系
    regression_data['target'] = regression_data['feature1'] * 2 + regression_data['feature2'] * -1.5 + np.random.randn(100) * 0.5
    regression_df = pd.DataFrame(regression_data)
    
    # 创建分类测试数据
    classification_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
        'target': np.random.randint(0, 2, 100)
    }
    classification_df = pd.DataFrame(classification_data)
    
    # 创建聚类测试数据
    clustering_data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100)
    }
    clustering_df = pd.DataFrame(clustering_data)
    
    return regression_df, classification_df, clustering_df

def test_linear_regression_visualization():
    """测试线性回归可视化"""
    print("测试线性回归可视化:")
    print(f"注册表内容: {list(plot_registry._registry.keys())}")
    regression_df, _, _ = create_test_data()
    
    # 先进行分析获取必要参数
    analyzer = AnalyzeData(
        df=regression_df,
        model="linearregression",
        target_col="target",
        feature_cols=["feature1", "feature2", "feature3"],
        is_return_model_predicting_set=True,
        is_return_model_score=True,
        is_split=False  # 不分割数据集
    )
    result = analyzer.run()
    
    # 构造可视化参数
    viz_params = {
        "task_type": result["task_type"],
        "model_name": "linearregression",
        "feature": regression_df[["feature1", "feature2", "feature3"]],
        "target": regression_df["target"],
        "predict": result["predictions"] if result["predictions"] is not None else regression_df["target"],
        "label_style": {
            "x": "真实值",
            "y": "预测值",
            "title": "线性回归结果"
        },
        "shape_style": {
            "points": {
                "size": 40,
                "colors": ["blue"]
            }
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    try:
        figures = visualizer.plot_chart()
        print(f"生成了 {len(figures)} 个图表")
        for name, fig in figures.items():
            print(f"  - {name}: {fig}")
        print("✅ 线性回归可视化测试通过\n")
        plt.close('all')  # 关闭所有图表以释放内存
        return True
    except Exception as e:
        print(f"❌ 线性回归可视化测试失败: {str(e)}\n")
        return False

def test_logistic_regression_visualization():
    """测试逻辑回归可视化"""
    print("测试逻辑回归可视化:")
    print(f"注册表内容: {list(plot_registry._registry.keys())}")
    _, classification_df, _ = create_test_data()
    
    # 先进行分析获取必要参数
    analyzer = AnalyzeData(
        df=classification_df,
        model="logisticregression",
        target_col="target",
        feature_cols=["feature1", "feature2", "feature3"],
        is_return_model_predicting_set=True,
        is_return_model_score=True,
        is_split=False  # 不分割数据集
    )
    result = analyzer.run()
    
    # 为逻辑回归创建概率预测值
    # 由于逻辑回归输出的是分类结果，我们需要构造一些概率值用于ROC曲线
    np.random.seed(42)
    y_score = np.random.rand(len(classification_df))
    
    # 构造可视化参数
    viz_params = {
        "task_type": result["task_type"],
        "model_name": "logisticregression",
        "feature": classification_df[["feature1", "feature2", "feature3"]],
        "target": classification_df["target"],
        "predict": result["predictions"] if result["predictions"] is not None else classification_df["target"],
        "model_specific": {
            "trained_model": result["trained_model"],
            "y_score": y_score
        },
        "label_style": {
            "title": "逻辑回归结果"
        },
        "shape_style": {
            "points": {
                "colors": ["tab:blue"]
            }
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    try:
        figures = visualizer.plot_chart()
        print(f"生成了 {len(figures)} 个图表")
        for name, fig in figures.items():
            print(f"  - {name}: {fig}")
        print("✅ 逻辑回归可视化测试通过\n")
        plt.close('all')  # 关闭所有图表以释放内存
        return True
    except Exception as e:
        print(f"❌ 逻辑回归可视化测试失败: {str(e)}\n")
        return False

def test_kmeans_visualization():
    """测试KMeans聚类可视化"""
    print("测试KMeans聚类可视化:")
    print(f"注册表内容: {list(plot_registry._registry.keys())}")
    _, _, clustering_df = create_test_data()
    
    # 先进行分析获取必要参数
    analyzer = AnalyzeData(
        df=clustering_df,
        model="kmeans",
        is_return_model_predicting_set=True,
        is_return_model_score=True,
        is_split=False  # 不分割数据集
    )
    result = analyzer.run()
    
    # 构造可视化参数
    viz_params = {
        "task_type": result["task_type"],
        "model_name": "kmeans",
        "feature": clustering_df[["feature1", "feature2", "feature3"]],
        "model_specific": {
            "trained_model": result["trained_model"]
        },
        "label_style": {
            "title": "KMeans聚类结果",
            "x": "特征1",
            "y": "特征2"
        },
        "shape_style": {
            "points": {
                "size": 40,
                "colors": ["tab:blue", "tab:orange", "tab:green"]
            }
        }
    }
    
    # 创建可视化对象并生成图表
    visualizer = DataVisualization(viz_params)
    try:
        figures = visualizer.plot_chart()
        print(f"生成了 {len(figures)} 个图表")
        for name, fig in figures.items():
            print(f"  - {name}: {fig}")
        print("✅ KMeans聚类可视化测试通过\n")
        plt.close('all')  # 关闭所有图表以释放内存
        return True
    except Exception as e:
        print(f"❌ KMeans聚类可视化测试失败: {str(e)}\n")
        return False

def test_missing_parameters():
    """测试缺少必要参数的情况"""
    print("测试缺少必要参数的情况:")
    
    # 构造缺少必要参数的可视化参数
    viz_params = {
        "model_name": "linearregression",
        "feature": pd.DataFrame({"x": [1, 2, 3]})
    }
    
    # 创建可视化对象并尝试生成图表
    visualizer = DataVisualization(viz_params)
    try:
        figures = visualizer.plot_chart()
        print("❌ 缺少必要参数测试失败 - 应该抛出异常\n")
        return False
    except ValueError as e:
        print(f"✅ 缺少必要参数测试通过 - 正确捕获异常: {str(e)}\n")
        return True
    except Exception as e:
        print(f"❌ 缺少必要参数测试失败 - 意外异常: {str(e)}\n")
        return False

def test_unsupported_model():
    """测试不支持的模型"""
    print("测试不支持的模型:")
    regression_df, _, _ = create_test_data()
    
    # 构造可视化参数
    viz_params = {
        "task_type": "regression",
        "model_name": "unsupported_model",
        "feature": regression_df[["feature1", "feature2", "feature3"]],
        "target": regression_df["target"],
        "predict": regression_df["target"]  # 简单使用目标值作为预测值
    }
    
    # 创建可视化对象并尝试生成图表
    visualizer = DataVisualization(viz_params)
    try:
        figures = visualizer.plot_chart()
        print("❌ 不支持的模型测试失败 - 应该抛出异常\n")
        return False
    except NotImplementedError as e:
        print(f"✅ 不支持的模型测试通过 - 正确捕获异常: {str(e)}\n")
        return True
    except Exception as e:
        print(f"❌ 不支持的模型测试失败 - 意外异常: {str(e)}\n")
        return False

# 测试代码
if __name__ == "__main__":
    print("开始测试 data_visualization 模块\n")
    print("="*50 + "\n")
    
    # 运行各种测试
    test_results = []
    test_results.append(test_linear_regression_visualization())
    test_results.append(test_logistic_regression_visualization())
    test_results.append(test_kmeans_visualization())
    test_results.append(test_missing_parameters())
    test_results.append(test_unsupported_model())
    
    print("="*50)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    print(f"测试完成: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过!")
    else:
        print("❌ 部分测试失败!")