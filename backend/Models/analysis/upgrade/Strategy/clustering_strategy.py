"""
聚类任务策略
"""

from ..Cores.base_strategy import BaseStrategy
from typing import Dict, Any
import pandas as pd
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score


class ClusteringStrategy(BaseStrategy):
    """
    聚类任务策略类，控制聚类分析流程的执行顺序和逻辑
    """
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行聚类分析策略
        
        参数:
            **kwargs: 分析参数
                - df: 数据集
                - feature_cols: 特征列名列表
                - model: 模型实例
                - metrics_list: 评估指标列表
                
        返回:
            Dict[str, Any]: 分析结果
        """
        try:
            df = kwargs.get("df")
            feature_cols = kwargs.get("feature_cols", [])
            model = kwargs.get("model")
            metrics_list = kwargs.get("metrics_list", ["silhouette", "calinski_harabasz", "davies_bouldin"])
            
            if df is None or not feature_cols or model is None:
                return {"error": "缺少必要的参数: df, feature_cols, model"}
            
            # 准备数据
            X = df[feature_cols]
            
            # 训练模型
            labels = model.fit_predict(X)
            
            # 计算评估指标
            results = {
                "model": model,
                "labels": labels.tolist(),
                "data_shape": X.shape if hasattr(X, 'shape') else None
            }
            
            metrics = {}
            for metric in metrics_list:
                try:
                    if metric == "silhouette" and len(set(labels)) > 1:
                        metrics[metric] = float(silhouette_score(X, labels))
                    elif metric == "calinski_harabasz" and len(set(labels)) > 1:
                        metrics[metric] = float(calinski_harabasz_score(X, labels))
                    elif metric == "davies_bouldin" and len(set(labels)) > 1:
                        metrics[metric] = float(davies_bouldin_score(X, labels))
                    elif len(set(labels)) <= 1:
                        metrics[metric] = "无法计算: 只有一个簇或所有点属于同一簇"
                except Exception as e:
                    metrics[metric] = f"计算出错: {str(e)}"
            
            results["metrics"] = metrics
            return results
            
        except Exception as e:
            return {"error": f"执行聚类分析策略时出错: {str(e)}"}

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        验证聚类任务参数
        
        参数:
            params (Dict[str, Any]): 参数字典
            
        返回:
            bool: 验证是否通过
        """
        # 实现聚类任务特定的参数验证逻辑
        required_params = ["df", "feature_cols"]
        for param in required_params:
            if param not in params:
                print(f"缺少必要参数: {param}")
                return False
        
        # 验证数据类型
        df = params["df"]
        if not isinstance(df, pd.DataFrame):
            print("df必须是pandas DataFrame类型")
            return False
            
        feature_cols = params["feature_cols"]
        if not isinstance(feature_cols, list):
            print("feature_cols必须是列表类型")
            return False
            
        # 检查列是否存在
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            print(f"以下特征列在数据中不存在: {missing_cols}")
            return False
            
        return True