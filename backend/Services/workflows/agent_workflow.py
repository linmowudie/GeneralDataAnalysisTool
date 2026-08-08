"""
backend/Services/workflows/agent_workflow.py
AgentWorkflow：Agent 自动分析闭环（画像 -> 推荐 -> 执行 -> 评估 -> 择优）

执行序列：
读取清洗后数据(回落导入数据) -> DataProfiler 画像 -> Planner 推荐 Top-N 候选
-> 逐候选 AnalysisComponent 执行 -> Evaluator 评估
-> pass 记 best 结束 / retry_next 继续 / 候选耗尽或超时取历史最优。

熔断：候选耗尽或总耗时超 timeout_sec 时终止并返回已有最优。
全部尝试记录写入 AgentDecision.attempts。
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

from backend.shared.types import (  # noqa: E402
    AgentDecision, AnalysisArtifact, AttemptRecord, DecisionStatus,
    PlanCandidate, StepName, WorkflowOrderError,
)
from backend.Cores.agent.profiler import DataProfiler  # noqa: E402
from backend.Services.components.analysis_component import AnalysisComponent  # noqa: E402

logger = logging.getLogger(__name__)


class AgentWorkflow:
    """Agent 自动分析工作流"""

    def __init__(self, planner=None, evaluator=None,
                 max_candidates: int = 3, timeout_sec: int = 300):
        from backend.Cores.agent.planner import RulePlanner
        from backend.Cores.agent.evaluator import MetricEvaluator

        self._planner = planner or RulePlanner()
        self._evaluator = evaluator or MetricEvaluator()
        self._max_candidates = max_candidates
        self._timeout_sec = timeout_sec
        self._profiler = DataProfiler()
        self._analyzer = AnalysisComponent()

    # ------------------------------------------------------------------ 执行
    def run(self, context, target_col: Optional[str] = None) -> AgentDecision:
        """执行 Agent 闭环并返回最终决策"""
        start = time.time()
        storage = context.get_temp_storage()
        session_id = context.session_id

        # 1. 读取清洗后数据（回落导入数据）
        df = storage.load_dataframe(session_id, "cleaned")
        if df is None:
            df = storage.load_dataframe(session_id, "imported")
        if df is None:
            raise WorkflowOrderError("会话中没有可用的数据，请先导入数据")

        # 2. 数据画像
        profile = self._profiler.profile(df, target_col=target_col)

        # 3. Planner 推荐 Top-N 候选
        candidates = self._planner.recommend(profile)
        candidates.sort(key=lambda c: c.priority)
        candidates = candidates[: self._max_candidates]
        logger.info("AgentWorkflow[%s]: 候选 %s", session_id,
                    [c.model_type for c in candidates])

        # 4. 逐候选执行 + 评估
        attempts: List[AttemptRecord] = []
        artifacts: Dict[str, AnalysisArtifact] = {}  # model_type -> 产物
        best: Optional[AttemptRecord] = None

        for candidate in candidates:
            if time.time() - start > self._timeout_sec:
                logger.warning("AgentWorkflow[%s]: 超时熔断，返回已有最优", session_id)
                break

            record = AttemptRecord(
                model_type=candidate.model_type,
                task_type=candidate.task_type,
            )
            try:
                artifact = self._analyzer.execute(
                    context, self._build_params(candidate, target_col)
                )
                record.metrics = artifact.metrics
                artifacts[candidate.model_type] = artifact
                record.evaluation = self._evaluator.evaluate(profile, artifact)
            except Exception as e:
                record.error = str(e)
                logger.warning("AgentWorkflow[%s]: 候选 %s 执行失败 %s",
                               session_id, candidate.model_type, e)

            attempts.append(record)

            if record.evaluation is None:
                continue
            if record.evaluation.status == DecisionStatus.PASS:
                best = record
                break
            # retry_next：继续下一候选

        # 5. 熔断后兜底：取历史最优（按评估 score）
        if best is None:
            best = self._pick_best(attempts)

        # 6. 最优产物写入上下文并推进状态机
        if best is not None and best.model_type in artifacts:
            context.set_artifact(artifacts[best.model_type])
            context.steps.complete(StepName.ANALYSIS)
            context.steps.lock(StepName.ANALYSIS)
            context.touch()

        decision = AgentDecision(
            session_id=session_id,
            profile=profile,
            attempts=attempts,
            best=best,
        )
        logger.info("AgentWorkflow[%s]: 闭环结束 best=%s 耗时 %.1fs",
                    session_id,
                    best.model_type if best else None, time.time() - start)
        return decision

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _build_params(candidate: PlanCandidate, target_col: Optional[str]) -> Dict[str, Any]:
        """将候选方案转换为 AnalysisComponent 参数"""
        return {
            "model_type": candidate.model_type,
            "target_col": target_col,
            "model_params": candidate.suggested_params or None,
        }

    @staticmethod
    def _pick_best(attempts: List[AttemptRecord]) -> Optional[AttemptRecord]:
        """无达标候选时，按评估 score 取历史最优（无 score 的跳过）"""
        scored = [a for a in attempts if a.evaluation is not None and a.evaluation.score is not None]
        if not scored:
            # 无评分记录时退而取首个执行成功的
            succeeded = [a for a in attempts if a.error is None]
            return succeeded[0] if succeeded else None
        return max(scored, key=lambda a: a.evaluation.score)
