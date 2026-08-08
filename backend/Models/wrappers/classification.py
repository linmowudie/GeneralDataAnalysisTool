"""backend/Models/wrappers/classification.py：分类模型薄封装"""
from .base import BaseWrapper


class ClassificationWrapper(BaseWrapper):
    """分类任务封装"""
    task_type = "classification"
