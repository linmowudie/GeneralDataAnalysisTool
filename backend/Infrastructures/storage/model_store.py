"""
backend/Infrastructures/storage/model_store.py
ModelStore：模型文件存储

承接原 api/model_extractor.py 的文件操作职责：
save_model / list_models / transfer_model / manage
"""

from __future__ import annotations

import pickle
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from .temp_storage import PROJECT_ROOT

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """模型文件元信息"""
    name: str
    size: int
    modified: float


class ModelStore:
    """模型文件存储（ModelOutput/自动保存、ModelOutput/用户提取）"""

    def __init__(self, base_dir: Optional[Path] = None):
        base = base_dir or (PROJECT_ROOT / "ModelOutput")
        self.auto_dir = base / "自动保存"
        self.user_extract_dir = base / "用户提取"
        self.auto_dir.mkdir(parents=True, exist_ok=True)
        self.user_extract_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- 保存
    def save_model(self, model: Any, name: Optional[str] = None, auto_dir: bool = True) -> str:
        """保存模型，返回模型存储键（文件名）"""
        if model is None:
            raise ValueError("模型实例为空，无法保存")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = name or getattr(model, "__class__", type(model)).__name__
        filename = f"{model_name}_{timestamp}.pkl"
        target_dir = self.auto_dir if auto_dir else self.user_extract_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / filename
        with open(path, "wb") as f:
            pickle.dump(model, f)
        logger.info("ModelStore: 模型已保存 %s", path)
        return filename

    # ---------------------------------------------------------------- 列表
    def list_models(self) -> List[ModelInfo]:
        """列出自动保存目录中的模型（最新在前）"""
        models: List[ModelInfo] = []
        for file_path in self.auto_dir.iterdir():
            if file_path.is_file() and file_path.suffix in (".pkl", ".pickle"):
                stat = file_path.stat()
                models.append(ModelInfo(name=file_path.name, size=stat.st_size, modified=stat.st_mtime))
        models.sort(key=lambda m: m.modified, reverse=True)
        return models

    # ---------------------------------------------------------------- 转移
    def transfer_model(self, name: Optional[str] = None, target_dir: Optional[Path] = None) -> bool:
        """将自动保存的模型转移到目标目录（默认用户提取目录）"""
        import shutil

        dest_dir = target_dir or self.user_extract_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        models = self.list_models()
        if not models:
            logger.warning("ModelStore: 自动保存目录中没有模型文件")
            return False

        selected = None
        if name:
            for m in models:
                if m.name == name:
                    selected = m
                    break
            if selected is None:
                logger.warning("ModelStore: 未找到指定模型 %s", name)
                return False
        else:
            selected = models[0]  # 最新的

        try:
            shutil.move(str(self.auto_dir / selected.name), str(dest_dir / selected.name))
            logger.info("ModelStore: 模型已转移 %s -> %s", selected.name, dest_dir)
            return True
        except Exception as e:
            logger.error("ModelStore: 模型转移失败 %s", e)
            return False

    # ---------------------------------------------------------------- 管理
    def manage(self, max_models: int = 5) -> List[str]:
        """超限清理最旧模型，返回被删除的文件名列表"""
        models = sorted(self.list_models(), key=lambda m: m.modified)  # 最旧在前
        removed: List[str] = []
        while len(models) > max_models:
            oldest = models.pop(0)
            try:
                (self.auto_dir / oldest.name).unlink()
                removed.append(oldest.name)
                logger.info("ModelStore: 已删除旧模型 %s", oldest.name)
            except Exception as e:
                logger.warning("ModelStore: 删除旧模型失败 %s: %s", oldest.name, e)
        return removed


# 全局单例
model_store = ModelStore()
