"""backend/Models/wrappers/reduction.py：降维模型薄封装"""
from .base import BaseWrapper


class ReductionWrapper(BaseWrapper):
    """降维任务封装（fit_transform 常用）"""
    task_type = "dimensionality_reduction"

    def fit_transform(self, X):
        from backend.shared.types import ComponentExecutionError
        try:
            return self.estimator.fit_transform(X)
        except Exception as e:
            raise ComponentExecutionError(f"降维变换失败: {str(e)}") from e
