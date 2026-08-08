"""
backend/Models/wrappers/base.py
BaseWrapper：sklearn 估计器薄封装基类

职责：训练/预测异常归一为 ComponentExecutionError；
sklearn 导入收敛在 ModelFactory（经 registry 映射），wrapper 不直接导入模型类。
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Any, Optional

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import ComponentExecutionError  # noqa: E402

logger = logging.getLogger(__name__)


class BaseWrapper:
    """估计器薄封装基类"""

    #: 子类标识的任务类型
    task_type: str = "unknown"

    def __init__(self, estimator: Any):
        self.estimator = estimator

    def fit(self, X, y=None):
        """训练，异常归一为 ComponentExecutionError"""
        try:
            if y is None:
                self.estimator.fit(X)
            else:
                self.estimator.fit(X, y)
            return self
        except Exception as e:
            logger.error("模型训练失败: %s", e, exc_info=True)
            raise ComponentExecutionError(f"模型训练失败: {str(e)}") from e

    def predict(self, X):
        """预测（无监督模型不适用）"""
        try:
            return self.estimator.predict(X)
        except Exception as e:
            logger.error("模型预测失败: %s", e, exc_info=True)
            raise ComponentExecutionError(f"模型预测失败: {str(e)}") from e

    def transform(self, X):
        """变换（降维/缩放类）"""
        try:
            return self.estimator.transform(X)
        except Exception as e:
            logger.error("模型变换失败: %s", e, exc_info=True)
            raise ComponentExecutionError(f"模型变换失败: {str(e)}") from e

    def get_params(self):
        try:
            return self.estimator.get_params()
        except Exception:
            return {}

    @property
    def model_name(self) -> str:
        return type(self.estimator).__name__
