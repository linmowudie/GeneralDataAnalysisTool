#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型提取脚本
用于从数据分析结果中提取训练好的模型并保存

该脚本提供命令行接口，允许用户指定数据文件、分析模型和参数，
然后执行完整的数据分析流程，并将训练好的模型保存到指定位置。
"""

import os
import sys
import argparse
import pickle
import json
from pathlib import Path
import pandas as pd
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

from Src.DataAnalyzer.core import DataProcessingEngine


def save_model(model, output_path, format_type="pickle"):
    """
    保存训练好的模型
    
    :param model: 训练好的模型对象
    :param output_path: 输出路径
    :param format_type: 保存格式 ("pickle" 或 "json")
    """
    output_path = Path(output_path)
    
    if format_type == "pickle":
        with open(output_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"模型已保存为 Pickle 格式: {output_path}")
    elif format_type == "json":
        # 注意：不是所有模型都支持直接 JSON 序列化
        try:
            model_params = model.get_params()
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(model_params, f, indent=2, ensure_ascii=False)
            print(f"模型参数已保存为 JSON 格式: {output_path}")
        except Exception as e:
            print(f"模型不支持 JSON 序列化: {e}")
            print("尝试保存为 Pickle 格式...")
            with open(output_path.with_suffix('.pkl'), 'wb') as f:
                pickle.dump(model, f)
            print(f"模型已保存为 Pickle 格式: {output_path.with_suffix('.pkl')}")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='模型提取工具')
    parser.add_argument('input_file', help='输入数据文件路径')
    parser.add_argument('-m', '--model', required=True, help='机器学习模型名称')
    parser.add_argument('-o', '--output', required=True, help='输出模型文件路径')
    parser.add_argument('--target-col', help='目标列名')
    parser.add_argument('--feature-cols', nargs='*', help='特征列名列表')
    parser.add_argument('--format', choices=['pickle', 'json'], default='pickle', 
                       help='输出格式 (默认: pickle)')
    parser.add_argument('--split-ratio', type=float, default=0.8, 
                       help='训练集比例 (默认: 0.8)')
    parser.add_argument('--random-state', type=int, default=42, 
                       help='随机种子 (默认: 42)')
    
    # 模型特定参数
    parser.add_argument('--model-params', type=str, 
                       help='模型参数 (JSON格式字符串)')
    
    args = parser.parse_args()
    
    try:
        # 创建数据处理引擎
        engine = DataProcessingEngine()
        
        # 确定文件类型
        input_path = Path(args.input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {args.input_file}")
        
        file_extension = input_path.suffix.lower()
        if file_extension == '.csv':
            resource_type = 'csv'
        elif file_extension in ['.xlsx', '.xls']:
            resource_type = 'excel'
        elif file_extension == '.json':
            resource_type = 'json'
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
        
        # 导入数据
        print(f"正在导入数据: {args.input_file}")
        engine.import_data(args.input_file, resource_type)
        
        # 数据清洗（使用标准模式）
        print("正在清洗数据...")
        engine.clean_data('standard', [])
        
        # 解析模型参数
        model_params: Optional[Dict[str, Any]] = None
        if args.model_params:
            try:
                model_params = json.loads(args.model_params)
            except json.JSONDecodeError as e:
                print(f"模型参数解析错误: {e}")
                return 1
        
        # 数据分析
        print(f"正在训练模型: {args.model}")
        # 明确声明返回类型为 Dict[str, Any]
        result = engine.analyze_data(
            model=args.model,
            target_col=args.target_col,
            feature_cols=args.feature_cols,
            split_ratio=args.split_ratio,
            random_state=args.random_state,
            model_params=model_params,
            is_return_model_param=True,
            is_return_model_score=True
        )
        
        # 确保结果不是 None
        if result is None:
            print("错误: 数据分析返回了空结果")
            return 1
            
        # 提取训练好的模型
        trained_model = result.get('trained_model')
        if trained_model is None:
            print("错误: 未能获取训练好的模型")
            return 1
        
        # 显示模型信息
        print(f"模型类型: {type(trained_model).__name__}")
        scores = result.get('scores')
        if scores is not None and isinstance(scores, dict):
            print("模型评分:")
            for metric, score in scores.items():
                print(f"  {metric}: {score}")
        model_params_result = result.get('model_params')
        if model_params_result is not None and isinstance(model_params_result, dict):
            print("模型参数:")
            params_items = list(model_params_result.items())
            for param, value in params_items[:5]:  # 只显示前5个
                print(f"  {param}: {value}")
            if len(params_items) > 5:
                print(f"  ... (还有 {len(params_items) - 5} 个参数)")
        
        # 保存模型
        save_model(trained_model, args.output, args.format)
        
        print("模型提取完成！")
        return 0
        
    except Exception as e:
        print(f"模型提取过程中发生错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())