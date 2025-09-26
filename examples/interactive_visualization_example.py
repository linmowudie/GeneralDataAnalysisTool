"""
examples/interactive_visualization_example.py
交互式可视化功能示例

该脚本演示如何使用新增的交互式可视化功能。
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from Src.DataAnalyzer.core import DataProcessingEngine

def linear_regression_interactive_example():
    """线性回归交互式可视化示例"""
    print("线性回归交互式可视化示例")
    
    # 生成示例数据
    np.random.seed(42)
    X = np.random.randn(100, 1) * 10
    y = 2 * X.squeeze() + 3 + np.random.randn(100) * 5
    
    # 创建DataFrame
    df = pd.DataFrame({'feature': X.squeeze(), 'target': y})
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    # 模拟导入数据
    engine.imported_data = df
    
    # 数据清洗
    engine.cleaned_data = df
    
    # 模拟分析数据
    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)
    
    engine.analyzed_data = {
        'trained_model': model,
        'X_train': pd.DataFrame(X, columns=['feature']),
        'y_train': pd.Series(y, name='target'),
        'predictions': pd.Series(predictions, name='predictions'),
        'task_type': 'regression'
    }
    
    # 交互式可视化
    param_dict = {
        "task_type": "regression",
        "model_name": "linearregression",
        "feature": pd.DataFrame(X, columns=['feature']),
        "target": pd.Series(y, name='target'),
        "predict": pd.Series(predictions, name='predictions'),
        "interactive": True  # 启用交互式可视化
    }
    
    engine.visualize_data(param_dict)
    
    # 显示图表信息
    if engine.visualized_plot:
        print(f"生成了 {len(engine.visualized_plot)} 个交互式图表:")
        for name, fig in engine.visualized_plot.items():
            print(f"  - {name}")
    else:
        print("未生成任何图表")

def kmeans_interactive_example():
    """KMeans聚类交互式可视化示例"""
    print("\nKMeans聚类交互式可视化示例")
    
    # 生成示例数据
    np.random.seed(42)
    X = np.random.randn(150, 4)
    
    # 创建DataFrame
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    # 模拟导入数据
    engine.imported_data = df
    
    # 数据清洗
    engine.cleaned_data = df
    
    # 模拟分析数据
    model = KMeans(n_clusters=3, random_state=42)
    model.fit(X)
    
    engine.analyzed_data = {
        'trained_model': model,
        'X_train': df,
        'task_type': 'clustering'
    }
    
    # 交互式可视化
    param_dict = {
        "task_type": "clustering",
        "model_name": "kmeans",
        "feature": df,
        "model_specific": {
            "trained_model": model
        },
        "interactive": True  # 启用交互式可视化
    }
    
    engine.visualize_data(param_dict)
    
    # 显示图表信息
    if engine.visualized_plot:
        print(f"生成了 {len(engine.visualized_plot)} 个交互式图表:")
        for name, fig in engine.visualized_plot.items():
            print(f"  - {name}")
    else:
        print("未生成任何图表")

def three_d_interactive_example():
    """3D交互式可视化示例"""
    print("\n3D交互式可视化示例")
    
    # 生成示例数据
    np.random.seed(42)
    X = np.random.randn(100, 3)
    
    # 创建DataFrame
    df = pd.DataFrame(X, columns=['x', 'y', 'z'])
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    # 模拟导入数据
    engine.imported_data = df
    
    # 数据清洗
    engine.cleaned_data = df
    
    # 3D可视化参数
    param_dict = {
        "task_type": "transformer",
        "model_name": "3d",
        "feature": df,
        "interactive": True  # 启用交互式可视化
    }
    
    engine.visualize_data(param_dict)
    
    # 显示图表信息
    if engine.visualized_plot:
        print(f"生成了 {len(engine.visualized_plot)} 个交互式图表:")
        for name, fig in engine.visualized_plot.items():
            print(f"  - {name}")
    else:
        print("未生成任何图表")

if __name__ == "__main__":
    print("=== 数据分析工具交互式可视化功能演示 ===")
    
    # 运行示例
    linear_regression_interactive_example()
    kmeans_interactive_example()
    three_d_interactive_example()
    
    print("\n=== 演示完成 ===")
    print("\n要查看交互式图表，请运行:")
    print("python examples/interactive_visualization_example.py")
    print("\n然后在生成的图表中点击查看交互功能，如:")
    print("- 鼠标悬停查看数据点信息")
    print("- 拖拽旋转3D图表")
    print("- 缩放图表")
    print("- 选择/取消选择数据系列")