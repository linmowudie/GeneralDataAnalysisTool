# data_visualization/plots/standardscaler.py
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any
from ..registry import plot_registry
from matplotlib.figure import Figure
import pandas as pd


@plot_registry.register("transformer", "standardscaler")
def plot_standardscaler(params: Dict[str, Any]) -> Dict[str, Figure]:
    figures = {}
    feature = params["feature"]
    transformed = params.get("model_specific", {}).get("transformed")
    if transformed is None:
        # 说明未给出变换后矩阵，直接返回空
        return figures

    df_original = feature
    df_scaled = pd.DataFrame(transformed, columns=feature.columns)

    # 1. 原始 vs 缩放后分布对比
    n_cols = min(6, len(df_original.columns))
    cols = df_original.columns[:n_cols]
    fig1, axes = plt.subplots(nrows=n_cols, ncols=2, figsize=(10, 4 * n_cols))
    for i, col in enumerate(cols):
        sns.histplot(df_original[col], kde=True, ax=axes[i, 0], color="steelblue")
        axes[i, 0].set_title(f"Original: {col}")
        sns.histplot(df_scaled[col], kde=True, ax=axes[i, 1], color="seagreen")
        axes[i, 1].set_title(f"Scaled: {col}")
    plt.tight_layout()
    figures["distribution_comparison"] = fig1

    # 2. 箱线图查看异常值
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.boxplot(data=df_scaled, orient="h", ax=ax2)
    ax2.set(title="Scaled Features Boxplot")
    figures["boxplot_scaled"] = fig2

    return figures