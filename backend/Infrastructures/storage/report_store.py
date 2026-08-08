"""
backend/Infrastructures/storage/report_store.py
ReportStore：报告存储（首版 html，pdf/excel 预留）
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .temp_storage import PROJECT_ROOT

logger = logging.getLogger(__name__)


class ReportStore:
    """报告落盘：ReportOutput/{report_id}.html"""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or (PROJECT_ROOT / "ReportOutput")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.base_dir / "_index.json"

    def _load_index(self) -> Dict[str, Dict]:
        if self._index_path.exists():
            try:
                with open(self._index_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_index(self, index: Dict[str, Dict]) -> None:
        with open(self._index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def save_report(self, report_id: str, content: str, fmt: str = "html",
                    session_id: Optional[str] = None) -> Path:
        """落盘报告，返回文件路径"""
        suffix = fmt if fmt in ("html", "pdf", "xlsx") else "html"
        path = self.base_dir / f"{report_id}.{suffix}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        index = self._load_index()
        index[report_id] = {
            "session_id": session_id,
            "format": suffix,
            "path": str(path),
        }
        self._save_index(index)
        logger.info("ReportStore: 报告已保存 %s", path)
        return path

    def load_report(self, report_id: str, fmt: str = "html") -> Optional[bytes]:
        """供导出端点返回"""
        path = self.base_dir / f"{report_id}.{fmt}"
        if not path.exists():
            # 回退查找任意格式
            for p in self.base_dir.glob(f"{report_id}.*"):
                path = p
                break
            else:
                return None
        return path.read_bytes()

    def list_reports(self, session_id: Optional[str] = None) -> List[Dict]:
        """报告列表"""
        index = self._load_index()
        reports = []
        for report_id, meta in index.items():
            if session_id and meta.get("session_id") != session_id:
                continue
            reports.append({"report_id": report_id, **meta})
        return reports


# 全局单例
report_store = ReportStore()
