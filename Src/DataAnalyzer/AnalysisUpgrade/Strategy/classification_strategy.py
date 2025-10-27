"""
分类任务策略（训练+评估）
"""

from ..Cores.base_strategy import BaseStrategy
from typing import Dict, Any
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class ClassificationStrategy(BaseStrategy):
    """
    分类任务策略类，控制分类分析流程的执行顺序和逻辑
    """
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行分类分析策略
        
        参数:
            **kwargs: 分析参数
                - df: 数据集
                - feature_cols: 特征列名列表
                - target_col: 目标列名
                - model: 模型实例
                - is_split: 是否分割数据集
                - split_ratio: 分割比例
                - metrics_list: 评估指标列表
                
        返回:
            Dict[str, Any]: 分析结果
        """
        try:
            df = kwargs.get("df")
            feature_cols = kwargs.get("feature_cols", [])
            target_col = kwargs.get("target_col")
            model = kwargs.get("model")
            is_split = kwargs.get("is_split", True)
            split_ratio = kwargs.get("split_ratio", 0.2)
            metrics_list = kwargs.get("metrics_list", ["accuracy"])
            
            if df is None or not feature_cols or target_col is None or model is None:
                return {"error": "缺少必要的参数: df, feature_cols, target_col, model"}
            
            # 准备数据
            X = df[feature_cols]
            y = df[target_col]
            
            # 数据分割
            if is_split:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=split_ratio, random_state=42
                )
            else:
                X_train, X_test, y_train, y_test = X, X, y, y
            
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测
            y_pred = model.predict(X_test)
            
            # 计算评估指标
            results = {
                "model": model,
                "predictions": y_pred.tolist(),
                "train_shape": getattr(X_train, 'shape', (len(X_train), len(X_train[0]) if hasattr(X_train, '__getitem__') and len(X_train) > 0 else 0)),
                "test_shape": getattr(X_test, 'shape', (len(X_test), len(X_test[0]) if hasattr(X_test, '__getitem__') and len(X_test) > 0 else 0))
            }
            
            metrics = {}
            for metric in metrics_list:
                try:
                    if metric == "accuracy":
                        metrics[metric] = float(accuracy_score(y_test, y_pred))
                    elif metric == "precision":
                        metrics[metric] = float(precision_score(y_test, y_pred, average='weighted'))
                    elif metric == "recall":
                        metrics[metric] = float(recall_score(y_test, y_pred, average='weighted'))
                    elif metric == "f1":
                        metrics[metric] = float(f1_score(y_test, y_pred, average='weighted'))
                except Exception as e:
                    metrics[metric] = f"计算出错: {str(e)}"
            
            results["metrics"] = metrics
            return results
            
        except Exception as e:
            return {"error": f"执行分类分析策略时出错: {str(e)}"}

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        验证分类任务参数
        
        参数:
            params (Dict[str, Any]): 参数字典
            
        返回:
            bool: 验证是否通过
        """
        # 实现分类任务特定的参数验证逻辑
        required_params = ["df", "feature_cols", "target_col"]
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
            
        target_col = params["target_col"]
        if not isinstance(target_col, str):
            print("target_col必须是字符串类型")
            return False
            
        # 检查列是否存在
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            print(f"以下特征列在数据中不存在: {missing_cols}")
            return False
            
        if target_col not in df.columns:
            print(f"目标列 {target_col} 在数据中不存在")
            return False
            
        return True