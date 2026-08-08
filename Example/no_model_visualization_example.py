"""
无模型可视化功能示例

该示例演示了如何使用新增的无模型可视化功能，
支持散点图、折线图、柱状图等各种基本图表类型。
"""

import pandas as pd
import numpy as np
from backend.Models.visualization import DataVisualization

def main():
    # 创建示例数据
    np.random.seed(42)
    data = {
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'z': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    }
    df = pd.DataFrame(data)
    
    # 示例1: 散点图
    print("生成散点图...")
    scatter_params = {
        'task_type': 'transformer',
        'model_name': 'no_model',
        'chart_type': 'scatter',
        'feature': df[['x', 'y']],
        'target': df['z'],
        'label_style': {
            'title': '示例散点图',
            'x': 'X轴',
            'y': 'Y轴'
        }
    }
    
    scatter_visualizer = DataVisualization(scatter_params)
    scatter_figures = scatter_visualizer.plot_chart()
    print(f"生成了 {len(scatter_figures)} 个散点图")
    
    # 示例2: 折线图
    print("生成折线图...")
    line_data = pd.DataFrame({
        'series1': np.cumsum(np.random.randn(50)),
        'series2': np.cumsum(np.random.randn(50)),
        'series3': np.cumsum(np.random.randn(50))
    })
    
    line_params = {
        'task_type': 'transformer',
        'model_name': 'no_model',
        'chart_type': 'line',
        'feature': line_data,
        'label_style': {
            'title': '示例折线图'
        }
    }
    
    line_visualizer = DataVisualization(line_params)
    line_figures = line_visualizer.plot_chart()
    print(f"生成了 {len(line_figures)} 个折线图")
    
    # 示例3: 柱状图
    print("生成柱状图...")
    bar_params = {
        'task_type': 'transformer',
        'model_name': 'no_model',
        'chart_type': 'bar',
        'feature': df[['x', 'y', 'z']],
        'label_style': {
            'title': '示例柱状图'
        }
    }
    
    bar_visualizer = DataVisualization(bar_params)
    bar_figures = bar_visualizer.plot_chart()
    print(f"生成了 {len(bar_figures)} 个柱状图")
    
    # 示例4: 交互式散点图
    print("生成交互式散点图...")
    interactive_scatter_params = {
        'task_type': 'transformer',
        'model_name': 'no_model',
        'chart_type': 'scatter',
        'feature': df[['x', 'y']],
        'target': df['z'],
        'interactive': True,
        'label_style': {
            'title': '交互式散点图示例'
        }
    }
    
    interactive_scatter_visualizer = DataVisualization(interactive_scatter_params)
    interactive_scatter_figures = interactive_scatter_visualizer.plot_chart()
    print(f"生成了 {len(interactive_scatter_figures)} 个交互式散点图")
    
    print("所有示例运行完成！")

if __name__ == "__main__":
    main()