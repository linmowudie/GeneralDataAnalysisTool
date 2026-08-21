"""
配置加载工具
"""

import json
from typing import Dict, Any


def load_config(config_file: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    参数:
        config_file (str): 配置文件路径
        
    返回:
        Dict[str, Any]: 配置信息字典
        
    异常:
        FileNotFoundError: 配置文件不存在
        json.JSONDecodeError: 配置文件格式错误
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"配置文件 {config_file} 加载成功")
        return config
    except FileNotFoundError:
        print(f"配置文件 {config_file} 不存在")
        raise
    except json.JSONDecodeError:
        print(f"配置文件 {config_file} 格式错误")
        raise