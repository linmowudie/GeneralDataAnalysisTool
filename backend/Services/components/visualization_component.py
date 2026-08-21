"""
backend/Services/components/visualization_component.py
VisualizationComponent：数据可视化部件（前置依赖 analysis）

param_dict 可选，缺省时按分析结果自动构建。
"""

from __future__ import annotations

import sys
import pickle
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import VisualizationArtifact, StepName, WorkflowOrderError  # noqa: E402
from backend.Services.components.base_component import BaseComponent  # noqa: E402

logger = logging.getLogger(__name__)


class VisualizationComponent(BaseComponent):
    """数据可视化部件"""

    name = StepName.VISUALIZATION
    required_inputs: List[StepName] = [StepName.ANALYSIS]

    def execute(self, context, params: Dict[str, Any]) -> VisualizationArtifact:
        storage = self._storage(context)
        session_id = self._session(context)

        analyzed_data = self._load_analysis_result(storage, session_id)
        if not analyzed_data:
            raise WorkflowOrderError("没有可用的分析数据，请先进行数据分析")

        param_dict = params.get("param_dict")
        if not param_dict:
            param_dict = self._build_default_params(analyzed_data)

        if param_dict.get("feature") is None:
            logger.warning("VisualizationComponent: 缺少特征数据，返回空图表")
            return VisualizationArtifact(step=StepName.VISUALIZATION, charts={})

        try:
            # 调用可视化模型（backend.Models.visualization）
            from backend.Models.visualization import DataVisualization

            visualizer = DataVisualization(param_dict)
            plots = visualizer.plot_chart()
        except Exception as e:
            logger.error("VisualizationComponent: 可视化失败 %s", e, exc_info=True)
            return VisualizationArtifact(step=StepName.VISUALIZATION, charts={})

        charts = self._serialize_plots(plots)

        # 落 temp_storage（stage=visualized），供报表使用
        self._save_plots(storage, session_id, plots)

        artifact = VisualizationArtifact(step=StepName.VISUALIZATION, charts=charts)
        logger.info("VisualizationComponent: 生成 %d 个图表", len(charts))
        return artifact

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _load_analysis_result(storage, session_id: str) -> Optional[Dict[str, Any]]:
        path = storage._stage_path(session_id, "analyzed")
        if not path.exists():
            return None
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning("VisualizationComponent: 加载分析结果失败 %s", e)
            return None

    @staticmethod
    def _build_default_params(analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据分析结果构建默认可视化参数（对齐原 core 逻辑）"""
        trained_model = analyzed_data.get("trained_model")
        task_type = analyzed_data.get("task_type", "unknown")
        param_dict = {
            "task_type": task_type,
            "model_name": trained_model.__class__.__name__.lower() if trained_model else "unknown",
        }
        if analyzed_data.get("X_test") is not None and analyzed_data.get("y_test") is not None \
                and analyzed_data.get("predictions") is not None:
            param_dict["feature"] = analyzed_data["X_test"]
            param_dict["target"] = analyzed_data["y_test"]
            param_dict["predict"] = analyzed_data["predictions"]
        elif analyzed_data.get("X_train") is not None and analyzed_data.get("y_train") is not None:
            param_dict["feature"] = analyzed_data["X_train"]
            param_dict["target"] = analyzed_data["y_train"]
            if trained_model is not None:
                try:
                    preds = trained_model.predict(analyzed_data["X_train"])
                    param_dict["predict"] = pd.Series(preds, index=analyzed_data["y_train"].index)
                except Exception:
                    param_dict["predict"] = None
        return param_dict

    @staticmethod
    def _serialize_plots(plots: Dict[str, Any]) -> Dict[str, Any]:
        """plotly Figure -> JSON 可序列化结构"""
        charts: Dict[str, Any] = {}
        for name, fig in (plots or {}).items():
            try:
                if hasattr(fig, "to_plotly_json"):
                    charts[name] = fig.to_plotly_json()
                elif hasattr(fig, "to_dict"):
                    charts[name] = fig.to_dict()
                else:
                    charts[name] = str(fig)
            except Exception:
                charts[name] = str(fig)
        return charts

    @staticmethod
    def _save_plots(storage, session_id: str, plots: Dict[str, Any]) -> None:
        path = storage._stage_path(session_id, "visualized")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(plots, f)
