"""
辅助函数工具模块
"""

import numpy as np
import matplotlib.pyplot as plt


def validate_data_shape(X, expected_features=None):
    """
    验证数据形状
    
    Args:
        X: 输入数据
        expected_features: 期望的特征数量
        
    Returns:
        tuple: (样本数, 特征数)
    """
    X = np.array(X)
    
    if X.ndim == 1:
        n_samples = X.shape[0]
        n_features = 1
    else:
        n_samples, n_features = X.shape
    
    if expected_features is not None and n_features != expected_features:
        raise ValueError(f"数据特征数 ({n_features}) 与期望特征数 ({expected_features}) 不匹配")
    
    return n_samples, n_features


def generate_colors(n_colors, colormap='viridis'):
    """
    生成颜色列表
    
    Args:
        n_colors: 颜色数量
        colormap: 颜色映射
        
    Returns:
        list: 颜色列表
    """
    cmap = plt.get_cmap(colormap)
    return [cmap(i / max(1, n_colors - 1)) for i in range(n_colors)]


def format_labels(labels, max_length=10):
    """
    格式化标签（截断过长的标签）
    
    Args:
        labels: 标签列表
        max_length: 最大长度
        
    Returns:
        list: 格式化后的标签列表
    """
    formatted_labels = []
    for label in labels:
        str_label = str(label)
        if len(str_label) > max_length:
            formatted_labels.append(str_label[:max_length-3] + '...')
        else:
            formatted_labels.append(str_label)
    
    return formatted_labels


def check_backend_compatibility(backend):
    """
    检查后端兼容性
    
    Args:
        backend: 后端名称 ('matplotlib' 或 'plotly')
        
    Returns:
        bool: 是否兼容
    """
    if backend == 'matplotlib':
        try:
            import matplotlib
            return True
        except ImportError:
            return False
    elif backend == 'plotly':
        try:
            import plotly
            return True
        except ImportError:
            return False
    else:
        return False