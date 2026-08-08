"""
策略调度器
自动选择最佳图表类型（如分类任务默认用混淆矩阵）
"""

from typing import Dict, Any, List
from .base_visualization import VisualizationStrategy


class VisualizationStrategySelector:
    """
    可视化策略选择器
    根据任务类型和数据特征自动选择最佳的图表类型
    """

    def __init__(self):
        """
        初始化策略选择器
        """
        pass

    def select_charts_for_classification(self, params: Dict[str, Any]) -> List[str]:
        """
        为分类任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        # 默认选择混淆矩阵作为分类任务的首选图表
        selected_charts = ["confusion_matrix"]
        
        # 根据类别数量决定是否添加其他图表
        y_test = params.get("y_test")
        if y_test is not None:
            unique_classes = len(set(y_test))
            if unique_classes == 2:
                # 二分类任务添加ROC曲线和精确率-召回率曲线
                selected_charts.extend(["roc_curve", "precision_recall_curve"])
            else:
                # 多分类任务添加各类别的ROC曲线
                selected_charts.append("roc_curve")
        
        return selected_charts

    def select_charts_for_regression(self, params: Dict[str, Any]) -> List[str]:
        """
        为回归任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        # 回归任务默认选择实际值vs预测值图和残差图
        return ["actual_vs_predicted", "residuals_plot"]

    def select_charts_for_clustering(self, params: Dict[str, Any]) -> List[str]:
        """
        为聚类任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        # 聚类任务默认选择聚类散点图和聚类柱状图
        return ["cluster_scatter", "cluster_bar"]

    def select_charts_for_transformer(self, params: Dict[str, Any]) -> List[str]:
        """
        为变换器任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        # 变换器任务默认选择变换前后分布对比图
        return ["before_after_distribution"]

    def select_charts_for_common(self, params: Dict[str, Any]) -> List[str]:
        """
        为通用图表任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        # 通用图表直接返回任务列表中的图表类型
        task_list = params.get("task_list", [])
        return task_list if task_list else ["scatter"]

    def select_charts(self, task_type: str, params: Dict[str, Any]) -> List[str]:
        """
        根据任务类型选择图表
        
        Args:
            task_type: 任务类型
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        if task_type == "classification":
            return self.select_charts_for_classification(params)
        elif task_type == "regression":
            return self.select_charts_for_regression(params)
        elif task_type == "clustering":
            return self.select_charts_for_clustering(params)
        elif task_type == "transformer":
            return self.select_charts_for_transformer(params)
        elif task_type == "common":
            return self.select_charts_for_common(params)
        else:
            # 默认返回散点图
            return ["scatter"]