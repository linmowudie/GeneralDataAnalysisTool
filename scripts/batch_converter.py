#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量数据格式转换脚本
用于将一个目录下的所有支持的文件批量转换为其他格式
"""

import pandas as pd
import os
from pathlib import Path
import argparse
import sys

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

from scripts.data_converter import DataConverter


def batch_convert(input_dir, output_dir, target_formats):
    """
    批量转换数据格式
    
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :param target_formats: 目标格式列表
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 支持的输入格式
    supported_formats = ['.csv', '.xlsx', '.xls', '.json']
    
    # 获取所有支持的输入文件
    input_files = []
    for fmt in supported_formats:
        input_files.extend(input_path.glob(f'*{fmt}'))
    
    if not input_files:
        print(f"在目录 {input_dir} 中没有找到支持的文件")
        return
    
    print(f"找到 {len(input_files)} 个文件需要转换")
    
    # 转换每个文件
    for input_file in input_files:
        print(f"\n正在处理文件: {input_file.name}")
        try:
            # 创建转换器
            converter = DataConverter(input_file)
            
            # 获取基础文件名（不含扩展名）
            base_name = input_file.stem
            
            # 转换为目标格式
            for target_format in target_formats:
                output_file = output_path / f"{base_name}.{target_format}"
                
                if target_format == 'csv':
                    converter.to_csv(output_file)
                elif target_format == 'xlsx':
                    converter.to_excel(output_file)
                elif target_format == 'json':
                    converter.to_json(output_file)
                elif target_format == 'html':
                    converter.to_html(output_file)
                elif target_format == 'sqlite':
                    converter.to_sqlite(output_file, base_name)
                else:
                    print(f"警告: 不支持的目标格式 {target_format}")
        
        except Exception as e:
            print(f"处理文件 {input_file.name} 时发生错误: {e}")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='批量数据格式转换工具')
    parser.add_argument('input_dir', help='输入目录路径')
    parser.add_argument('output_dir', help='输出目录路径')
    parser.add_argument('-f', '--formats', nargs='+', 
                       choices=['csv', 'xlsx', 'json', 'html', 'sqlite'],
                       default=['csv'], 
                       help='目标格式列表 (默认: csv)')
    
    args = parser.parse_args()
    
    try:
        batch_convert(args.input_dir, args.output_dir, args.formats)
        print("\n批量数据转换完成！")
        
    except Exception as e:
        print(f"批量数据转换过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()