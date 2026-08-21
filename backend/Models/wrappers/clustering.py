"""backend/Models/wrappers/clustering.py：聚类模型薄封装"""
from .base import BaseWrapper


class ClusteringWrapper(BaseWrapper):
    """聚类任务封装（无监督，fit 不传 y）"""
    task_type = "clustering"
