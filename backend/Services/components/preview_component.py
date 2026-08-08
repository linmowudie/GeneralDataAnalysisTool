"""
backend/Services/components/preview_component.py
PreviewComponent：数据预览部件（前置依赖 import）
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Any, Dict, List

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import PreviewArtifact, StepName, WorkflowOrderError  # noqa: E402
from backend.Services.components.base_component import BaseComponent  # noqa: E402

logger = logging.getLogger(__name__)


class PreviewComponent(BaseComponent):
    """数据预览部件"""

    name = StepName.PREVIEW
    required_inputs: List[StepName] = [StepName.IMPORT]

    def execute(self, context, params: Dict[str, Any]) -> PreviewArtifact:
        head_n = params.get("head_n", 10)

        storage = self._storage(context)
        df = storage.load_dataframe(self._session(context), "imported")
        if df is None:
            raise WorkflowOrderError("没有可预览的数据，请先导入数据")

        head_records = df.head(head_n).to_dict(orient="records")
        dataset_info = {
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "columns": list(df.columns),
            "data_types": {col: str(df[col].dtype) for col in df.columns},
        }

        artifact = PreviewArtifact(
            step=StepName.PREVIEW,
            head_records=head_records,
            dataset_info=dataset_info,
        )
        logger.info("PreviewComponent: 预览完成 rows=%s", len(df))
        return artifact
