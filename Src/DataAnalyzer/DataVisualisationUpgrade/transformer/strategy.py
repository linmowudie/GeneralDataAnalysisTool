"""
变换策略：根据变换类型选择图表
"""

from typing import Dict, Any, List


class TransformerStrategySelector:
    """
    变换器任务策略选择器
    根据变换器的类型和数据特征选择合适的图表类型
    """

    def select_charts(self, params: Dict[str, Any]) -> List[str]:
        """
        为变换器任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        selected_charts = []
        
        # 获取模型名称和类型
        model_name = params.get("model_name", "").lower()
        
        # 根据模型类型选择图表
        if "scaler" in model_name or "normalizer" in model_name:
            # 标准化/归一化类变换器
            selected_charts.extend([
                "before_after_distribution",
                "scaled_features_box"
            ])
        elif "pca" in model_name:
            # PCA降维
            selected_charts.extend([
                "explained_variance",
                "principal_components_scatter",
                "biplot"
            ])
        elif "tsne" in model_name:
            # t-SNE降维
            selected_charts.extend([
                "embedding_scatter",
                "perplexity_comparison"
            ])
        elif "umap" in model_name:
            # UMAP降维
            selected_charts.extend([
                "embedding_scatter",
                "connectivity_plot"
            ])
        elif "three_d" in model_name:
            # 3D投影
            selected_charts.extend([
                "scatter_3d",
                "surface_3d",
                "wireframe_3d"
            ])
        elif "no_model" in model_name:
            # 无模型图表
            task_list = params.get("task_list", [])
            selected_charts.extend(task_list)
        else:
            # 默认变换器图表
            selected_charts.append("before_after_distribution")
        
        return selected_charts