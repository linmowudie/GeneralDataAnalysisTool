"""
绘制ROC曲线工具函数
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from typing import Any, Optional, Tuple, Dict, Union
import matplotlib.axes as axes
import matplotlib.figure as figure


def plot_roc_curve(
    y_true: Any, 
    y_pred_proba: Optional[np.ndarray], 
    class_names: Optional[list] = None, 
    figsize: Tuple[int, int] = (8, 6)
) -> Tuple[figure.Figure, axes.Axes]:
    """
    绘制ROC曲线
    
    Args:
        y_true: 真实标签
        y_pred_proba: 预测概率
        class_names: 类别名称列表
        figsize: 图表大小
        
    Returns:
        fig, ax: matplotlib图表对象
    """
    # 检查y_pred_proba是否为None
    if y_pred_proba is None:
        raise ValueError("预测概率(y_pred_proba)不能为空(None)，模型可能不支持概率预测")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # 处理二分类情况
    if len(np.unique(y_true)) == 2:
        # 为二分类情况使用不同的变量名避免类型冲突
        binary_fpr, binary_tpr, _ = roc_curve(y_true, y_pred_proba[:, 1])
        binary_roc_auc = auc(binary_fpr, binary_tpr)
        
        ax.plot(binary_fpr, binary_tpr, label=f'ROC曲线 (AUC = {binary_roc_auc:.2f})')
        ax.plot([0, 1], [0, 1], 'k--', label='随机分类器')
        ax.set_xlim((0.0, 1.0))  # 使用元组而不是列表
        ax.set_ylim((0.0, 1.05))  # 使用元组而不是列表
        ax.set_xlabel('假正率')
        ax.set_ylabel('真正率')
        ax.set_title('ROC曲线')
        ax.legend(loc="lower right")
    else:
        # 处理多分类情况
        from sklearn.preprocessing import label_binarize
        from itertools import cycle
        
        classes = np.unique(y_true)
        y_true_bin_result = label_binarize(y_true, classes=classes)
        
        # 检查y_true_bin是否有效
        if y_true_bin_result is None:
            raise ValueError("无法对真实标签进行二值化处理")
        
        # 转换为数组以确保类型安全
        y_true_bin_array: np.ndarray = np.asarray(y_true_bin_result)
        n_classes = y_true_bin_array.shape[1]
        
        multi_fpr: Dict[int, np.ndarray] = dict()
        multi_tpr: Dict[int, np.ndarray] = dict()
        multi_roc_auc: Dict[int, float] = dict()
        
        colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'red', 'green', 'purple'])
        
        for i, color in zip(range(n_classes), colors):
            fpr_vals, tpr_vals, _ = roc_curve(y_true_bin_array[:, i], y_pred_proba[:, i])
            multi_fpr[i] = fpr_vals
            multi_tpr[i] = tpr_vals
            multi_roc_auc[i] = float(auc(fpr_vals, tpr_vals))
            class_name = class_names[i] if class_names and i < len(class_names) else f'类别 {i}'
            ax.plot(multi_fpr[i], multi_tpr[i], color=color, lw=2,
                   label=f'{class_name} (AUC = {multi_roc_auc[i]:.2f})')
        
        ax.plot([0, 1], [0, 1], 'k--', lw=2)
        ax.set_xlim((0.0, 1.0))  # 使用元组而不是列表
        ax.set_ylim((0.0, 1.05))  # 使用元组而不是列表
        ax.set_xlabel('假正率')
        ax.set_ylabel('真正率')
        ax.set_title('多分类ROC曲线')
        ax.legend(loc="lower right")
    
    return fig, ax