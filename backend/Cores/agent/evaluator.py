"""
backend/Cores/agent/evaluator.py
MethodEvaluator 接口 + Metric/LLM 实现

MetricEvaluator：阈值表（R2>=0.7 / accuracy>=0.8 / f1>=0.75 / silhouette>=0.4 -> pass）。
LLMEvaluator：指标摘要 + 任务背景 -> LLM 语义评估（无 LLM 环境回落 Metric）。
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Dict, Optional, Protocol, runtime_checkable

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import (  # noqa: E402
    DataProfile, AnalysisArtifact, EvaluationReport, DecisionStatus, TaskType,
)

logger = logging.getLogger(__name__)


@runtime_checkable
class MethodEvaluator(Protocol):
    """评估器接口"""

    def evaluate(self, profile: DataProfile, artifact: AnalysisArtifact) -> EvaluationReport:
        ...


# 指标阈值表：达到阈值即 pass
_THRESHOLD_TABLE: Dict[str, float] = {
    "r2": 0.7,
    "r2_score": 0.7,
    "accuracy": 0.8,
    "f1": 0.75,
    "f1_score": 0.75,
    "silhouette": 0.4,
    "silhouette_score": 0.4,
}

# 归一化上界（用于 score 压缩到 0~1）
_SCORE_CAP: Dict[str, float] = {
    "r2": 1.0, "r2_score": 1.0,
    "accuracy": 1.0, "f1": 1.0, "f1_score": 1.0,
    "silhouette": 1.0, "silhouette_score": 1.0,
    "mse": 1.0, "mae": 1.0,  # 误差类指标不归一化加分
}


class MetricEvaluator:
    """指标阈值评估器"""

    def evaluate(self, profile: DataProfile, artifact: AnalysisArtifact) -> EvaluationReport:
        metrics = artifact.metrics or {}
        evaluated: Dict[str, float] = {}
        score_parts = []
        passed = False
        has_threshold_metric = False

        for name, value in metrics.items():
            key = name.lower()
            evaluated[name] = value
            if key in _THRESHOLD_TABLE:
                has_threshold_metric = True
                if value >= _THRESHOLD_TABLE[key]:
                    passed = True
            # 归一化评分（越大越好的指标）
            if key in _SCORE_CAP and key not in ("mse", "mae"):
                score_parts.append(max(0.0, min(1.0, value / _SCORE_CAP[key])))

        score = sum(score_parts) / len(score_parts) if score_parts else None

        if passed:
            status = DecisionStatus.PASS
            suggestion = "模型表现达标，建议保留当前结果。"
            next_action = "keep"
        elif has_threshold_metric:
            status = DecisionStatus.RETRY_NEXT
            suggestion = "模型表现未达标，建议尝试下一个候选方法。"
            next_action = "retry_next"
        else:
            # 无可判定阈值的指标（如纯误差指标）：保持，交由人工判断
            status = DecisionStatus.PASS
            suggestion = "无可判定阈值的指标，保留当前结果供人工评估。"
            next_action = "keep"

        return EvaluationReport(
            status=status,
            score=score,
            metrics_evaluated=evaluated,
            suggestion=suggestion,
            next_action=next_action,
        )


class LLMEvaluator:
    """LLM 语义评估器（无 LLM 环境回落 Metric）"""

    def __init__(self, gateway=None, fallback: Optional[MethodEvaluator] = None):
        from backend.Infrastructures.llm_gateway import get_llm_gateway
        self._gateway = gateway or get_llm_gateway()
        self._fallback = fallback or MetricEvaluator()

    def evaluate(self, profile: DataProfile, artifact: AnalysisArtifact) -> EvaluationReport:
        prompt = self._build_prompt(profile, artifact)
        schema_hint = {
            "status": {"type": "string", "default": "retry_next"},
            "suggestion": {"type": "string", "default": ""},
        }
        try:
            raw = self._gateway.chat_json(prompt, schema_hint)
            status_value = str(raw.get("status", "")).lower()
            if status_value in ("pass", "fail", "retry_next"):
                status = DecisionStatus(status_value)
                base = self._fallback.evaluate(profile, artifact)
                return EvaluationReport(
                    status=status,
                    score=base.score,
                    metrics_evaluated=base.metrics_evaluated,
                    suggestion=raw.get("suggestion", "") or base.suggestion,
                    next_action="keep" if status == DecisionStatus.PASS else "retry_next",
                )
        except Exception as e:
            logger.warning("LLMEvaluator: LLM 调用失败，回落指标评估 %s", e)
        return self._fallback.evaluate(profile, artifact)

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _build_prompt(profile: DataProfile, artifact: AnalysisArtifact) -> str:
        return (
            "你是机器学习评估专家。请根据任务背景与模型指标判断当前方法是否达标，"
            "返回 JSON：status(pass/fail/retry_next) 与 suggestion。\n"
            f"任务类型：{artifact.task_type.value}，模型：{artifact.model_type}\n"
            f"数据规模：{profile.n_rows} 行 x {profile.n_cols} 列\n"
            f"指标：{artifact.metrics}"
        )
