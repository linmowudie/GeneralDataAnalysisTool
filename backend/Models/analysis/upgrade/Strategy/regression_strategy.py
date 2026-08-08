"""
回归任务策略
"""

from ..Cores.base_strategy import BaseStrategy
from typing import Dict, Any
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np


class RegressionStrategy(BaseStrategy):
    """
    回归任务策略类，控制回归分析流程的执行顺序和逻辑
    """
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行回归分析策略
        
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
            metrics_list = kwargs.get("metrics_list", ["mse", "rmse", "mae", "r2"])
            
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
                "predictions": y_pred.tolist()
            }
            
            # 获取形状信息
            try:
                # 使用类型检查避免错误
                if not isinstance(X_train, list) and hasattr(X_train, 'shape'):
                    results["train_shape"] = X_train.shape
                if not isinstance(X_test, list) and hasattr(X_test, 'shape'):
                    results["test_shape"] = X_test.shape
            except:
                # 如果无法获取形状信息，跳过
                pass
            
            metrics = {}
            for metric in metrics_list:
                try:
                    if metric == "mse":
                        metrics[metric] = float(mean_squared_error(y_test, y_pred))
                    elif metric == "rmse":
                        metrics[metric] = float(np.sqrt(mean_squared_error(y_test, y_pred)))
                    elif metric == "mae":
                        metrics[metric] = float(mean_absolute_error(y_test, y_pred))
                    elif metric == "r2":
                        metrics[metric] = float(r2_score(y_test, y_pred))
                except Exception as e:
                    metrics[metric] = f"计算出错: {str(e)}"
            
            results["metrics"] = metrics
            return results
            
        except Exception as e:
            return {"error": f"执行回归分析策略时出错: {str(e)}"}

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        验证回归任务参数
        
        参数:
            params (Dict[str, Any]): 参数字典
            
        返回:
            bool: 验证是否通过
        """
        # 实现回归任务特定的参数验证逻辑
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