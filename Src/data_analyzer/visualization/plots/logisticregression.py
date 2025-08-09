# data_visualization/plots/logisticregression.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix, roc_curve, auc
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure


@plot_registry.register("classification", "logisticregression")
def plot_logisticregression(params: Dict[str, Any]) -> Dict[str, Figure]:
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
    sns.heatmap(cm, annot=True, fmt="d", cmap="Purples", ax=ax1)
    ax1.set(title="Confusion Matrix", xlabel="Predicted", ylabel="Actual")
    figures["confusion_matrix"] = fig1

    # 2. ROC 曲线
    y_score = params.get("model_specific", {}).get("y_score")
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

    # 3. 回归系数（柱状图）
    model = params.get("model_specific", {}).get("trained_model")
    if model and hasattr(model, "coef_"):
        coef = model.coef_.ravel()
        top_n = min(15, len(coef))
        idx = np.argsort(np.abs(coef))[-top_n:]
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.barh(range(top_n), coef[idx], color=point_colors[0])
        ax3.set_yticks(range(top_n))
        ax3.set_yticklabels([feature.columns[i] for i in idx])
        ax3.invert_yaxis()
        ax3.set(title="Top 15 |Coefficients|")
        figures["coefficients"] = fig3

    return figures