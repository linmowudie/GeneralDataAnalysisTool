"""
变换器模块初始化
"""

from .pca import PCAStrategy
from .standardscaler import StandardScalerStrategy
from .tsne import TSNEStrategy
from .umap import UMAPStrategy
from .three_d import ThreeDStrategy
from .no_model import NoModelStrategy
from .base import TransformerStrategy
from .strategy import TransformerStrategySelector