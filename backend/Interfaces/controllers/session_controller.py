"""
backend/Interfaces/controllers/session_controller.py
SessionController：会话控制器

持有 SessionRegistry，统一入口：创建/结束/重置/状态查询/步骤执行。
路由与 SDK 共用同一控制器，保证 Web 与 SDK 行为一致。
"""

from __future__ import annotations

import sys
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import Artifact, StepName  # noqa: E402
from backend.Services.workflows.context import WorkflowContext  # noqa: E402
from backend.Services.workflows.manual_workflow import ManualWorkflow  # noqa: E402
from .session_registry import SessionRegistry  # noqa: E402

logger = logging.getLogger(__name__)


class SessionController:
    """会话控制器"""

    def __init__(self, registry: Optional[SessionRegistry] = None):
        self._registry = registry or SessionRegistry()
        self._workflow = ManualWorkflow()

    # ---------------------------------------------------------------- 属性
    @property
    def registry(self) -> SessionRegistry:
        return self._registry

    @property
    def workflow(self) -> ManualWorkflow:
        return self._workflow

    # ---------------------------------------------------------------- 会话
    def create_session(self) -> str:
        return self._registry.create().session_id

    def get_context(self, session_id: str) -> WorkflowContext:
        """获取上下文（不存在/超时抛领域异常）"""
        return self._registry.get(session_id)

    def session_lock(self, session_id: str) -> asyncio.Lock:
        return self._registry.lock(session_id)

    def end_session(self, session_id: str) -> bool:
        return self._registry.remove(session_id)

    def cleanup_expired_sessions(self) -> int:
        return self._registry.cleanup_expired()

    # ---------------------------------------------------------------- 重置
    def reset_step(self, session_id: str, step: str) -> bool:
        """级联重置步骤；未知步骤名与原实现一致按成功处理（no-op）"""
        ctx = self._registry.get(session_id)
        try:
            step_enum = StepName(step)
        except ValueError:
            logger.warning("SessionController: 未知步骤名 %s，忽略", step)
            return True
        ctx.reset_step(step_enum)
        return True

    def reset_all(self, session_id: str) -> bool:
        ctx = self._registry.get(session_id)
        ctx.reset_all()
        return True

    # ---------------------------------------------------------------- 状态
    def get_step_status(self, session_id: str) -> Dict[str, Any]:
        """会话不存在时返回空状态（与原契约一致）"""
        ctx = self._registry.peek(session_id)
        if ctx is None:
            return {"completed_steps": [], "locked_steps": []}
        return ctx.steps.status()

    # ---------------------------------------------------------------- 执行
    def execute_step(self, session_id: str, step: StepName,
                     params: Optional[Dict[str, Any]] = None) -> Artifact:
        """执行指定步骤（自动解锁目标步骤，保持与原行为一致：锁不阻塞重跑）"""
        ctx = self._registry.get(session_id)
        if ctx.steps.is_locked(step):
            ctx.steps.unlock(step)
        return self._workflow.execute_step(ctx, step, params or {})

    # ---------------------------------------------------------------- 元信息
    def set_last_imported_file(self, session_id: str, name: Optional[str]) -> None:
        self._registry.meta(session_id)["last_imported_file"] = name

    def get_last_imported_file(self, session_id: str) -> Optional[str]:
        return self._registry.meta(session_id).get("last_imported_file")


# 全局单例（Web 与 SDK 默认共用）
session_controller = SessionController()
