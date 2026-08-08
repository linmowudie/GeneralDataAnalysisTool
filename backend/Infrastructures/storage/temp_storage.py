"""
backend/Infrastructures/storage/temp_storage.py
TempStorage：会话级临时存储

目录布局：TempStorage/{session_id}/{stage}.pkl
产物布局：TempStorage/{session_id}/artifacts/{step}.pkl
"""

from __future__ import annotations

import pickle
import shutil
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# 项目根目录（backend 的上一级）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class TempStorage:
    """会话级临时存储，支持断点续跑"""

    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            self.base_path = PROJECT_ROOT / "TempStorage"
        else:
            p = Path(base_path)
            self.base_path = p if p.is_absolute() else PROJECT_ROOT / p
        self.base_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ 路径
    def _session_dir(self, session_id: str) -> Path:
        return self.base_path / session_id

    def _stage_path(self, session_id: str, stage: str) -> Path:
        return self._session_dir(session_id) / f"{stage}.pkl"

    def _artifact_path(self, session_id: str, step: str) -> Path:
        return self._session_dir(session_id) / "artifacts" / f"{step}.pkl"

    # ------------------------------------------------------------ DataFrame
    def save_dataframe(self, df: pd.DataFrame, session_id: str, stage: str) -> str:
        """按会话+阶段落 pkl，返回存储键"""
        path = self._stage_path(session_id, stage)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(df, f)
        logger.debug("TempStorage: 保存 DataFrame session=%s stage=%s", session_id, stage)
        return f"{session_id}/{stage}"

    def load_dataframe(self, session_id: str, stage: str) -> Optional[pd.DataFrame]:
        """读取指定会话+阶段的 DataFrame"""
        path = self._stage_path(session_id, stage)
        if not path.exists():
            return None
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning("TempStorage: 加载失败 session=%s stage=%s err=%s", session_id, stage, e)
            return None

    # ------------------------------------------------------------- Artifact
    def save_artifact(self, session_id: str, artifact: Any) -> str:
        """产物持久化（断点续跑）"""
        step = getattr(artifact, "step", "unknown")
        step_value = getattr(step, "value", str(step))
        path = self._artifact_path(session_id, step_value)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(artifact, f)
        return f"{session_id}/artifacts/{step_value}"

    def load_artifact(self, session_id: str, step: str) -> Optional[Any]:
        step_value = getattr(step, "value", str(step))
        path = self._artifact_path(session_id, step_value)
        if not path.exists():
            return None
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning("TempStorage: 加载产物失败 session=%s step=%s err=%s", session_id, step_value, e)
            return None

    # ---------------------------------------------------------------- 清理
    def clear_stage(self, session_id: str, stage: str) -> Dict[str, int]:
        """清理单阶段"""
        stats = {"files_removed": 0, "space_freed": 0}
        path = self._stage_path(session_id, stage)
        if path.exists():
            stats["space_freed"] += path.stat().st_size
            path.unlink()
            stats["files_removed"] += 1
        return stats

    def clear_session(self, session_id: str) -> Dict[str, int]:
        """清理会话全部"""
        stats = {"files_removed": 0, "space_freed": 0}
        session_dir = self._session_dir(session_id)
        if session_dir.exists():
            for f in session_dir.rglob("*"):
                if f.is_file():
                    stats["files_removed"] += 1
                    stats["space_freed"] += f.stat().st_size
            shutil.rmtree(session_dir, ignore_errors=True)
        return stats

    def clear_stage_globally(self, stage: str) -> Dict[str, int]:
        """跨会话清理指定阶段（供 /api/cleanup/run-step 使用）"""
        stats = {"files_removed": 0, "space_freed": 0}
        if not self.base_path.exists():
            return stats
        for session_dir in self.base_path.iterdir():
            if not session_dir.is_dir():
                continue
            path = session_dir / f"{stage}.pkl"
            if path.exists():
                stats["space_freed"] += path.stat().st_size
                path.unlink()
                stats["files_removed"] += 1
        return stats

    def clear_all(self) -> Dict[str, int]:
        """启动时全清"""
        stats = {"files_removed": 0, "space_freed": 0}
        if self.base_path.exists():
            for item in self.base_path.iterdir():
                if item.is_dir():
                    for f in item.rglob("*"):
                        if f.is_file():
                            stats["files_removed"] += 1
                            stats["space_freed"] += f.stat().st_size
                    shutil.rmtree(item, ignore_errors=True)
        logger.info("TempStorage: 全量清理完成 %s", stats)
        return stats


# 全局单例
temp_storage = TempStorage()
