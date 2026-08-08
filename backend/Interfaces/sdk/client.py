"""
backend/Interfaces/sdk/client.py
DataAnalysisClient：Python SDK 门面（直调控制器，不经 HTTP，不依赖 fastapi）
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import (  # noqa: E402
    Artifact, AgentDecision, StepName,
)
from backend.Interfaces.controllers import (  # noqa: E402
    SessionController, StepController, AgentController,
)

logger = logging.getLogger(__name__)


class DataAnalysisClient:
    """SDK 门面：手动流程 + Agent 闭环，与 Web 端共用同一控制器层"""

    def __init__(self, planner=None, evaluator=None):
        self._session = SessionController()  # SDK 独立会话空间
        self._step = StepController(self._session)
        self._agent = AgentController(self._session, planner=planner, evaluator=evaluator)

    # ---------------------------------------------------------------- 会话
    def create_session(self) -> str:
        return self._session.create_session()

    def end_session(self, session_id: str) -> bool:
        return self._session.end_session(session_id)

    def step_status(self, session_id: str) -> Dict[str, Any]:
        return self._session.get_step_status(session_id)

    def reset_step(self, session_id: str, step: str) -> bool:
        return self._session.reset_step(session_id, step)

    def reset_all(self, session_id: str) -> bool:
        return self._session.reset_all(session_id)

    # ---------------------------------------------------------------- 导入
    def import_file(self, session_id: str, file_path: str,
                    resource_type: Optional[str] = None,
                    chunksize: Optional[int] = None) -> Artifact:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        params = {
            "resource_path": str(path),
            "resource_type": resource_type or path.suffix.lstrip(".").lower() or "csv",
        }
        if chunksize:
            params["chunksize"] = chunksize
        ctx = self._session.get_context(session_id)
        ctx.reset_step(StepName.IMPORT)
        self._session.set_last_imported_file(session_id, path.name)
        return self._session.execute_step(session_id, StepName.IMPORT, params)

    def import_database(self, session_id: str, db_type: str, host: str, port: int,
                        database: str, table: str,
                        username: Optional[str] = None,
                        password: Optional[str] = None) -> Artifact:
        if username and password:
            conn = f"{db_type}://{username}:{password}@{host}:{port}/{database}"
        else:
            conn = f"{db_type}://{host}:{port}/{database}"
        params = {
            "resource_path": table,
            "resource_type": db_type,
            "db_connection_string": conn,
            "query": f"SELECT * FROM {table}",
            "is_database": True,
        }
        ctx = self._session.get_context(session_id)
        ctx.reset_step(StepName.IMPORT)
        self._session.set_last_imported_file(session_id, f"{database}.{table}")
        return self._session.execute_step(session_id, StepName.IMPORT, params)

    # ---------------------------------------------------------------- 手动流程
    def preview(self, session_id: str, head_n: int = 10) -> Artifact:
        return self._session.execute_step(session_id, StepName.PREVIEW, {"head_n": head_n})

    def clean(self, session_id: str, mode: str = "standard",
              params_list: Optional[List[str]] = None,
              is_freedom_params: bool = False,
              target_col: Optional[str] = None) -> Artifact:
        return self._session.execute_step(session_id, StepName.CLEANING, {
            "select_mode": mode,
            "params_list": params_list or [],
            "is_freedom_params": is_freedom_params,
            "target_col": target_col,
        })

    def analyze(self, session_id: str, model_type: str,
                **parameters: Any) -> Artifact:
        return self._session.execute_step(session_id, StepName.ANALYSIS, {
            "model_type": model_type,
            **parameters,
        })

    def visualize(self, session_id: str,
                  param_dict: Optional[Dict[str, Any]] = None) -> Artifact:
        params = {"param_dict": param_dict} if param_dict else {}
        return self._session.execute_step(session_id, StepName.VISUALIZATION, params)

    def report(self, session_id: str, report_type: str = "full") -> Artifact:
        return self._session.execute_step(session_id, StepName.REPORT, {
            "report_type": report_type,
        })

    # ---------------------------------------------------------------- 步骤锁
    def lock_step(self, session_id: str, step: str) -> Dict[str, Any]:
        return self._step.lock(session_id, step)

    def unlock_step(self, session_id: str, step: str) -> Dict[str, Any]:
        return self._step.unlock(session_id, step)

    # ---------------------------------------------------------------- Agent
    def data_profile(self, session_id: str, target_col: Optional[str] = None):
        return self._agent.data_profile(session_id, target_col=target_col)

    def recommend_methods(self, session_id: str, target_col: Optional[str] = None):
        return self._agent.recommend_methods(session_id, target_col=target_col)

    def evaluate(self, session_id: str):
        return self._agent.evaluate(session_id)

    def auto_analyze(self, session_id: str, max_candidates: int = 3,
                     target_col: Optional[str] = None,
                     timeout_sec: int = 300) -> AgentDecision:
        return self._agent.auto_analyze(
            session_id,
            max_candidates=max_candidates,
            target_col=target_col,
            timeout_sec=timeout_sec,
        )

    def get_decision(self, session_id: str) -> Optional[AgentDecision]:
        return self._agent.get_decision(session_id)
