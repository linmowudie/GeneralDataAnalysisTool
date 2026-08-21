"""
backend/Cores/agent/planner.py
AnalysisPlanner 接口 + Rule/LLM 实现

RulePlanner：内置规则表（任务类型 × 数据规模 × 特征类型 -> 候选模型，候选集来自 ModelRegistry）。
LLMPlanner：profile 序列化为 prompt -> llm_gateway.chat_json -> 解析为 PlanCandidate 列表。
"""

from __future__ import annotations

import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import DataProfile, PlanCandidate, TaskType  # noqa: E402
from backend.Models.registry import model_registry  # noqa: E402

logger = logging.getLogger(__name__)


@runtime_checkable
class AnalysisPlanner(Protocol):
    """规划器接口"""

    def recommend(self, profile: DataProfile) -> List[PlanCandidate]:
        ...


# 任务类型 -> 候选模型 key（优先级从前到后递减）
_RULE_TABLE: Dict[TaskType, List[str]] = {
    TaskType.REGRESSION: ["linearregression", "ridge", "lasso"],
    TaskType.CLASSIFICATION: ["logisticregression", "decisiontreeclassifier", "kneighborsclassifier", "svc"],
    TaskType.CLUSTERING: ["kmeans", "dbscan", "meanshift"],
    TaskType.DIMENSIONALITY_REDUCTION: ["pca", "tsne"],
    TaskType.ASSOCIATION: ["apriori"],
}


class RulePlanner:
    """规则规划器"""

    def __init__(self, registry=None):
        self._registry = registry or model_registry

    def recommend(self, profile: DataProfile) -> List[PlanCandidate]:
        task = profile.inferred_task_type
        candidates: List[PlanCandidate] = []

        # 若推断任务无候选（如 unknown），退化为按列数选择聚类/回归
        if task not in _RULE_TABLE:
            task = TaskType.CLUSTERING if not profile.target_col else TaskType.REGRESSION

        model_keys = _RULE_TABLE.get(task, [])
        available = set(self._registry.list_models())

        priority = 1
        for key in model_keys:
            if key not in available:
                continue
            suggested = self._suggest_params(key, profile)
            candidates.append(PlanCandidate(
                model_type=key,
                task_type=task,
                suggested_params=suggested,
                priority=priority,
                reason=f"规则推荐：任务类型 {task.value} 优先使用 {key}",
            ))
            priority += 1

        logger.info("RulePlanner: 推荐 %d 个候选", len(candidates))
        return candidates

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _suggest_params(model_key: str, profile: DataProfile) -> Dict[str, Any]:
        """按数据规模给出轻量参数建议"""
        params: Dict[str, Any] = {}
        if model_key == "kmeans":
            # 聚类簇数粗略建议：与列数相关，夹在 2~10
            params["n_clusters"] = max(2, min(10, profile.n_cols - 1))
        elif model_key == "kneighborsclassifier":
            params["n_neighbors"] = 3 if profile.n_rows < 100 else 5
        return params


class LLMPlanner:
    """LLM 规划器（无 LLM 环境回落规则）"""

    def __init__(self, gateway=None, fallback: Optional[AnalysisPlanner] = None):
        from backend.Infrastructures.llm_gateway import get_llm_gateway
        self._gateway = gateway or get_llm_gateway()
        self._fallback = fallback or RulePlanner()

    def recommend(self, profile: DataProfile) -> List[PlanCandidate]:
        prompt = self._build_prompt(profile)
        schema_hint = {
            "candidates": {"type": "list", "items_default": []},
        }
        try:
            raw = self._gateway.chat_json(prompt, schema_hint)
            candidates = self._parse(raw, profile)
            if candidates:
                return candidates
        except Exception as e:
            logger.warning("LLMPlanner: LLM 调用失败，回落规则 %s", e)
        return self._fallback.recommend(profile)

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _build_prompt(profile: DataProfile) -> str:
        summary = {
            "n_rows": profile.n_rows,
            "n_cols": profile.n_cols,
            "target_col": profile.target_col,
            "inferred_task_type": profile.inferred_task_type.value,
            "columns": [
                {"name": c.name, "dtype": c.dtype, "is_numeric": c.is_numeric}
                for c in profile.columns
            ],
        }
        return (
            "你是机器学习方法选择专家。根据以下数据画像推荐最合适的分析方法候选列表，"
            "返回 JSON，键为 candidates，每项含 model_type/task_type/priority/reason。\n"
            f"数据画像：{json.dumps(summary, ensure_ascii=False)}"
        )

    def _parse(self, raw: Dict[str, Any], profile: DataProfile) -> List[PlanCandidate]:
        candidates: List[PlanCandidate] = []
        available = set(model_registry.list_models())
        for idx, item in enumerate(raw.get("candidates", [])):
            model_type = str(item.get("model_type", "")).lower()
            if not model_type or model_type not in available:
                continue
            try:
                task = TaskType(item.get("task_type", profile.inferred_task_type.value))
            except ValueError:
                task = profile.inferred_task_type
            candidates.append(PlanCandidate(
                model_type=model_type,
                task_type=task,
                suggested_params=item.get("suggested_params", {}) or {},
                priority=int(item.get("priority", idx + 1)),
                reason=item.get("reason", "LLM 推荐"),
            ))
        return candidates
