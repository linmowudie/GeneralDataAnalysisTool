"""
backend/Interfaces/web/utils.py
Web 层工具：示例数据 / dataclass-Agent 契约 -> JSON 字典
"""

from __future__ import annotations

import dataclasses
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd


def sample_iris_df() -> pd.DataFrame:
    """与原 api 一致的示例数据（预览/可视化兜底）"""
    data = {
        "sepal_length": [5.1, 4.9, 4.7, 4.6, 5.0],
        "sepal_width": [3.5, 3.0, 3.2, 3.1, 3.6],
        "petal_length": [1.4, 1.4, 1.3, 1.5, 1.4],
        "petal_width": [0.2, 0.2, 0.2, 0.2, 0.2],
        "species": ["setosa", "setosa", "setosa", "setosa", "setosa"],
    }
    return pd.DataFrame(data)


def sample_regression_df() -> pd.DataFrame:
    """可视化兜底示例（与原 api 一致）"""
    return pd.DataFrame({
        "x": [1, 2, 3, 4, 5],
        "y": [2, 4, 6, 8, 10],
        "category": ["A", "B", "A", "B", "A"],
    })


def to_jsonable(obj: Any) -> Any:
    """dataclass / Enum / datetime 递归转 JSON 可序列化结构（Agent 契约出参用）"""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_jsonable(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(item) for item in obj]
    return obj
