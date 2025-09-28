"""
配置管理模块

该模块提供对项目中各种配置文件的统一管理功能。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

# 获取配置文件目录
CONFIG_DIR = Path(__file__).parent

def load_model_config() -> Dict[str, Any]:
    """
    加载模型配置文件
    
    :return: 模型配置字典
    """
    config_path = CONFIG_DIR / 'model_config.json'
    
    if not config_path.exists():
        raise FileNotFoundError(f"模型配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 将嵌套配置扁平化处理，方便直接通过模型名称获取配置
    flat_config = {}
    for category, models in config.items():
        for model_name, model_info in models.items():
            flat_config[model_name] = model_info
    
    return flat_config

def load_database_config() -> Dict[str, Any]:
    """
    加载数据库配置文件
    
    :return: 数据库配置字典
    """
    config_path = CONFIG_DIR / 'database_config.json'
    
    if not config_path.exists():
        raise FileNotFoundError(f"数据库配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config

def load_model_mapping_config() -> Dict[str, Any]:
    """
    加载模型映射配置文件
    
    :return: 模型映射配置字典
    """
    config_path = CONFIG_DIR / 'model_mapping_config.json'
    
    if not config_path.exists():
        raise FileNotFoundError(f"模型映射配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config

# 加载模型配置
MODEL_CONFIG: Dict[str, Dict[str, Any]] = load_model_config()

# 加载数据库配置
DATABASE_CONFIG: Dict[str, Dict[str, Any]] = load_database_config()

# 加载模型映射配置
MODEL_MAPPING_CONFIG: Dict[str, Dict[str, Any]] = load_model_mapping_config()