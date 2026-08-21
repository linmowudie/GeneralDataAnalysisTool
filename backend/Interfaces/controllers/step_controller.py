"""
backend/Interfaces/controllers/step_controller.py
StepController：步骤锁控制器

锁状态唯一来源为 StepStateMachine（消除原 step_lock 与 core 双轨）。
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Any, Dict, List

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import StepName, WorkflowOrderError  # noqa: E402
from .session_controller import SessionController  # noqa: E402

logger = logging.getLogger(__name__)

VALID_STEPS: List[str] = [s.value for s in StepName]


class StepController:
    """步骤锁控制器"""

    def __init__(self, session_controller: SessionController):
        self._session = session_controller

    # ---------------------------------------------------------------- 内部
    @staticmethod
    def _validate(step: str) -> StepName:
        try:
            return StepName(step)
        except ValueError:
            raise WorkflowOrderError(f"无效的步骤名称: {step}。有效步骤: {VALID_STEPS}")

    # ---------------------------------------------------------------- 操作
    def lock(self, session_id: str, step: str) -> Dict[str, Any]:
        step_enum = self._validate(step)
        ctx = self._session.get_context(session_id)
        ctx.steps.lock(step_enum)
        ctx.touch()
        logger.info("StepController: 会话 %s 步骤 %s 已锁定", session_id, step)
        return {
            "status": "success",
            "message": f"步骤 {step} 已成功锁定",
            "locked_steps": ctx.steps.status()["locked_steps"],
        }

    def unlock(self, session_id: str, step: str) -> Dict[str, Any]:
        step_enum = self._validate(step)
        ctx = self._session.get_context(session_id)
        ctx.steps.unlock(step_enum)
        ctx.touch()
        logger.info("StepController: 会话 %s 步骤 %s 已解锁", session_id, step)
        return {
            "status": "success",
            "message": f"步骤 {step} 已成功解锁",
            "locked_steps": ctx.steps.status()["locked_steps"],
        }

    def status(self, session_id: str) -> Dict[str, Any]:
        ctx = self._session.get_context(session_id)
        return ctx.steps.status()

    def lock_multiple(self, session_id: str, steps: List[str]) -> Dict[str, Any]:
        step_enums = [self._validate(s) for s in steps]
        ctx = self._session.get_context(session_id)
        for step_enum in step_enums:
            ctx.steps.lock(step_enum)
        ctx.touch()
        logger.info("StepController: 会话 %s 批量锁定 %s", session_id, steps)
        return {
            "status": "success",
            "message": f"{len(steps)} 个步骤已成功锁定",
            "locked_steps": ctx.steps.status()["locked_steps"],
        }
