"""
backend/Services/components/analysis_component.py
AnalysisComponent：数据分析部件（前置依赖 cleaning，无清洗时回落 import）

内部：调用分析模型训练/预测/计算指标 -> 模型经 ModelStore 落盘 -> 产出 AnalysisArtifact。
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import (  # noqa: E402
    AnalysisArtifact, StepName, TaskType, WorkflowOrderError,
    ComponentExecutionError, InvalidModelParams,
)
from backend.Services.components.base_component import BaseComponent  # noqa: E402
from backend.Infrastructures.storage import model_store  # noqa: E402

logger = logging.getLogger(__name__)


def _map_task_type(raw: str) -> TaskType:
    """将底层任务类型字符串映射为 TaskType 枚举"""
    mapping = {
        "regression": TaskType.REGRESSION,
        "classification": TaskType.CLASSIFICATION,
        "clustering": TaskType.CLUSTERING,
        "transformer": TaskType.DIMENSIONALITY_REDUCTION,
        "dimensionality_reduction": TaskType.DIMENSIONALITY_REDUCTION,
        "association": TaskType.ASSOCIATION,
    }
    return mapping.get((raw or "").lower(), TaskType.UNKNOWN)


class AnalysisComponent(BaseComponent):
    """数据分析部件"""

    name = StepName.ANALYSIS
    required_inputs: List[StepName] = [StepName.CLEANING]  # 无清洗时回落 import

    def execute(self, context, params: Dict[str, Any]) -> AnalysisArtifact:
        storage = self._storage(context)
        session_id = self._session(context)

        model_type = params.get("model_type") or params.get("model")
        if not model_type:
            raise WorkflowOrderError("缺少 model_type，无法执行分析")

        # 数据回落：优先 cleaned，其次 imported
        df = storage.load_dataframe(session_id, "cleaned")
        if df is None:
            df = storage.load_dataframe(session_id, "imported")
        if df is None:
            raise WorkflowOrderError("会话中没有可用的数据，请先导入或清洗数据")

        # 与现 run-analysis 参数一一对应
        # 注意：分析结果会落盘供可视化/报表使用，默认必须返回训练集与预测集，
        # 否则 VisualizationComponent 取不到特征数据会返回空图表
        analysis_kwargs = dict(
            df=df,
            model=model_type,
            random_state=params.get("random_state", 42),
            is_split=params.get("is_split", True),
            split_ratio=params.get("split_ratio", 0.8),
            feature_cols=params.get("feature_cols"),
            target_col=params.get("target_col"),
            is_return_model_param=params.get("is_return_model_param", False),
            metrics_list=params.get("metrics_list"),
            is_return_model_score=params.get("is_return_model_score", True),
            is_return_training_set=params.get("is_return_training_set", True),
            is_return_model_predicting_set=params.get("is_return_model_predicting_set", True),
            feature_cols_encoding=params.get("feature_cols_encoding", "onehot"),
            target_col_encoding=params.get("target_col_encoding", "label"),
            test_set=params.get("test_set"),
            model_params=params.get("model_params"),
        )

        try:
            # 调用分析模型（backend.Models.analysis）
            from backend.Models.analysis import DataAnalyzer

            analyzer = DataAnalyzer(**analysis_kwargs)
            result = analyzer.analyze()
        except ValueError as e:
            # 模型参数/配置错误（与原 api 的 400 语义一致）
            logger.error("AnalysisComponent: 模型配置错误 %s", e)
            raise InvalidModelParams(f"模型配置错误: {str(e)}") from e
        except Exception as e:
            logger.error("AnalysisComponent: 分析失败 %s", e, exc_info=True)
            raise ComponentExecutionError(f"数据分析过程中出错: {str(e)}") from e

        # 保存完整分析结果（含 trained_model 实例）到 analyzed 阶段，供可视化/报表使用
        self._save_analysis_result(storage, session_id, result)

        # 模型落盘 -> trained_model_ref
        trained_model = result.get("trained_model")
        trained_model_ref: Optional[str] = None
        if trained_model is not None:
            try:
                trained_model_ref = model_store.save_model(trained_model)
            except Exception as e:
                logger.warning("AnalysisComponent: 模型落盘失败 %s", e)

        # 提取指标
        metrics: Dict[str, float] = {}
        model_score = result.get("model_score")
        if isinstance(model_score, dict):
            for k, v in model_score.items():
                try:
                    metrics[str(k)] = float(v)
                except (TypeError, ValueError):
                    pass

        # 提取预测值
        predictions = result.get("predictions")
        prediction_list = None
        if predictions is not None:
            try:
                prediction_list = pd.Series(predictions).tolist() if not isinstance(predictions, list) else predictions
            except Exception:
                prediction_list = None

        artifact = AnalysisArtifact(
            step=StepName.ANALYSIS,
            task_type=_map_task_type(result.get("task_type", "")),
            model_type=str(model_type).lower(),
            model_params=result.get("model_params") or analysis_kwargs.get("model_params") or {},
            metrics=metrics,
            predictions=prediction_list,
            trained_model_ref=trained_model_ref,
        )
        logger.info("AnalysisComponent: 分析完成 model=%s metrics=%s", model_type, metrics)
        return artifact

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _save_analysis_result(storage, session_id: str, result: Dict[str, Any]) -> None:
        """将完整分析结果以 pickle 形式落到 analyzed 阶段（含模型实例）"""
        import pickle

        path = storage._stage_path(session_id, "analyzed")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(result, f)
