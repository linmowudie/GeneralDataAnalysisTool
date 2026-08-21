"""
backend/Services/workflows/manual_workflow.py
ManualWorkflow：手动工作流（步骤顺序执行）

execute_step：
1. 校验步骤顺序与锁状态（锁状态检查优先，抛 StepLocked / WorkflowOrderError）
2. 从部件注册表取部件执行
3. 产物写入 context.artifacts 并落 temp_storage
4. 推进状态机（标记完成；import/cleaning/analysis 完成后按现有语义自动锁定）
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import (  # noqa: E402
    Artifact, StepName, StepLocked, WorkflowOrderError,
)
from backend.Services.components.base_component import BaseComponent  # noqa: E402
from backend.Services.components import (  # noqa: E402
    ImportComponent, PreviewComponent, CleaningComponent,
    AnalysisComponent, VisualizationComponent, ReportingComponent,
)

logger = logging.getLogger(__name__)


class ManualWorkflow:
    """手动工作流：按步骤调度部件执行"""

    def __init__(self):
        self._components: Dict[StepName, BaseComponent] = {
            StepName.IMPORT: ImportComponent(),
            StepName.PREVIEW: PreviewComponent(),
            StepName.CLEANING: CleaningComponent(),
            StepName.ANALYSIS: AnalysisComponent(),
            StepName.VISUALIZATION: VisualizationComponent(),
            StepName.REPORT: ReportingComponent(),
        }
        # 前置完成条件（满足任一集合即可执行；空列表表示无前置要求）
        self._preconditions: Dict[StepName, List[Set[StepName]]] = {
            StepName.IMPORT: [],
            StepName.PREVIEW: [{StepName.IMPORT}],
            StepName.CLEANING: [{StepName.IMPORT}],
            StepName.ANALYSIS: [{StepName.CLEANING}, {StepName.IMPORT}],
            StepName.VISUALIZATION: [{StepName.ANALYSIS}],
            StepName.REPORT: [{StepName.ANALYSIS}],
        }
        # 完成后自动锁定的步骤（与现 api 语义一致）
        self._auto_lock: Set[StepName] = {
            StepName.IMPORT, StepName.CLEANING, StepName.ANALYSIS,
        }

    # ------------------------------------------------------------------ 执行
    def execute_step(self, context, step: StepName, params: Optional[Dict[str, Any]] = None) -> Artifact:
        """执行指定步骤并返回产物"""
        params = params or {}

        # 1. 校验锁状态
        if context.steps.is_locked(step):
            raise StepLocked(f"步骤 {step.value} 已锁定，无法执行")

        # 校验步骤顺序（前置完成条件）
        self._check_order(context, step)

        # 2. 取部件执行
        component = self._components.get(step)
        if component is None:
            raise WorkflowOrderError(f"未知的步骤: {step.value}")

        logger.info("ManualWorkflow[%s]: 执行步骤 %s", context.session_id, step.value)
        artifact = component.execute(context, params)

        # 3. 产物写入 context（内部同步落 temp_storage）
        context.set_artifact(artifact)

        # 4. 推进状态机
        context.steps.complete(step)
        if step in self._auto_lock:
            context.steps.lock(step)
        context.touch()

        return artifact

    # ------------------------------------------------------------------ 内部
    def _check_order(self, context, step: StepName) -> None:
        """校验前置步骤是否满足（任一集合全部完成即可）"""
        required_groups = self._preconditions.get(step)
        if not required_groups:
            return

        for group in required_groups:
            if all(context.steps.is_completed(s) for s in group):
                return
        expected = " 或 ".join(
            " + ".join(s.value for s in group) for group in required_groups
        )
        raise WorkflowOrderError(f"步骤 {step.value} 的前置步骤未完成（需先完成：{expected}）")
