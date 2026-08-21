"""
backend/Services/workflows/context.py
WorkflowContext + StepStateMachine

StepStateMachine 是锁状态与完成状态的唯一来源（消除 step_lock 与 core 步骤状态双轨）。
级联重置语义与原 reset_step_and_following 一致：重置某步骤时解锁并清空其后所有步骤
的 Artifact 与 temp_storage 数据。
"""

from __future__ import annotations

import sys
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import Artifact, StepName, STEP_ORDER  # noqa: E402
from backend.Infrastructures.storage import temp_storage  # noqa: E402

logger = logging.getLogger(__name__)

# StepName -> temp_storage 阶段键映射
_STAGE_MAP: Dict[StepName, str] = {
    StepName.IMPORT: "imported",
    StepName.PREVIEW: "imported",
    StepName.CLEANING: "cleaned",
    StepName.ANALYSIS: "analyzed",
    StepName.VISUALIZATION: "visualized",
    StepName.REPORT: "visualized",
}


class StepStateMachine:
    """步骤状态机（锁状态唯一来源）"""

    ORDER: List[StepName] = STEP_ORDER

    def __init__(self):
        self._completed: List[StepName] = []
        self._locked: List[StepName] = []

    # ---------------------------------------------------------------- 完成
    def complete(self, step: StepName) -> None:
        if step not in self._completed:
            self._completed.append(step)

    # ---------------------------------------------------------------- 锁定
    def lock(self, step: StepName) -> None:
        if step not in self._locked:
            self._locked.append(step)

    def unlock(self, step: StepName) -> None:
        if step in self._locked:
            self._locked.remove(step)

    def is_locked(self, step: StepName) -> bool:
        return step in self._locked

    def is_completed(self, step: StepName) -> bool:
        return step in self._completed

    # ---------------------------------------------------------------- 重置
    def reset_from(self, step: StepName) -> List[StepName]:
        """
        级联重置：从 step 起解锁并清除完成状态，返回被重置的步骤列表。
        """
        if step not in self.ORDER:
            return []
        index = self.ORDER.index(step)
        steps_to_reset = self.ORDER[index:]

        self._locked = [s for s in self._locked if s not in steps_to_reset]
        self._completed = [s for s in self._completed if s not in steps_to_reset]
        return steps_to_reset

    # ---------------------------------------------------------------- 状态
    def status(self) -> Dict[str, List[str]]:
        """返回前端契约格式"""
        return {
            "completed_steps": [s.value for s in self._completed],
            "locked_steps": [s.value for s in self._locked],
        }


class WorkflowContext:
    """工作流上下文：持有会话的步骤状态机、产物与临时存储"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.steps = StepStateMachine()
        self.artifacts: Dict[StepName, Artifact] = {}
        self.created_at = time.time()
        self.last_accessed = time.time()
        self._temp_storage = temp_storage

    # ---------------------------------------------------------------- 存储
    def get_temp_storage(self):
        return self._temp_storage

    def touch(self) -> None:
        self.last_accessed = time.time()

    # ---------------------------------------------------------------- 产物
    def set_artifact(self, artifact: Artifact) -> None:
        self.artifacts[artifact.step] = artifact
        self._temp_storage.save_artifact(self.session_id, artifact)

    def get_artifact(self, step: StepName) -> Optional[Artifact]:
        return self.artifacts.get(step)

    def clear_artifact(self, step: StepName) -> None:
        self.artifacts.pop(step, None)

    # ---------------------------------------------------------------- 重置
    def reset_step(self, step: StepName) -> List[StepName]:
        """级联重置某步骤及其后续：状态机 + Artifact + temp_storage"""
        reset_steps = self.steps.reset_from(step)
        for s in reset_steps:
            self.clear_artifact(s)
            stage = _STAGE_MAP.get(s)
            if stage:
                self._temp_storage.clear_stage(self.session_id, stage)
        logger.info("WorkflowContext[%s]: 已重置步骤 %s", self.session_id,
                    [s.value for s in reset_steps])
        return reset_steps

    def reset_all(self) -> None:
        """重置会话全部数据"""
        for s in list(self.ORDER_ALL):
            self.clear_artifact(s)
        self.steps.reset_from(StepName.IMPORT)
        self._temp_storage.clear_session(self.session_id)

    ORDER_ALL: List[StepName] = STEP_ORDER
