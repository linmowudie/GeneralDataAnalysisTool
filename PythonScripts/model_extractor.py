#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型提取脚本
用于转移自动保存的模型并管理模型数量

该脚本负责将自动保存的模型转移到用户提取目录，
并监控自动保存目录中的模型数量，防止溢出。
"""

import os
import sys
import argparse
import pickle
import json
from pathlib import Path
import shutil
from typing import Dict, Any, Optional
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))


def manage_auto_saved_models(auto_save_dir: Path, max_models: int = 5):
    """
    管理自动保存目录中的模型数量，当模型数量超过指定数量时删除最早的模型文件
    
    :param auto_save_dir: 自动保存目录路径
    :param max_models: 最大模型文件数量
    """
    # 确保目录存在
    auto_save_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有模型文件（按修改时间排序）
    model_files = []
    for file_path in auto_save_dir.iterdir():
        if file_path.is_file() and file_path.suffix in ['.pkl', '.pickle']:
            model_files.append((file_path, file_path.stat().st_mtime))
    
    # 按修改时间排序（最早的在前）
    model_files.sort(key=lambda x: x[1])
    
    # 如果文件数量超过限制，删除最早的文件
    removed_files = []
    while len(model_files) > max_models:
        oldest_file, _ = model_files.pop(0)
        try:
            oldest_file.unlink()
            removed_files.append(oldest_file.name)
            print(f"已删除旧的自动保存模型文件: {oldest_file.name}")
        except Exception as e:
            print(f"删除旧模型文件失败 {oldest_file.name}: {e}")
    
    return removed_files


def transfer_model(auto_save_dir: Path, user_extract_dir: Path, model_name: str = ""):
    """
    将自动保存的模型转移到用户提取目录
    
    :param auto_save_dir: 自动保存目录路径
    :param user_extract_dir: 用户提取目录路径
    :param model_name: 指定要转移的模型文件名，如果为None则转移最新的模型
    :return: 转移是否成功
    """
    # 确保目录存在
    auto_save_dir.mkdir(parents=True, exist_ok=True)
    user_extract_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有模型文件（按修改时间排序）
    model_files = []
    for file_path in auto_save_dir.iterdir():
        if file_path.is_file() and file_path.suffix in ['.pkl', '.pickle']:
            model_files.append((file_path, file_path.stat().st_mtime))
    
    # 按修改时间排序（最新的在前）
    model_files.sort(key=lambda x: x[1], reverse=True)
    
    if not model_files:
        print("自动保存目录中没有模型文件")
        return False
    
    # 选择要转移的模型
    if model_name:
        selected_model = None
        for file_path, _ in model_files:
            if file_path.name == model_name:
                selected_model = file_path
                break
        if not selected_model:
            print(f"未找到指定的模型文件: {model_name}")
            return False
    else:
        # 默认转移最新的模型
        selected_model = model_files[0][0]
    
    # 转移模型文件
    try:
        destination = user_extract_dir / selected_model.name
        shutil.move(str(selected_model), str(destination))
        print(f"模型已从自动保存目录转移至用户提取目录: {selected_model.name}")
        return True
    except Exception as e:
        print(f"转移模型文件失败: {e}")
        return False


def main():
    """
    主函数 - 处理模型转移和管理请求
    """
    parser = argparse.ArgumentParser(description='模型提取和管理工具')
    parser.add_argument('--transfer', nargs='?', const='latest', metavar='MODEL_NAME',
                       help='转移自动保存的模型到用户提取目录，可以指定模型文件名，不指定则转移最新的')
    parser.add_argument('--manage', action='store_true',
                       help='管理自动保存目录中的模型数量（默认保留最新的5个）')
    parser.add_argument('--max-models', type=int, default=5,
                       help='自动保存目录中最大模型文件数量（默认: 5）')
    
    args = parser.parse_args()
    
    # 定义目录路径
    project_root = Path(__file__).parent.parent
    auto_save_dir = project_root / "ModelOutput" / "自动保存"
    user_extract_dir = project_root / "ModelOutput" / "用户提取"
    
    # 如果没有指定任何操作，则显示帮助信息
    if not any([args.transfer, args.manage]):
        parser.print_help()
        return 0
    
    # 转移模型
    if args.transfer:
        if args.transfer == 'latest':
            transfer_model(auto_save_dir, user_extract_dir)
        else:
            transfer_model(auto_save_dir, user_extract_dir, args.transfer)
    
    # 管理自动保存目录中的模型数量
    if args.manage:
        removed_files = manage_auto_saved_models(auto_save_dir, args.max_models)
        if not removed_files:
            print(f"自动保存目录中的模型数量未超过 {args.max_models} 个，无需删除")
    
    print("操作完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())