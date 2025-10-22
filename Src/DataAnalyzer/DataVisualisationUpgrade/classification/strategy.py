"""
分类内部策略：根据二分类/多分类选择不同图表
"""

from typing import Dict, Any, List


class ClassificationStrategySelector:
    """
    分类任务策略选择器
    根据分类任务的特点选择合适的图表类型
    """

    def select_charts(self, params: Dict[str, Any]) -> List[str]:
        """
        为分类任务选择图表类型
        
        Args:
            params: 参数字典，应包含y_test等信息
            
        Returns:
            图表类型列表
        """
        selected_charts = []
        
        # 获取测试标签
        y_test = params.get("y_test")
        if y_test is None:
            # 如果没有测试标签，则返回默认图表
            return ["confusion_matrix"]
        
        # 获取类别数量
        unique_classes = len(set(y_test))
        
        # 添加基本图表
        selected_charts.append("confusion_matrix")
        
        # 根据类别数量选择额外图表
        if unique_classes == 2:
            # 二分类任务
            selected_charts.extend([
                "roc_curve",
                "precision_recall_curve",
                "calibration_curve"
            ])
        else:
            # 多分类任务
            selected_charts.append("roc_curve")
            
        # 检查模型是否支持概率预测
        model = params.get("model")
        if model and hasattr(model, "predict_proba"):
            try:
                model.predict_proba(params.get("X_test", []))
                selected_charts.append("calibration_curve")
            except:
                pass
        
        return selected_charts