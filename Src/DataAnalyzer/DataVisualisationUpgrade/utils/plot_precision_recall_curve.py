"""
绘制精确率-召回率曲线工具函数
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, average_precision_score
from sklearn.preprocessing import label_binarize
from itertools import cycle
from typing import Any, Optional, Tuple, Dict, Union
import matplotlib.axes as axes
import matplotlib.figure as figure


def plot_precision_recall_curve(
    y_true: Any, 
    y_pred_proba: Optional[np.ndarray], 
    class_names: Optional[list] = None, 
    figsize: Tuple[int, int] = (8, 6)
) -> Tuple[figure.Figure, axes.Axes]:
    """
    绘制精确率-召回率曲线
    
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
        binary_precision, binary_recall, _ = precision_recall_curve(y_true, y_pred_proba[:, 1])
        binary_average_precision = average_precision_score(y_true, y_pred_proba[:, 1])
        
        ax.plot(binary_recall, binary_precision, label=f'精确率-召回率曲线 (AP = {binary_average_precision:.2f})')
        ax.set_xlabel('召回率')
        ax.set_ylabel('精确率')
        ax.set_title('精确率-召回率曲线')
        ax.legend(loc="lower left")
    else:
        # 处理多分类情况
        classes = np.unique(y_true)
        y_true_bin_result = label_binarize(y_true, classes=classes)
        
        # 检查y_true_bin是否有效，并确保不是None
        if y_true_bin_result is None:
            raise ValueError("无法对真实标签进行二值化处理")
        
        # 转换为数组以确保类型安全
        y_true_bin_array: np.ndarray = np.asarray(y_true_bin_result)
        n_classes = y_true_bin_array.shape[1]
        
        # 明确声明变量类型
        multi_precision: Dict[int, np.ndarray] = dict()
        multi_recall: Dict[int, np.ndarray] = dict()
        multi_average_precision: Dict[int, float] = dict()
        
        colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'red', 'green', 'purple'])
        
        for i, color in zip(range(n_classes), colors):
            precision_vals, recall_vals, _ = precision_recall_curve(y_true_bin_array[:, i], y_pred_proba[:, i])
            multi_precision[i] = precision_vals
            multi_recall[i] = recall_vals
            multi_average_precision[i] = float(average_precision_score(y_true_bin_array[:, i], y_pred_proba[:, i]))
            class_name = class_names[i] if class_names and i < len(class_names) else f'类别 {i}'
            ax.plot(multi_recall[i], multi_precision[i], color=color, lw=2,
                   label=f'{class_name} (AP = {multi_average_precision[i]:.2f})')
        
        ax.set_xlabel('召回率')
        ax.set_ylabel('精确率')
        ax.set_title('多分类精确率-召回率曲线')
        ax.legend(loc="lower left")
    
    return fig, ax