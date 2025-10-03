"""
examples/extended_interactive_visualization_example.py
扩展交互式可视化功能示例

该脚本演示如何使用新增的交互式可视化功能。
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from Src.DataAnalyzer.core import DataProcessingEngine

def decision_tree_interactive_example():
    """决策树分类器交互式可视化示例"""
    print("决策树分类器交互式可视化示例")
    
    # 生成示例数据
    np.random.seed(42)
    X = np.random.randn(100, 4)
    y = (X[:, 0] + X[:, 1] + np.random.randn(100) * 0.5 > 0).astype(int)
    
    # 创建DataFrame
    feature_names = [f'feature_{i}' for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    # 模拟导入数据
    engine.imported_data = df
    
    # 数据清洗
    engine.cleaned_data = df
    
    # 模拟分析数据
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X, y)
    
    engine.analyzed_data = {
        'trained_model': model,
        'X_train': pd.DataFrame(X, columns=feature_names),
        'y_train': pd.Series(y, name='target'),
        'task_type': 'classification'
    }
    
    # 交互式可视化
    param_dict = {
        "task_type": "classification",
        "model_name": "decisiontreeclassifier",
        "feature": pd.DataFrame(X, columns=feature_names),
        "target": pd.Series(y, name='target'),
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

def time_series_interactive_example():
    """时间序列交互式可视化示例"""
    print("\n时间序列交互式可视化示例")
    
    # 生成示例时间序列数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    values1 = np.cumsum(np.random.randn(100)) + 100
    values2 = np.cumsum(np.random.randn(100)) + 80
    
    # 创建DataFrame
    df = pd.DataFrame({
        'date': dates,
        'series1': values1,
        'series2': values2
    })
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    # 模拟导入数据
    engine.imported_data = df
    
    # 数据清洗
    engine.cleaned_data = df
    
    # 时间序列可视化参数
    param_dict = {
        "task_type": "transformer",
        "model_name": "timeseries",
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

def feature_importance_interactive_example():
    """特征重要性交互式可视化示例"""
    print("\n特征重要性交互式可视化示例")
    
    # 生成示例特征重要性数据
    np.random.seed(42)
    feature_names = [f'feature_{i}' for i in range(10)]
    importances = np.abs(np.random.randn(10))
    importances = importances / np.sum(importances)  # 归一化
    
    # 创建DataFrame
    df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    })
    
    # 创建数据处理引擎
    engine = DataProcessingEngine()
    
    # 模拟导入数据
    engine.imported_data = df
    
    # 数据清洗
    engine.cleaned_data = df
    
    # 特征重要性可视化参数
    param_dict = {
        "task_type": "analysis",
        "model_name": "featureimportance",
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
    print("=== 数据分析工具扩展交互式可视化功能演示 ===")
    
    # 运行示例
    decision_tree_interactive_example()
    time_series_interactive_example()
    feature_importance_interactive_example()
    
    print("\n=== 演示完成 ===")
    print("\n要查看交互式图表，请运行:")
    print("python examples/extended_interactive_visualization_example.py")
    print("\n然后在生成的图表中点击查看交互功能，如:")
    print("- 鼠标悬停查看数据点信息")
    print("- 拖拽旋转3D图表")
    print("- 缩放图表")
    print("- 选择/取消选择数据系列")
    print("- 使用范围选择器选择时间范围")