# visualization/plots/logisticregression.py
"""
Src/DataAnalyzer/VisualizationModule/Plots/logisticregression.py
逻辑回归可视化模块

该模块提供逻辑回归模型的可视化功能，
包括决策边界和分类结果的可视化展示。
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix, roc_curve, auc, classification_report
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure
import logging
import pandas as pd

logger = logging.getLogger(__name__)

@plot_registry.register("classification", "logisticregression")
def plot_logisticregression(params: Dict[str, Any]) -> Dict[str, Figure]:
    logger.debug("开始执行逻辑回归可视化")
    logger.debug(f"参数: {params.keys()}")
    figures = {}
    target = params["target"]
    predict = params["predict"]
    feature = params["feature"]
    label_style = params.get("label_style", {})
    shape_style = params.get("shape_style", {})
    point_colors = shape_style.get("points", {}).get("colors", ["tab:blue"])

    try:
        # 确保target和predict具有一致的索引
        if isinstance(target, pd.Series) and isinstance(predict, np.ndarray):
            # 如果predict是numpy数组，将其转换为具有相同索引的Series
            predict = pd.Series(predict, index=target.index)
        elif isinstance(target, pd.Series) and isinstance(predict, pd.Series):
            # 如果两者都是Series，获取共同索引
            common_index = target.index.intersection(predict.index)
            target = target.loc[common_index]
            predict = predict.loc[common_index]
        
        # 1. 混淆矩阵
        logger.debug("生成混淆矩阵")
        cm = confusion_matrix(target, predict)
        fig1, ax1 = plt.subplots(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax1)
        ax1.set(title=label_style.get("title", "Confusion Matrix") or "Confusion Matrix", 
                xlabel="Predicted", ylabel="Actual")
        figures["confusion_matrix"] = fig1

        # 2. ROC 曲线
        logger.debug("生成ROC曲线")
        y_score = params.get("model_specific", {}).get("y_score")
        if y_score is not None:
            # 确保y_score和target具有一致的索引
            if isinstance(y_score, np.ndarray) and isinstance(target, pd.Series):
                y_score = pd.Series(y_score, index=target.index)
            
            fpr, tpr, _ = roc_curve(target, y_score)
            roc_auc = auc(fpr, tpr)
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.plot(fpr, tpr, color=point_colors[0], lw=2,
                     label=f"ROC curve (AUC = {roc_auc:.3f})")
            ax2.plot([0, 1], [0, 1], "k--", lw=1)
            ax2.set(xlim=[0.0, 1.0], ylim=[0.0, 1.05],
                    title="ROC Curve", xlabel="False Positive Rate", ylabel="True Positive Rate")
            ax2.legend(loc="lower right")
            ax2.grid(True, alpha=0.3)
            figures["roc_curve"] = fig2
        else:
            logger.warning("未提供y_score，跳过ROC曲线绘制")

        # 3. 回归系数（柱状图）
        logger.debug("生成回归系数图")
        model = params.get("model_specific", {}).get("trained_model")
        if model and hasattr(model, "coef_"):
            coef = model.coef_.ravel()
            # 确保特征列存在
            if hasattr(feature, 'columns') and len(feature.columns) > 0:
                top_n = min(15, len(coef))
                idx = np.argsort(np.abs(coef))[-top_n:]
                fig3, ax3 = plt.subplots(figsize=(8, max(4, top_n * 0.3)))  # 根据特征数量调整高度
                bars = ax3.barh(range(top_n), coef[idx], color=point_colors[0])
                ax3.set_yticks(range(top_n))
                ax3.set_yticklabels([feature.columns[i] for i in idx])
                ax3.invert_yaxis()
                ax3.set(title="Feature Coefficients (Top 15 by Absolute Value)")
                ax3.set_xlabel("Coefficient Value")
                ax3.grid(True, alpha=0.3)
                
                # 在每个条形上添加数值标签
                for i, (bar, coeff) in enumerate(zip(bars, coef[idx])):
                    ax3.text(bar.get_width() + (0.01 * np.sign(coeff) * np.max(np.abs(coef))), 
                            bar.get_y() + bar.get_height()/2, 
                            f'{coeff:.3f}', 
                            ha='left' if coeff >= 0 else 'right', 
                            va='center')
                
                figures["coefficients"] = fig3
            else:
                logger.warning("特征列信息不可用，跳过系数图绘制")
        else:
            logger.warning("模型或系数信息不可用，跳过系数图绘制")

    except Exception as e:
        logger.error(f"逻辑回归可视化过程中出现错误: {str(e)}")
        raise
    
    logger.debug(f"逻辑回归可视化完成，生成了 {len(figures)} 个图表")
    return figures