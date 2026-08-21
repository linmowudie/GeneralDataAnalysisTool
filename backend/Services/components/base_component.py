"""
backend/Services/components/base_component.py
BaseComponent：部件统一协议（原 backend/Cores/base_component.py 迁入）

执行前置检查由 Services 依据 required_inputs 完成；部件内部不再各自校验步骤顺序。
组件层不 import fastapi，不感知请求来源。
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import Artifact, StepName  # noqa: E402


@runtime_checkable
class ComponentContext(Protocol):
    """部件执行所需的最小上下文协议（由 Services.WorkflowContext 实现）"""

    session_id: str

    def get_temp_storage(self):
        """返回 TempStorage 实例"""
        ...


class BaseComponent(ABC):
    """部件统一协议基类"""

    #: 对应 StepName
    name: StepName = StepName.IMPORT
    #: 前置产物依赖
    required_inputs: List[StepName] = []

    @abstractmethod
    def execute(self, context: ComponentContext, params: Dict[str, Any]) -> Artifact:
        """执行部件逻辑并返回产物"""
        raise NotImplementedError

    # ---------------------------------------------------------------- 工具
    def _storage(self, context: ComponentContext):
        return context.get_temp_storage()

    def _session(self, context: ComponentContext) -> str:
        return context.session_id
