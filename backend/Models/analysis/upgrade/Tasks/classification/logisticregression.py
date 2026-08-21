from ...Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, List, Optional, Union

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class LogisticRegressionAnalyzer(BaseAnalyzer):

    def __init__(self):
        super().__init__()

    def load_params(self, model_name: str) -> Dict[str, Any]:
        """
        从配置文件加载逻辑回归模型的参数
        """
        # 使用基类提供的模板方法加载参数
        return self.load_model_params(model_name, "classification")

    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        
        # 声明结果结构
        result: Dict[str, Any] = {}
        result["is_valid"] = True

        # 检验输入参数是否为空
        if params is None:
            result["is_valid"] = False
            logger.error("输入参数为空")
            return result

        # 一些参数的基本信息
        logger.info(f"学习类型为{params.get('learn_type')}，模型类型为{params.get('model_type')}")
        logger.info(f"模型为{params.get('model')}")

        if params.get("random_state") is None:
            logger.warning("未指定随机种子，将使用默认值42")

        if params.get("is_split") is None:
            logger.warning("未指定是否进行数据集分割，将使用默认值True，并且使用默认划分比例：0.8")

        if params.get("split_ratio") is None:
            logger.warning("未指定数据集划分比例，将使用默认值0.8")

        if params.get("feature_cols") is None:
            logger.warning("未指定特征列，将使用所有列，如果数据集包含目标列，可能会出现无法进行数据分析")

        if params.get("target_col") is None:
            logger.warning("未指定目标列，将使用最后一列作为目标列")

        if params.get("metrics_list") is None:
            logger.warning("未指定评估指标，将使用默认值：['accuracy_score', 'precision_score', 'recall_score', 'f1_score']")

        if params.get("is_return_model_score") is None:
            logger.warning("未指定是否返回模型得分，将使用默认值True")
        
        if params.get("feature_cols_encoding") is None:
            logger.warning("未指定特征列编码方式，将使用默认值：'onehot'")

        if params.get("target_col_encoding") is None:
            logger.warning("未指定目标列编码方式，将使用默认值：'label'")

        if params.get("test_set") is not None and params.get("is_split") is True:
            logger.info("已指定测试集")
            result["is_valid"] = False
            return result

        if params.get("model_params") is not None:
            logger.info("已指定模型参数")
            logger.info("将会采用过滤法指定模型支持的全部参数")
            result["input_params"] = True

        else:
            logger.info("未指定模型参数，将使用默认参数,但是大概率训练出错")

        if params.get("default_model_params") is not None:
            logger.info(f"默认参数已加载，结果如下{params.get('default_model_params')}")

        if params.get("model_info"):
            logger.info(f"模型信息已加载，结果如下{params.get('model_info')}")
        
        else:
            logger.warning("模型信息加载失败")
            result["is_valid"] = False
        
        return result
        

    def replace_params(self, default_params: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        invalid_keys = []

        for key in params:
            if key != "key_description" and key not in default_params:
                invalid_keys.append(key)

        if invalid_keys:
            print(f"发现无效参数，已忽略: {invalid_keys}")

        for key, default_value in default_params.items():
            if key == "key_description":
                continue
            result[key] = params.get(key, default_value)

        return result

    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> tuple:
        """
        对数据进行预处理，包括缺失值填充和特征编码
        """
        # 填充缺失值
        X_processed = self.fill_missing_values(X, X.columns.tolist())
        
        # 特征编码
        X_processed = self.feature_set_encoding(X_processed, "auto")
        
        y_processed = y
        if y is not None:
            # 如果目标列存在，则对其进行编码
            y_processed, _ = self.target_col_encoding(y, "label")
            
        return X_processed, y_processed

    def train(self, X_train: pd.DataFrame, y_train: Optional[pd.Series]) -> Any:
        """
        使用训练数据拟合逻辑回归模型
        """
        # 确保模型实例已创建
        if self._model_instance is None:
            raise ValueError("模型实例未创建，请先调用 instantiate_model 方法")
            
        # 调用模型的fit方法进行训练
        self._model_instance.fit(X_train, y_train)
        return self._model_instance

    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        """
        训练后处理，提取模型的系数和截距等信息
        """
        result = {}
        
        # 获取模型系数
        if hasattr(model, 'coef_'):
            coef = model.coef_
            if isinstance(coef, np.ndarray):
                result['coefficients'] = coef.tolist()
            else:
                result['coefficients'] = coef
            
        # 获取模型截距
        if hasattr(model, 'intercept_'):
            intercept = model.intercept_
            if isinstance(intercept, np.ndarray):
                result['intercept'] = intercept.tolist()
            else:
                result['intercept'] = intercept
            
        # 获取特征名称
        if hasattr(model, 'feature_names_in_'):
            feature_names = model.feature_names_in_
            if isinstance(feature_names, np.ndarray):
                result['feature_names'] = feature_names.tolist()
            else:
                result['feature_names'] = feature_names
            
        # 获取类别信息
        if hasattr(model, 'classes_'):
            classes = model.classes_
            if isinstance(classes, np.ndarray):
                result['classes'] = classes.tolist()
            else:
                result['classes'] = classes
            
        return result

    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        获取逻辑回归模型的特征重要性（系数的绝对值）
        """
        # 获取特征名称
        feature_names = getattr(model, 'feature_names_in_', None)
        
        # 获取系数
        coef = getattr(model, 'coef_', None)
        
        if feature_names is None or coef is None:
            return {}
            
        # 对于二分类或多分类，我们取系数的平均绝对值
        if coef.ndim == 1:
            importance_values = np.abs(coef)
        else:
            # 多分类情况，取所有类别系数的平均绝对值
            importance_values = np.mean(np.abs(coef), axis=0)
            
        # 创建特征重要性字典
        feature_importance = dict(zip(feature_names, importance_values))
        return feature_importance

    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """
        保存模型及相关产物
        """
        try:
            import joblib
            # 保存模型
            joblib.dump(model, f"{filepath}.joblib")
            
            # 保存编码器
            if self._fitted_encoders:
                joblib.dump(self._fitted_encoders, f"{filepath}_encoders.joblib")
                
            return True
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
            return False

    def predict(self, model: Any, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """
        使用训练好的模型进行预测
        """
        # 进行预测
        predictions = model.predict(X)
        
        # 如果有编码器，尝试还原标签
        if "target" in self._fitted_encoders:
            try:
                predictions = self._fitted_encoders["target"].inverse_transform(predictions)
            except Exception as e:
                logger.warning(f"标签解码失败: {e}")
                
        return pd.Series(predictions, index=X.index)

    def get_default_metrics(self, model_type: str) -> List[str]:
        """
        获取逻辑回归的默认评估指标
        """
        if model_type == "classification":
            return ["accuracy", "precision", "recall", "f1_score"]
        return []

    def build_result(self, 
                     model: Any,
                     model_score: Optional[Dict[str, float]],
                     feature_importance: Dict[str, float],
                     postprocess_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建并返回最终结果字典

        参数:
            model (Any): 训练完成的模型
            model_score (Optional[Dict[str, float]]): 模型评估得分
            feature_importance (Dict[str, float]): 特征重要性
            postprocess_result (Dict[str, Any]): 后处理结果

        返回:
            Dict[str, Any]: 完整的分析结果
            key: value
            {
                "model": object,
                "model_score": dict,
                "train_set": pd.DataFrame,
                "test_set": pd.DataFrame,
                "feature_cols": list[str],
                "encodeing_method": Dict[str, str]
            }
        """
        result = {
            "model": model,
            "model_score": model_score,
            "feature_importance": feature_importance,
            "postprocess_result": postprocess_result
        }
        return result
