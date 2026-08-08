"""
backend/Cores/agent/profiler.py
DataProfiler：数据画像

规则：全数值 + 有目标列 -> 回归/分类；无目标列 -> 聚类；高维 -> 建议降维。
Agent 部件只读 Artifact 与 ModelRegistry，不修改任何状态。
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import DataProfile, ColumnProfile, TaskType  # noqa: E402

logger = logging.getLogger(__name__)

# 高维阈值：特征列数超过该值建议降维
HIGH_DIM_THRESHOLD = 20


class DataProfiler:
    """数据画像器"""

    def profile(self, df: pd.DataFrame, target_col: Optional[str] = None) -> DataProfile:
        n_rows, n_cols = df.shape
        columns: List[ColumnProfile] = []
        numeric_cols = 0

        for col in df.columns:
            series = df[col]
            is_numeric = pd.api.types.is_numeric_dtype(series)
            if is_numeric:
                numeric_cols += 1
            columns.append(ColumnProfile(
                name=str(col),
                dtype=str(series.dtype),
                missing_rate=float(series.isna().mean()) if n_rows > 0 else 0.0,
                unique_count=int(series.nunique()),
                cardinality=int(series.nunique()),
                is_numeric=is_numeric,
            ))

        all_numeric = numeric_cols == n_cols and n_cols > 0
        inferred = self._infer_task_type(df, target_col, all_numeric, n_cols)

        try:
            memory_mb = float(df.memory_usage(deep=True).sum()) / (1024 * 1024)
        except Exception:
            memory_mb = 0.0

        profile = DataProfile(
            n_rows=int(n_rows),
            n_cols=int(n_cols),
            columns=columns,
            target_col=target_col,
            inferred_task_type=inferred,
            memory_mb=memory_mb,
        )
        logger.info("DataProfiler: rows=%s cols=%s task=%s", n_rows, n_cols, inferred.value)
        return profile

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _infer_task_type(df: pd.DataFrame, target_col: Optional[str],
                         all_numeric: bool, n_cols: int) -> TaskType:
        """任务类型推断规则"""
        # 高维优先建议降维
        if n_cols > HIGH_DIM_THRESHOLD:
            return TaskType.DIMENSIONALITY_REDUCTION

        # 无目标列 -> 聚类
        if not target_col or target_col not in df.columns:
            return TaskType.CLUSTERING

        # 有目标列：目标列取值基数决定回归/分类
        target = df[target_col]
        if pd.api.types.is_numeric_dtype(target):
            # 数值目标：唯一值较少视为分类，否则回归
            if target.nunique() <= 10:
                return TaskType.CLASSIFICATION
            return TaskType.REGRESSION
        # 非数值目标 -> 分类
        return TaskType.CLASSIFICATION
