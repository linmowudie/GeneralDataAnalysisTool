# visualization/plots/decisiontreeclassifier.py
"""
Src/DataAnalyzer/visualization/plots/decisiontreeclassifier.py
决策树分类器可视化模块

该模块提供决策树分类器模型的可视化功能，
包括决策树结构图的绘制。
"""

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.tree import plot_tree
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure


@plot_registry.register("classification", "decisiontreeclassifier")
def plot_decisiontreeclassifier(params: Dict[str, Any]) -> Dict[str, Figure]:
    figures = {}
    target = params["target"]
    predict = params["predict"]
    feature = params["feature"]
    label_style = params.get("label_style", {})
    shape_style = params.get("shape_style", {})
    point_colors = shape_style.get("points", {}).get("colors", ["tab:blue"])
    model = params.get("model_specific", {}).get("trained_model")

    # 1. 混淆矩阵
    cm = confusion_matrix(target, predict)
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax1)
    ax1.set(
        title=label_style.get("title", "Confusion Matrix") or "Confusion Matrix",
        xlabel="Predicted",
        ylabel="Actual"
    )
    figures["confusion_matrix"] = fig1

    # 2. 特征重要性
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        feat_names = feature.columns
        idx = importances.argsort()[::-1][:10]  # 取前 10
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.barh(range(len(idx)), importances[idx], color=point_colors[0])
        ax2.set_yticks(range(len(idx)))
        ax2.set_yticklabels([feat_names[i] for i in idx])
        ax2.invert_yaxis()
        ax2.set(title="Top 10 Feature Importances")
        figures["feature_importance"] = fig2

    # 3. 决策树结构（深度 <=3，防止图过大）
    if model is not None:
        fig3, ax3 = plt.subplots(figsize=(12, 8))
        plot_tree(
            model,
            feature_names=feature.columns,
            class_names=[str(c) for c in target.unique()],
            filled=True,
            max_depth=3,
            ax=ax3
        )
        figures["decision_tree"] = fig3

    return figures