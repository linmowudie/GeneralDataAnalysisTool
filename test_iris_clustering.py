import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Src.DataAnalyzer.AnalysisModule.analyzer import AnalyzeData
from Src.DataAnalyzer.VisualizationModule import DataVisualization

def test_iris_clustering():
    """测试鸢尾花数据集聚类分析和可视化"""
    # 读取鸢尾花数据集
    df = pd.read_csv('iris.csv')
    print("数据集信息:")
    print(df.head())
    print(f"数据集形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    
    # 移除目标列，因为我们进行的是无监督聚类
    feature_cols = [col for col in df.columns if col != 'target']
    features_df = df[feature_cols]
    print(f"特征列: {feature_cols}")
    
    # 进行KMeans聚类分析
    print("\n开始KMeans聚类分析...")
    analyzer = AnalyzeData(
        df=features_df,
        model="kmeans",
        is_return_model_predicting_set=True,
        is_return_model_score=True,
        is_split=False
    )
    
    # 手动设置聚类数
    analyzer.model_params = {"n_clusters": 3}
    
    result = analyzer.run()
    print("分析完成!")
    print(f"结果键值: {list(result.keys())}")
    print(f"任务类型: {result['task_type']}")
    
    # 准备可视化参数
    viz_params = {
        "task_type": result["task_type"],
        "model_name": "kmeans",
        "feature": features_df,
        "model_specific": {
            "trained_model": result["trained_model"]
        },
        "label_style": {
            "title": "Iris Dataset KMeans Clustering",
            "x": "Sepal Length (cm)",
            "y": "Sepal Width (cm)"
        },
        "shape_style": {
            "points": {
                "size": 50,
                "colors": ["tab:blue", "tab:orange", "tab:green"]
            }
        }
    }
    
    # 创建可视化对象并生成图表
    print("\n开始可视化...")
    visualizer = DataVisualization(viz_params)
    figures = visualizer.plot_chart()
    
    print(f"生成了 {len(figures)} 个图表:")
    for name, fig in figures.items():
        print(f"  - {name}: {fig}")
        
        # 保存图表到test_images文件夹
        fig.savefig(f'test_images/iris_{name}.png', dpi=300, bbox_inches='tight')
        print(f"    已保存为 test_images/iris_{name}.png")
    
    # 显示图表（可选）
    print("\n显示图表...")
    for name, fig in figures.items():
        fig.show()
    
    print("聚类分析和可视化完成!")
    return figures

if __name__ == "__main__":
    figures = test_iris_clustering()
    
    # 保持图表打开
    plt.show()