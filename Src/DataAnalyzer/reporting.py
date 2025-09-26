"""
Src/DataAnalyzer/reporting.py
报告生成模块

该模块负责生成数据分析报告，包括结果汇总、图表展示
和分析结论等内容。
"""

import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)    

class Report:

    def __init__(
            self,
            model_params: Optional[Dict] = None,
            model_scores: Optional[Dict] = None,
            visualizations: Optional[Dict] = None,
            model_predictions: Optional[pd.Series] = None,    
            ):
        """
        :param model_params:模型参数
        :param model_scores:模型得分
        :param model_predictions:模型预测结果
        :param visualizations:可视化结果
        """
        self.model_params = model_params
        self.model_scores = model_scores
        self.visualizations = visualizations
        self.model_predictions = model_predictions

    def return_report(self) -> Dict:
        """
        返回报告内容
        """
        report = {
            "model_params": self.model_params,
            "model_scores": self.model_scores,
            "visualizations": self.visualizations,
            "model_predictions": self.model_predictions
        }
        try:
            to_move = [ key for key, value in report.items() if value is None]
            for key in to_move:
                report.pop(key, None)

        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error: {e}")
            report = {}
            
        return report