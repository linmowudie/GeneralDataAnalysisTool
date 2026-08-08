"""
backend/Services/workflows/builder.py
WorkflowBuilder：按模式构建工作流实例
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import WorkflowMode  # noqa: E402
from .manual_workflow import ManualWorkflow  # noqa: E402
from .agent_workflow import AgentWorkflow  # noqa: E402


class WorkflowBuilder:
    """工作流构建器"""

    def __init__(self, planner=None, evaluator=None,
                 max_candidates: int = 3, timeout_sec: int = 300):
        self._planner = planner
        self._evaluator = evaluator
        self._max_candidates = max_candidates
        self._timeout_sec = timeout_sec

    def build(self, mode: WorkflowMode):
        """按模式构建工作流：MANUAL -> ManualWorkflow；AGENT -> AgentWorkflow"""
        if mode == WorkflowMode.MANUAL:
            return ManualWorkflow()
        return AgentWorkflow(
            planner=self._planner,
            evaluator=self._evaluator,
            max_candidates=self._max_candidates,
            timeout_sec=self._timeout_sec,
        )
