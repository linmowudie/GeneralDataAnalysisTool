"""
通用图表选择策略（如数据量大用散点，小用气泡）
"""

from typing import Dict, Any, List, Optional
import numpy as np


class CommonStrategySelector:
    """
    通用图表策略选择器
    根据数据量和特征选择合适的通用图表类型
    """

    def select_charts(self, params: Dict[str, Any]) -> List[str]:
        """
        为通用图表任务选择图表类型
        
        Args:
            params: 参数字典
            
        Returns:
            图表类型列表
        """
        selected_charts = []
        
        # 获取任务列表
        task_list = params.get("task_list", [])
        if task_list:
            # 如果指定了任务列表，则直接返回
            return task_list
        
        # 获取数据
        X = params.get("X")
        y = params.get("y")
        
        if X is not None:
            X = np.array(X)
            n_samples, n_features = X.shape
            
            # 根据数据量和特征数选择图表
            if n_samples > 1000:
                # 数据量大时选择散点图
                selected_charts.append("scatter")
            elif n_samples > 100:
                # 中等数据量选择散点图
                selected_charts.append("scatter")
            else:
                # 小数据量选择折线图或柱状图
                selected_charts.append("line")
                
            # 根据特征数选择额外图表
            if n_features > 1:
                if n_features <= 5:
                    # 特征数较少时添加成对图
                    selected_charts.append("pair_plot")
                else:
                    # 特征数较多时添加热力图
                    selected_charts.append("heatmap")
                    
        else:
            # 默认选择散点图
            selected_charts.append("scatter")
        
        return selected_charts


class ChartTypeSelector:
    """
    图表类型选择器
    根据数据特征选择最适合的图表类型
    """
    
    @staticmethod
    def select_for_data_shape(X: np.ndarray, y: Optional[np.ndarray] = None) -> List[str]:
        """
        根据数据形状选择图表类型
        
        Args:
            X: 特征数据
            y: 目标数据（可选）
            
        Returns:
            推荐的图表类型列表
        """
        n_samples, n_features = X.shape
        
        chart_types = []
        
        # 根据样本数量选择
        if n_samples > 1000:
            chart_types.append("scatter")
        elif n_samples > 100:
            chart_types.append("scatter")
        elif n_samples > 10:
            chart_types.append("line")
        else:
            chart_types.append("bar")
            
        # 根据特征数量选择
        if n_features > 1:
            chart_types.append("heatmap")
            
        # 如果有目标值且是分类数据
        if y is not None:
            unique_values = len(np.unique(y))
            if unique_values <= 20:  # 假设类别数不超过20为分类任务
                chart_types.append("bar")
            else:
                chart_types.append("histogram")
                
        return chart_types
    
    @staticmethod
    def select_for_analysis_purpose(purpose: str) -> List[str]:
        """
        根据分析目的选择图表类型
        
        Args:
            purpose: 分析目的（'distribution', 'correlation', 'comparison', 'composition'）
            
        Returns:
            推荐的图表类型列表
        """
        purpose_chart_map = {
            "distribution": ["histogram", "box_plot"],
            "correlation": ["scatter", "heatmap"],
            "comparison": ["bar", "line"],
            "composition": ["pie", "bar"]
        }
        
        return purpose_chart_map.get(purpose, ["scatter"])