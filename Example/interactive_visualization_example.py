"""
Example/interactive_visualization_example.py
交互式可视化功能示例

该脚本演示如何使用 Models 层的可视化分发器（DataVisualization）生成交互式图表。
（原 DataProcessingEngine 已删除；可视化能力现由
 backend.Models.visualization.DataVisualization 提供）
"""

import sys
import os

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

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


def linear_regression_interactive_example():
    """线性回归交互式可视化示例"""
    print("线性回归交互式可视化示例")

    # 生成示例数据
    np.random.seed(42)
    X = np.random.randn(100, 1) * 10
    y = 2 * X.squeeze() + 3 + np.random.randn(100) * 5

    # 训练模型并预测
    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)

    # 交互式可视化参数
    param_dict = {
        "task_type": "regression",
        "model_name": "linearregression",
        "feature": pd.DataFrame(X, columns=['feature']),
        "target": pd.Series(y, name='target'),
        "predict": pd.Series(predictions, name='predictions'),
        "interactive": True  # 启用交互式可视化
    }

    plots = DataVisualization(param_dict).plot_chart()
    show_charts(plots)


def kmeans_interactive_example():
    """KMeans聚类交互式可视化示例"""
    print("\nKMeans聚类交互式可视化示例")

    # 生成示例数据
    np.random.seed(42)
    X = np.random.randn(150, 4)

    # 创建DataFrame
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])

    # 训练模型
    model = KMeans(n_clusters=3, random_state=42)
    model.fit(X)

    # 交互式可视化参数
    param_dict = {
        "task_type": "clustering",
        "model_name": "kmeans",
        "feature": df,
        "model_specific": {
            "trained_model": model
        },
        "interactive": True  # 启用交互式可视化
    }

    plots = DataVisualization(param_dict).plot_chart()
    show_charts(plots)


def three_d_interactive_example():
    """3D交互式可视化示例"""
    print("\n3D交互式可视化示例")

    # 生成示例数据
    np.random.seed(42)
    X = np.random.randn(100, 3)

    # 创建DataFrame
    df = pd.DataFrame(X, columns=['x', 'y', 'z'])

    # 3D可视化参数
    param_dict = {
        "task_type": "transformer",
        "model_name": "3d",
        "feature": df,
        "interactive": True  # 启用交互式可视化
    }

    plots = DataVisualization(param_dict).plot_chart()
    show_charts(plots)


if __name__ == "__main__":
    print("=== 数据分析工具交互式可视化功能演示 ===")

    # 运行示例
    linear_regression_interactive_example()
    kmeans_interactive_example()
    three_d_interactive_example()

    print("\n=== 演示完成 ===")
    print("\n要查看交互式图表，请运行:")
    print("python Example/interactive_visualization_example.py")
    print("\n然后在生成的图表中点击查看交互功能，如:")
    print("- 鼠标悬停查看数据点信息")
    print("- 拖拽旋转3D图表")
    print("- 缩放图表")
    print("- 选择/取消选择数据系列")
