"""
backend/Services/components/reporting_component.py
ReportingComponent：数据报表部件（前置依赖 analysis + visualization）

首版落盘 html（pdf/excel 预留）。
"""

from __future__ import annotations

import sys
import uuid
import pickle
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import ReportArtifact, StepName, ReportType  # noqa: E402
from backend.Services.components.base_component import BaseComponent  # noqa: E402
from backend.Infrastructures.storage import report_store  # noqa: E402

logger = logging.getLogger(__name__)


class ReportingComponent(BaseComponent):
    """数据报表部件"""

    name = StepName.REPORT
    required_inputs: List[StepName] = [StepName.ANALYSIS, StepName.VISUALIZATION]

    def execute(self, context, params: Dict[str, Any]) -> ReportArtifact:
        storage = self._storage(context)
        session_id = self._session(context)
        report_type = params.get("report_type", ReportType.FULL.value)

        analyzed_data = self._load_pickle(storage, session_id, "analyzed") or {}
        visualized = self._load_pickle(storage, session_id, "visualized") or {}

        # 调用报告组装模型（backend.Models.reporting）
        try:
            from backend.Models.reporting import Report

            generator = Report(
                model_params=analyzed_data.get("model_params"),
                model_scores=analyzed_data.get("model_score"),
                visualizations=visualized,
                model_predictions=analyzed_data.get("predictions"),
            )
            content = generator.return_report()
        except Exception as e:
            logger.warning("ReportingComponent: 报告组装失败，使用空内容 %s", e)
            content = {}

        report_id = f"report_{session_id[:8]}_{uuid.uuid4().hex[:8]}"
        html = self._render_html(report_id, report_type, content)
        file_path = report_store.save_report(report_id, html, fmt="html", session_id=session_id)

        artifact = ReportArtifact(
            step=StepName.REPORT,
            report_id=report_id,
            content=content,
            file_path=str(file_path),
        )
        logger.info("ReportingComponent: 报告生成完成 id=%s", report_id)
        return artifact

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _load_pickle(storage, session_id: str, stage: str) -> Optional[Any]:
        path = storage._stage_path(session_id, stage)
        if not path.exists():
            return None
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning("ReportingComponent: 加载 %s 失败 %s", stage, e)
            return None

    @staticmethod
    def _render_html(report_id: str, report_type: str, content: Dict[str, Any]) -> str:
        """将报告内容渲染为简单 HTML（首版）"""
        sections = []
        for key, value in (content or {}).items():
            sections.append(f"<h2>{key}</h2><pre>{value}</pre>")
        body = "\n".join(sections) if sections else "<p>无报告内容</p>"
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>{report_id}</title></head><body>"
            f"<h1>数据分析报告（{report_type}）</h1>{body}</body></html>"
        )
