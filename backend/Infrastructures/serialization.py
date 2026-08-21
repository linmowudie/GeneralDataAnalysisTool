"""
backend/Infrastructures/serialization.py
Serializer：统一 JSON 安全序列化（修复原 data_analysis.py 中 np 未导入 Bug）

单一入口 make_serializable(data)
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def _is_json_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, bool)) or value is None


def make_serializable(data: Any) -> Any:
    """
    将任意分析结果转换为 JSON 可序列化结构

    - DataFrame -> records 列表
    - Series -> list
    - ndarray -> list
    - numpy 标量 -> 原生类型
    - 模型实例/sklearn 对象 -> 类名字符串
    - NaN/Inf -> None
    - dict/list 递归处理
    """
    # DataFrame
    if isinstance(data, pd.DataFrame):
        return make_serializable(data.to_dict(orient="records"))

    # Series
    if isinstance(data, pd.Series):
        return make_serializable(data.to_list())

    # ndarray
    if isinstance(data, np.ndarray):
        return make_serializable(data.tolist())

    # numpy 标量
    if isinstance(data, (np.integer,)):
        return int(data)
    if isinstance(data, (np.floating,)):
        value = float(data)
        return None if (math.isnan(value) or math.isinf(value)) else value
    if isinstance(data, (np.bool_,)):
        return bool(data)

    # 浮点 NaN/Inf
    if isinstance(data, float):
        return None if (math.isnan(data) or math.isinf(data)) else data

    # dict 递归（None 值转空对象，与原前端契约保持一致）
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # 跳过训练好的模型实例，转为类名
            if key == "trained_model":
                if value is not None:
                    result["trained_model"] = type(value).__name__
                continue
            if value is None:
                result[str(key)] = {}
            else:
                result[str(key)] = make_serializable(value)
        return result

    # list/tuple 递归
    if isinstance(data, (list, tuple, set)):
        return [make_serializable(item) for item in data]

    # JSON 原生类型直接返回
    if _is_json_scalar(data):
        return data

    # 其他对象（模型实例等）转类名
    if hasattr(data, "__class__") and not isinstance(data, type):
        return type(data).__name__

    return str(data)


class Serializer:
    """统一序列化入口（命名空间封装）"""

    @staticmethod
    def serialize(data: Any) -> Any:
        return make_serializable(data)
