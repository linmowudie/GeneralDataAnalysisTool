"""
backend/Interfaces/controllers/agent_controller.py
AgentController：Agent 闭环控制器（画像 / 推荐 / 评估 / 自动分析 / 决策查询）
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import (  # noqa: E402
    AgentDecision, DataProfile, EvaluationReport, PlanCandidate,
    StepName, WorkflowOrderError,
)
from backend.Cores.agent.profiler import DataProfiler  # noqa: E402
from backend.Services.workflows.agent_workflow import AgentWorkflow  # noqa: E402
from .session_controller import SessionController  # noqa: E402

logger = logging.getLogger(__name__)


class AgentController:
    """Agent 控制器"""

    def __init__(self, session_controller: SessionController,
                 planner=None, evaluator=None):
        self._session = session_controller
        self._planner = planner
        self._evaluator = evaluator
        self._profiler = DataProfiler()
        self._decisions: Dict[str, AgentDecision] = {}

    # ---------------------------------------------------------------- 画像
    def data_profile(self, session_id: str, target_col: Optional[str] = None) -> DataProfile:
        ctx = self._session.get_context(session_id)
        df = self._load_data(session_id)
        if df is None:
            raise WorkflowOrderError("会话中没有可用的数据，请先导入数据")
        return self._profiler.profile(df, target_col=target_col)

    # ---------------------------------------------------------------- 推荐
    def recommend_methods(self, session_id: str,
                          target_col: Optional[str] = None) -> List[PlanCandidate]:
        profile = self.data_profile(session_id, target_col)
        planner = self._planner
        if planner is None:
            from backend.Cores.agent.planner import RulePlanner
            planner = RulePlanner()
        candidates = planner.recommend(profile)
        candidates.sort(key=lambda c: c.priority)
        return candidates

    # ---------------------------------------------------------------- 评估
    def evaluate(self, session_id: str) -> EvaluationReport:
        ctx = self._session.get_context(session_id)
        artifact = ctx.get_artifact(StepName.ANALYSIS)
        if artifact is None:
            raise WorkflowOrderError("尚无分析结果，请先执行分析")
        profile = self.data_profile(session_id)
        evaluator = self._evaluator
        if evaluator is None:
            from backend.Cores.agent.evaluator import MetricEvaluator
            evaluator = MetricEvaluator()
        return evaluator.evaluate(profile, artifact)

    # ---------------------------------------------------------------- 闭环
    def auto_analyze(self, session_id: str, max_candidates: int = 3,
                     target_col: Optional[str] = None,
                     timeout_sec: int = 300) -> AgentDecision:
        ctx = self._session.get_context(session_id)
        # 解锁分析步骤以允许 Agent 重跑
        ctx.steps.unlock(StepName.ANALYSIS)
        workflow = AgentWorkflow(
            planner=self._planner,
            evaluator=self._evaluator,
            max_candidates=max_candidates,
            timeout_sec=timeout_sec,
        )
        decision = workflow.run(ctx, target_col=target_col)
        self._decisions[session_id] = decision
        return decision

    def get_decision(self, session_id: str) -> Optional[AgentDecision]:
        self._session.get_context(session_id)  # 校验会话有效性
        return self._decisions.get(session_id)

    # ---------------------------------------------------------------- 内部
    def _load_data(self, session_id: str):
        from backend.Infrastructures.storage import temp_storage

        df = temp_storage.load_dataframe(session_id, "cleaned")
        if df is None:
            df = temp_storage.load_dataframe(session_id, "imported")
        return df
