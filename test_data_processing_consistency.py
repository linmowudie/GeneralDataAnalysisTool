# -*- coding: utf-8 -*-
"""
测试数据处理流程的一致性
确保在数据清洗和分析过程中训练集和测试集的样本保持一致
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score

# 添加项目路径到系统路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入项目核心引擎
from Src.DataAnalyzer.core import DataProcessingEngine

def main():
    """主函数 - 测试数据处理流程的一致性"""
    print("开始测试数据处理流程的一致性")
    
    try:
        # 创建数据处理引擎实例
        engine = DataProcessingEngine()
        
        # 1. 数据导入阶段
        print("\n=== 数据导入阶段 ===")
        import_params = {
            "resource_path": os.path.join(project_root, "Data", "breast_cancer.csv"),
            "resource_type": "csv"
        }
        engine.import_data(**import_params)
        print(f"数据导入成功，数据形状: {engine.imported_data.shape}")
        
        # 将target_name列重命名为target，以测试字符串编码功能
        engine.imported_data = engine.imported_data.drop(columns=['target'])
        engine.imported_data = engine.imported_data.rename(columns={'target_name': 'target'})
        print(f"重命名目标列后，数据形状: {engine.imported_data.shape}")
        print(f"目标列类型: {engine.imported_data['target'].dtype}")
        print(f"目标列唯一值: {engine.imported_data['target'].unique()}")
        
        # 2. 数据清洗阶段
        print("\n=== 数据清洗阶段 ===")
        clean_params = {
            "select_mode": "standard",
            "params_list": [],
            "target_col": "target"  # 传递目标列信息
        }
        engine.clean_data(**clean_params)
        print(f"数据清洗完成，清洗后数据形状: {engine.cleaned_data.shape}")
        print(f"清洗后目标列类型: {engine.cleaned_data['target'].dtype}")
        print(f"清洗后目标列唯一值: {engine.cleaned_data['target'].unique()}")
        
        # 3. 数据分析阶段
        print("\n=== 数据分析阶段 ===")
        analyze_params = {
            "model": "logisticregression",
            "target_col": "target",
            "is_split": True,
            "split_ratio": 0.7,  # 70%用于训练，30%用于测试
            "is_return_model_score": True,
            "is_return_model_predicting_set": True,
            "is_return_training_set": True,
            "random_state": 42
        }
        engine.analyze_data(**analyze_params)
        print("数据分析完成")
        
        if engine.analyzed_data and 'model_score' in engine.analyzed_data:
            print(f"模型准确率: {engine.analyzed_data['model_score']['accuracy']:.4f}")
        
        # 检查数据一致性
        print("\n=== 数据一致性检查 ===")
        analyzed_data = engine.analyzed_data
        
        # 检查训练集和测试集
        if 'X_train' in analyzed_data and analyzed_data['X_train'] is not None:
            print(f"训练集特征形状: {analyzed_data['X_train'].shape}")
        if 'y_train' in analyzed_data and analyzed_data['y_train'] is not None:
            print(f"训练集目标形状: {analyzed_data['y_train'].shape}")
        if 'X_test' in analyzed_data and analyzed_data['X_test'] is not None:
            print(f"测试集特征形状: {analyzed_data['X_test'].shape}")
        if 'y_test' in analyzed_data and analyzed_data['y_test'] is not None:
            print(f"测试集目标形状: {analyzed_data['y_test'].shape}")
        if 'predictions' in analyzed_data and analyzed_data['predictions'] is not None:
            print(f"预测结果形状: {analyzed_data['predictions'].shape}")
        
        # 检查索引一致性
        if (analyzed_data['y_test'] is not None and 
            analyzed_data['predictions'] is not None):
            y_test = analyzed_data['y_test']
            predictions = analyzed_data['predictions']
            
            # 检查索引是否一致
            if isinstance(y_test, pd.Series) and isinstance(predictions, pd.Series):
                common_index = y_test.index.intersection(predictions.index)
                print(f"y_test和predictions的共同索引数量: {len(common_index)}")
                print(f"y_test索引数量: {len(y_test.index)}")
                print(f"predictions索引数量: {len(predictions.index)}")
                
                if len(common_index) == len(y_test.index) == len(predictions.index):
                    print("✓ 索引完全一致")
                else:
                    print("✗ 索引不一致")
            else:
                print("无法检查索引一致性")
        
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