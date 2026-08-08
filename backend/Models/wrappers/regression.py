"""backend/Models/wrappers/regression.py：回归模型薄封装"""
from .base import BaseWrapper


class RegressionWrapper(BaseWrapper):
    """回归任务封装"""
    task_type = "regression"
