"""backend/Models/wrappers/association.py：关联规则模型薄封装"""
from .base import BaseWrapper


class AssociationWrapper(BaseWrapper):
    """关联规则学习封装（非 sklearn 估计器，走专用执行路径）"""
    task_type = "association"
