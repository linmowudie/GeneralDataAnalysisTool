# -*- coding: utf-8 -*-
"""
测试可视化模块的数据一致性处理功能
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加项目路径到系统路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入项目核心引擎
from Src.DataAnalyzer.core import DataProcessingEngine

def main():
    """主函数 - 测试可视化模块的数据一致性处理"""
    print("开始测试可视化模块的数据一致性处理功能")
    
    try:
        # 创建数据处理引擎实例
        engine = DataProcessingEngine()
        
        # 1. 数据导入阶段
        print("\n=== 数据导入阶段 ===")
        import_params = {
            "resource_path": os.path.join(project_root, "Data", "iris.csv"),
            "resource_type": "csv"
        }
        engine.import_data(**import_params)
        print(f"数据导入成功，数据形状: {engine.imported_data.shape}")
        
        # 2. 数据清洗阶段
        print("\n=== 数据清洗阶段 ===")
        clean_params = {
            "select_mode": "standard",
            "params_list": []
        }
        engine.clean_data(**clean_params)
        print(f"数据清洗完成，清洗后数据形状: {engine.cleaned_data.shape}")
        
        # 3. 数据分析阶段
        print("\n=== 数据分析阶段 ===")
        analyze_params = {
            "model": "logisticregression",
            "feature_cols": ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)'],
            "target_col": "target",
            "is_split": True,
            "split_ratio": 0.8,
            "is_return_model_score": True,
            "is_return_model_predicting_set": True,
            "is_return_training_set": True,
            "random_state": 42
        }
        engine.analyze_data(**analyze_params)
        print("数据分析完成")
        
        if engine.analyzed_data and 'model_score' in engine.analyzed_data:
            print(f"模型准确率: {engine.analyzed_data['model_score']['accuracy']:.4f}")
        
        # 4. 数据可视化阶段
        print("\n=== 数据可视化阶段 ===")
        engine.visualize_data()
        print("数据可视化完成")
        
        # 检查生成的图表
        if engine.visualized_plot:
            print(f"生成了 {len(engine.visualized_plot)} 个图表:")
            for name in engine.visualized_plot.keys():
                print(f"  - {name}")
        else:
            print("没有生成任何图表")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        if 'engine' in locals():
            engine.cleanup()

if __name__ == "__main__":
    main()