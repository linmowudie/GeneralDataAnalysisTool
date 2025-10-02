#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据预览脚本
用于从临时存储中获取数据并显示前几行，方便用户查看数据结构
"""

import sys
import os
import json
import pandas as pd
import pickle
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Src.DataAnalyzer.TempStorage.manager import TempStorageManager


def preview_data(limit: int = 5) -> dict:
    """
    预览临时存储中的数据
    
    Parameters:
    -----------
    limit : int, default 5
        要显示的行数
        
    Returns:
    --------
    dict
        包含数据预览信息的字典
    """
    try:
        # 初始化临时存储管理器
        storage_manager = TempStorageManager()
        
        # 检查是否有存储的数据
        files = []
        for stage in ['imported', 'cleaned', 'analyzed', 'visualized']:
            stage_path = getattr(storage_manager, f"{stage}_path")
            if stage_path.exists():
                for file_path in stage_path.iterdir():
                    if file_path.is_file():
                        files.append((file_path, stage))
        
        if not files:
            return {
                "success": False,
                "message": "临时存储中没有数据，请先导入数据"
            }
        
        # 获取最新的数据文件
        files.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)
        latest_file, stage = files[0]
        
        # 读取数据
        if latest_file.suffix == '.parquet':
            df = pd.read_parquet(latest_file)
        elif latest_file.suffix == '.pkl':
            with open(latest_file, 'rb') as f:
                df = pickle.load(f)
        else:
            return {
                "success": False,
                "message": f"不支持的文件格式: {latest_file}"
            }
        
        # 确保是DataFrame
        if not isinstance(df, pd.DataFrame):
            return {
                "success": False,
                "message": "存储的数据不是DataFrame格式"
            }
        
        # 获取前几行数据
        preview_df = df.head(limit)
        
        # 转换为字典格式
        result = {
            "success": True,
            "file_name": latest_file.name,
            "file_path": str(latest_file),
            "stage": stage,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "preview_data": preview_df.to_dict(orient='records')
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"数据预览失败: {str(e)}"
        }


def main():
    """主函数"""
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print("参数必须是整数")
            sys.exit(1)
    else:
        limit = 5
    
    result = preview_data(limit)
    
    # 以JSON格式输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()