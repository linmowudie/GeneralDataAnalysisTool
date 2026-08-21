"""
Example/extended_interactive_visualization_example.py
扩展交互式可视化功能示例

该脚本演示如何使用 Models 层的可视化分发器（DataVisualization）生成
决策树、时间序列、特征重要性等交互式图表。
（原 DataProcessingEngine 已删除；可视化能力现由
 backend.Models.visualization.DataVisualization 提供）
"""

import sys
import os

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录添加到系统路径
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.Models.visualization import DataVisualization


def show_charts(plots):
    """显示图表信息"""
    if plots:
        print(f"生成了 {len(plots)} 个交互式图表:")
        for name in plots.keys():
            print(f"  - {name}")
    else:
        print("未生成任何图表")


def decision_tree_interactive_example():
    """决策树分类器交互式可视化示例"""
    print("决策树分类器交互式可视化示例")

    # 生成示例数据
    np.random.seed(42)
    X = np.random.randn(100, 4)
    y = (X[:, 0] + X[:, 1] + np.random.randn(100) * 0.5 > 0).astype(int)

    # 创建DataFrame
    feature_names = [f'feature_{i}' for i in range(X.shape[1])]

    # 训练模型并预测
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X, y)
    predictions = model.predict(X)

    # 交互式可视化参数
    param_dict = {
        "task_type": "classification",
        "model_name": "decisiontreeclassifier",
        "feature": pd.DataFrame(X, columns=feature_names),
        "target": pd.Series(y, name='target'),
        "predict": pd.Series(predictions, name='predictions'),
        "interactive": True  # 启用交互式可视化
    }

    plots = DataVisualization(param_dict).plot_chart()
    show_charts(plots)


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

    # 时间序列可视化参数
    param_dict = {
        "task_type": "transformer",
        "model_name": "timeseries",
        "feature": df,
        "interactive": True  # 启用交互式可视化
    }

    plots = DataVisualization(param_dict).plot_chart()
    show_charts(plots)


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

    # 特征重要性可视化参数
    param_dict = {
        "task_type": "analysis",
        "model_name": "featureimportance",
        "feature": df,
        "interactive": True  # 启用交互式可视化
    }

    plots = DataVisualization(param_dict).plot_chart()
    show_charts(plots)


if __name__ == "__main__":
    print("=== 数据分析工具扩展交互式可视化功能演示 ===")

    # 运行示例
    decision_tree_interactive_example()
    time_series_interactive_example()
    feature_importance_interactive_example()

    print("\n=== 演示完成 ===")
    print("\n要查看交互式图表，请运行:")
    print("python Example/extended_interactive_visualization_example.py")
    print("\n然后在生成的图表中点击查看交互功能，如:")
    print("- 鼠标悬停查看数据点信息")
    print("- 拖拽旋转3D图表")
    print("- 缩放图表")
    print("- 选择/取消选择数据系列")
    print("- 使用范围选择器选择时间范围")
