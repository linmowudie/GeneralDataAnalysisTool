"""backend.Models.wrappers：按任务分包的 sklearn 薄封装"""
from .base import BaseWrapper
from .regression import RegressionWrapper
from .classification import ClassificationWrapper
from .clustering import ClusteringWrapper
from .reduction import ReductionWrapper
from .association import AssociationWrapper

__all__ = [
    "BaseWrapper",
    "RegressionWrapper",
    "ClassificationWrapper",
    "ClusteringWrapper",
    "ReductionWrapper",
    "AssociationWrapper",
]
