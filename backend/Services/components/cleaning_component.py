"""
backend/Services/components/cleaning_component.py
CleaningComponent：数据清洗部件（前置依赖 import）
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Any, Dict, List

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import CleanedArtifact, StepName, WorkflowOrderError, ComponentExecutionError  # noqa: E402
from backend.Services.components.base_component import BaseComponent  # noqa: E402

logger = logging.getLogger(__name__)


class CleaningComponent(BaseComponent):
    """数据清洗部件"""

    name = StepName.CLEANING
    required_inputs: List[StepName] = [StepName.IMPORT]

    def execute(self, context, params: Dict[str, Any]) -> CleanedArtifact:
        select_mode = params.get("select_mode", "standard")
        params_list = params.get("params_list", []) or []
        is_freedom_params = params.get("is_freedom_params", False)
        target_col = params.get("target_col")

        storage = self._storage(context)
        df = storage.load_dataframe(self._session(context), "imported")
        if df is None:
            raise WorkflowOrderError("没有可清洗的数据，请先导入数据")

        try:
            # 调用清洗模型（backend.Models.cleaning）
            from backend.Models.cleaning import CleanDataMode

            cleaner = CleanDataMode(
                df,
                select_mode,
                params_list,
                is_freedom_params,
                target_col,
            )
            cleaned_df = cleaner.clean_data()
        except Exception as e:
            logger.error("CleaningComponent: 清洗失败 %s", e, exc_info=True)
            raise ComponentExecutionError(f"数据清洗失败: {str(e)}") from e

        storage_key = storage.save_dataframe(cleaned_df, self._session(context), "cleaned")

        artifact = CleanedArtifact(
            step=StepName.CLEANING,
            storage_key=storage_key,
            shape=cleaned_df.shape,
            columns=list(cleaned_df.columns),
            target_col=target_col,
            clean_summary={
                "select_mode": select_mode,
                "rows_before": int(len(df)),
                "rows_after": int(len(cleaned_df)),
            },
        )
        logger.info("CleaningComponent: 清洗完成 shape=%s", cleaned_df.shape)
        return artifact
