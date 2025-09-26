# visualization/plots/kneighborsclassifier.py
"""
Src/DataAnalyzer/visualization/plots/kneighborsclassifier.py
K近邻分类器可视化模块

该模块提供K近邻分类器模型的可视化功能，
包括分类结果的可视化展示。
"""

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
import numpy as np
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure


@plot_registry.register("classification", "kneighborsclassifier")
def plot_kneighborsclassifier(params: Dict[str, Any]) -> Dict[str, Figure]:
    figures = {}
    target = params["target"]
    predict = params["predict"]
    feature = params["feature"]
    label_style = params.get("label_style", {})
    shape_style = params.get("shape_style", {})
    point_colors = shape_style.get("points", {}).get("colors", ["tab:blue"])

    # 1. 混淆矩阵
    cm = confusion_matrix(target, predict)
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Greens", ax=ax1)
    ax1.set(title="Confusion Matrix", xlabel="Predicted", ylabel="Actual")
    figures["confusion_matrix"] = fig1

    # 2. ROC 曲线（仅二分类）
    classes = np.unique(target)
    if len(classes) == 2:
        y_score = params.get("model_specific", {}).get("y_score")  # 需要外部传入 prob[:,1]
        if y_score is not None:
            fpr, tpr, _ = roc_curve(target, y_score)
            roc_auc = auc(fpr, tpr)
            fig2, ax2 = plt.subplots()
            ax2.plot(fpr, tpr, color=point_colors[0], lw=2,
                     label=f"ROC curve (AUC = {roc_auc:.2f})")
            ax2.plot([0, 1], [0, 1], "k--", lw=1)
            ax2.set(xlim=[0.0, 1.0], ylim=[0.0, 1.05],
                    title="ROC Curve", xlabel="False Positive Rate", ylabel="True Positive Rate")
            ax2.legend(loc="lower right")
            figures["roc_curve"] = fig2

    # 3. 特征空间决策边界（仅二维）
    if feature.shape[1] == 2:
        fig3, ax3 = plt.subplots()
        x_min, x_max = feature.iloc[:, 0].min() - 1, feature.iloc[:, 0].max() + 1
        y_min, y_max = feature.iloc[:, 1].min() - 1, feature.iloc[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                             np.linspace(y_min, y_max, 300))
        mesh = np.c_[xx.ravel(), yy.ravel()]
        model = params.get("model_specific", {}).get("trained_model")
        if model:
            Z = model.predict(mesh).reshape(xx.shape)
            ax3.contourf(xx, yy, Z, alpha=0.3, cmap= plt.get_cmap('coolwarm')) 
            sns.scatterplot(x=feature.iloc[:, 0], y=feature.iloc[:, 1],
                            hue=target, palette="Set2", ax=ax3, edgecolor="k")
            ax3.set(title="Decision Boundary", xlabel=feature.columns[0], ylabel=feature.columns[1])
            figures["decision_boundary"] = fig3

    return figures