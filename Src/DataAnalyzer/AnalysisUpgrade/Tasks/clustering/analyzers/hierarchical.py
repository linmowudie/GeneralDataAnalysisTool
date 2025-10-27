"""
Hierarchical Clustering
这里将实现层次聚类的具体分析逻辑
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
import io
import base64


class HierarchicalClusteringAnalyzer(BaseAnalyzer):
    """
    层次聚类分析器
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.scaler = None
        self.config = None
        self.linkage_matrix = None
        self._load_config()
    
    def _load_config(self):
        """
        从配置文件加载参数配置
        """
        try:
            # 构建配置文件路径
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Configs')
            config_path = os.path.join(config_dir, 'model_analysis.json')
            
            # 读取配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            self.config = None
    
    def load_params(self, config_path: str) -> Dict[str, Any]:
        """
        从配置文件中加载任务参数
        
        参数:
            config_path (str): 配置文件路径
            
        返回:
            Dict[str, Any]: 包含模型名称、超参数等的字典
        """
        return self.load_config(config_path)
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        参数校验方法
        
        参数:
            params (Dict[str, Any]): 待校验的参数字典
            
        返回:
            bool: 校验是否通过
        """
        try:
            # 尝试从配置文件获取支持的参数列表
            if self.config and ('preprocessing_special_params' in self.config or 'ML_model_special_params' in self.config):
                # 元数据键，不视为参数
                metadata_keys = ['type', 'description', 'required', 'default']
                
                # 从配置中提取支持的参数列表
                supported_params = set()
                
                # 检查preprocessing_special_params中的聚类相关参数
                if 'preprocessing_special_params' in self.config:
                    for param_name, param_info in self.config['preprocessing_special_params'].items():
                        if isinstance(param_info, dict) and param_name not in metadata_keys:
                            supported_params.add(param_name)
                
                # 检查ML_model_special_params中的层次聚类相关参数
                if 'ML_model_special_params' in self.config:
                    for model_type, params_dict in self.config['ML_model_special_params'].items():
                        if isinstance(params_dict, dict) and ('hierarchical' in model_type.lower() or 'agglomerative' in model_type.lower() or 'clustering' in model_type.lower()):
                            for param_name, param_info in params_dict.items():
                                if isinstance(param_info, dict) and param_name not in metadata_keys:
                                    supported_params.add(param_name)
                
                # 校验传入的参数是否都在支持的参数列表中
                if supported_params:
                    for param in params:
                        if param not in supported_params:
                            print(f"警告: 参数 {param} 不在配置文件定义的支持参数列表中")
            
            # 降级方案：硬编码的有效参数列表
            valid_params = {
                'n_clusters': int,
                'affinity': str,
                'memory': (str, type(None)),
                'connectivity': (np.ndarray, callable, type(None)),
                'compute_full_tree': (bool, str),
                'linkage': str,
                'distance_threshold': (float, type(None)),
                'compute_distances': bool
            }
            
            # 支持的连接方式
            valid_linkages = ['ward', 'complete', 'average', 'single']
            
            # 支持的亲和度计算方法
            valid_affinities = {
                'ward': ['euclidean'],
                'complete': ['euclidean', 'l1', 'l2', 'manhattan', 'cosine'],
                'average': ['euclidean', 'l1', 'l2', 'manhattan', 'cosine'],
                'single': ['euclidean', 'l1', 'l2', 'manhattan', 'cosine']
            }
            
            # 参数类型和值范围校验
            for param, value in params.items():
                if param in valid_params:
                    # 检查类型
                    if isinstance(valid_params[param], tuple):
                        valid_types = valid_params[param]
                        if not any(isinstance(value, t) for t in valid_types):
                            print(f"参数 {param} 类型错误: 期望 {valid_types}, 得到 {type(value)}")
                            return False
                    elif not isinstance(value, valid_params[param]):
                        print(f"参数 {param} 类型错误: 期望 {valid_params[param]}, 得到 {type(value)}")
                        return False
                    
                    # 检查值范围和有效值
                    if param == 'n_clusters' and value <= 0:
                        print(f"参数 {param} 值错误: 必须大于 0")
                        return False
                    elif param == 'linkage' and value not in valid_linkages:
                        print(f"参数 {param} 值错误: 必须是 {valid_linkages} 之一")
                        return False
                    elif param == 'affinity' and 'linkage' in params:
                        # 检查亲和度和连接方式的兼容性
                        if params['linkage'] in valid_affinities and value not in valid_affinities[params['linkage']]:
                            print(f"参数 {param} 值错误: 连接方式 {params['linkage']} 仅支持 {valid_affinities[params['linkage']]} 亲和度")
                            return False
            
            # 检查n_clusters和distance_threshold不能同时为None
            if 'n_clusters' not in params or params['n_clusters'] is None:
                if 'distance_threshold' not in params or params['distance_threshold'] is None:
                    print("错误: n_clusters 和 distance_threshold 必须至少指定一个")
                    return False
            
            return True
        except Exception:
            # 如果配置加载或参数校验失败，默认返回True以保持兼容性
            return True
    
    def preprocess(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> tuple:
        """
        数据预处理方法
        
        参数:
            X (pd.DataFrame): 特征数据
            y (Optional[pd.Series]): 目标数据（聚类任务中通常为空）
            
        返回:
            tuple: 预处理后的(X, y)数据
        """
        # 基本预处理，确保数据类型正确
        if X.isnull().any().any():
            X = X.fillna(X.mean())
        
        # 层次聚类对特征缩放敏感，添加标准化步骤
        if self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        # 转换回DataFrame以保持特征名称
        X_scaled_df = pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
        
        return X_scaled_df, y
    
    def train(self, X_train: pd.DataFrame, y: Optional[pd.Series] = None) -> Any:
        """
        训练层次聚类模型
        
        参数:
            X_train (pd.DataFrame): 训练特征数据
            y (Optional[pd.Series]): 目标数据（聚类任务中通常为空）
            
        返回:
            Any: 训练完成的模型对象
        """
        try:
            # 创建并训练层次聚类模型
            self.model = AgglomerativeClustering(
                n_clusters=3, 
                affinity='euclidean',
                linkage='ward',
                compute_distances=True
            )
            self.model.fit(X_train)
            
            # 计算linkage matrix用于绘制树状图
            if X_train.shape[0] <= 500:  # 限制样本数量以避免过度计算
                self.linkage_matrix = linkage(X_train, method='ward')
            
            return self.model
        except Exception as e:
            raise Exception(f"层次聚类训练失败: {str(e)}")
    
    def postprocess(self, model: Any, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        训练后处理方法
        
        参数:
            model (Any): 训练完成的模型
            X (pd.DataFrame): 特征数据
            y (Optional[pd.Series]): 目标数据
            
        返回:
            Dict[str, Any]: 包含后处理结果的字典
        """
        try:
            # 获取聚类标签
            labels = model.labels_
            
            result = {
                "labels": labels.tolist()
            }
            
            # 获取聚类数量
            result["n_clusters"] = len(np.unique(labels))
            
            # 计算聚类评估指标
            if X.shape[0] > len(np.unique(labels)) and X.shape[1] > 0:
                try:
                    result["silhouette_score"] = float(silhouette_score(X, labels))
                except:
                    result["silhouette_score"] = None
                
                try:
                    result["davies_bouldin_score"] = float(davies_bouldin_score(X, labels))
                except:
                    result["davies_bouldin_score"] = None
                
                try:
                    result["calinski_harabasz_score"] = float(calinski_harabasz_score(X, labels))
                except:
                    result["calinski_harabasz_score"] = None
            
            # 添加树状图的base64编码图像（如果有linkage matrix）
            if self.linkage_matrix is not None and X.shape[0] <= 100:  # 仅对小样本生成树状图
                try:
                    result["dendrogram"] = self._generate_dendrogram()
                except Exception as e:
                    print(f"生成树状图失败: {e}")
            
            return result
        except Exception as e:
            raise Exception(f"后处理失败: {str(e)}")
    
    def _generate_dendrogram(self) -> str:
        """
        生成树状图并转换为base64编码的字符串
        
        返回:
            str: base64编码的树状图图像
        """
        plt.figure(figsize=(10, 7))
        dendrogram(self.linkage_matrix)
        plt.title('层次聚类树状图')
        plt.xlabel('样本索引')
        plt.ylabel('距离')
        
        # 将图像保存到内存
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # 转换为base64编码
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        获取特征重要性（层次聚类任务中基于聚类中心来判断）
        
        参数:
            model (Any): 模型对象
            
        返回:
            Dict[str, float]: 特征重要性字典
        """
        try:
            # 由于层次聚类不直接提供聚类中心，我们计算每个簇的均值作为中心
            if hasattr(model, 'labels_'):
                # 假设X是最后一次处理的数据
                # 这里返回一个默认的特征重要性字典
                return {}
            return {}
        except Exception:
            return {}
    
    def save_model_artifacts(self, model: Any, filepath: str) -> bool:
        """
        保存模型
        
        参数:
            model (Any): 要保存的模型对象
            filepath (str): 保存路径
            
        返回:
            bool: 是否保存成功
        """
        try:
            # 保存模型和缩放器
            artifacts = {
                'model': model,
                'scaler': self.scaler,
                'linkage_matrix': self.linkage_matrix
            }
            joblib.dump(artifacts, filepath)
            return True
        except Exception as e:
            print(f"保存层次聚类模型失败: {e}")
            return False
    
    def predict(self, model: Any, X: pd.DataFrame) -> pd.Series:
        """
        使用模型进行预测
        
        注意：AgglomerativeClustering不支持直接predict，需要重新训练或使用额外的策略
        
        参数:
            model (Any): 模型对象
            X (pd.DataFrame): 输入数据
            
        返回:
            pd.Series: 预测结果（聚类标签）
        """
        try:
            # 由于AgglomerativeClustering不支持直接预测新数据
            # 我们需要创建一个新的模型实例并训练
            # 首先准备数据
            if self.scaler is not None:
                X_scaled = self.scaler.transform(X)
                X_scaled_df = pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
            else:
                X_scaled_df = X
            
            # 创建新的模型实例，使用与原模型相同的参数
            if hasattr(model, 'n_clusters'):
                new_model = AgglomerativeClustering(
                    n_clusters=model.n_clusters,
                    affinity=getattr(model, 'affinity', 'euclidean'),
                    linkage=getattr(model, 'linkage', 'ward')
                )
                # 注意：这里只是为了获取新数据的聚类，不是真正的预测
                # 实际上，层次聚类是不可预测的，这只是一个近似方法
                predictions = new_model.fit_predict(X_scaled_df)
                return pd.Series(predictions, name='cluster')
            else:
                raise ValueError("模型不包含必要的参数进行预测")
        except Exception as e:
            raise Exception(f"预测失败: {str(e)}")
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """
        获取默认评估指标列表
        
        参数:
            model_type (str): 模型类型
            
        返回:
            List[str]: 默认评估指标列表
        """
        return ['silhouette_score', 'davies_bouldin_score', 'calinski_harabasz_score']
    
    def analyzer(
        self, 
        df: pd.DataFrame, 
        learn_type: str, 
        model_type: str, 
        model: str,
        random_state: int = 42, 
        is_split: bool = False,  # 聚类任务默认不划分训练/测试集
        split_ratio: float = 0.2,
        feature_cols: Optional[List[str]] = None, 
        target_col: Optional[str] = None,  # 聚类任务通常没有目标列
        metrics_list: Optional[List[str]] = None, 
        is_return_model_score: bool = True,
        feature_cols_encoding: str = "auto", 
        target_col_encoding: str = "auto",
        test_set: Optional[pd.DataFrame] = None, 
        model_params: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
        """
        执行完整层次聚类流程的核心方法
        
        参数:
            df (pd.DataFrame): 输入数据集，不能为空
            learn_type (str): 学习类型，如 "ML"（机器学习）
            model_type (str): 模型类别，如 "clustering"
            model (str): 模型名称，如 "hierarchical"
            random_state (int): 随机种子，用于复现实验结果，默认为42
            is_split (bool): 是否自动划分训练/测试集，聚类任务通常为False
            split_ratio (float): 测试集占比，范围 (0,1)，仅当 is_split=True 时生效，默认为0.2
            feature_cols (List[str]): 特征列名列表，不能为空
            target_col (str): 目标列名，聚类任务通常为None
            metrics_list (List[str]): 评价指标列表，如 ["silhouette_score"]，默认使用默认指标
            is_return_model_score (bool): 是否返回模型评估得分，默认为True
            feature_cols_encoding (str): 特征列编码方式，支持 "onehot"、"label"、"ordinal"、"none"、"auto" 等，默认为"auto"
            target_col_encoding (str): 目标列编码方式，聚类任务通常为 "none"
            test_set (pd.DataFrame): 外部传入的测试集，仅当 is_split=False 时使用，默认为None
            model_params (Dict[str, Any]): 模型特定超参数，默认为{}
            
        返回:
            Dict[str, Any]: 包含模型、评估结果等信息的字典
        """
        try:
            # 准备数据
            if feature_cols:
                X = df[feature_cols].copy()
            else:
                # 聚类任务通常使用所有列
                X = df.copy()
                if target_col and target_col in X.columns:
                    X = X.drop(columns=[target_col])
            
            # 确保X是DataFrame类型
            if not isinstance(X, pd.DataFrame):
                X = pd.DataFrame(X)
            
            # 检查特征数量
            if X.shape[1] == 0:
                raise ValueError("数据集至少需要包含一个特征列")
            
            # 处理模型参数
            if model_params is None:
                model_params = {}
            
            # 校验参数
            self.validate_params(model_params)
            
            # 合并默认参数和用户参数
            params = {}
            params.update(model_params)
            
            # 设置默认参数
            if 'n_clusters' not in params and 'distance_threshold' not in params:
                params['n_clusters'] = 3
            if 'linkage' not in params:
                params['linkage'] = 'ward'
            if 'affinity' not in params and params.get('linkage') == 'ward':
                params['affinity'] = 'euclidean'
            if 'compute_distances' not in params:
                params['compute_distances'] = True
            
            # 聚类任务通常不需要划分训练/测试集
            # 但如果设置了is_split=True，仍然支持划分
            if is_split and test_set is None:
                from sklearn.model_selection import train_test_split
                X_train, X_test = train_test_split(
                    X, test_size=split_ratio, random_state=random_state
                )
            else:
                X_train = X
                X_test = test_set
            
            # 数据预处理（包括标准化）
            # 初始化缩放器
            self.scaler = StandardScaler()
            X_train_scaled = pd.DataFrame(
                self.scaler.fit_transform(X_train), 
                index=X_train.index, 
                columns=X_train.columns
            )
            
            # 训练模型
            self.model = AgglomerativeClustering(**params)
            self.model.fit(X_train_scaled)
            
            # 获取聚类结果
            train_labels = self.model.labels_
            
            # 计算linkage matrix用于绘制树状图（如果样本数量合理）
            if X_train_scaled.shape[0] <= 500:
                try:
                    # 根据指定的linkage方法选择scipy对应的方法
                    method_map = {
                        'ward': 'ward',
                        'complete': 'complete',
                        'average': 'average',
                        'single': 'single'
                    }
                    scipy_method = method_map.get(params.get('linkage'), 'ward')
                    self.linkage_matrix = linkage(X_train_scaled, method=scipy_method)
                except Exception as e:
                    print(f"计算linkage matrix失败: {e}")
                    self.linkage_matrix = None
            
            # 计算聚类评估指标
            metrics = {}
            if X_train_scaled.shape[0] > len(np.unique(train_labels)):
                try:
                    metrics["silhouette_score"] = float(silhouette_score(X_train_scaled, train_labels))
                except Exception as e:
                    print(f"计算轮廓系数失败: {e}")
                    metrics["silhouette_score"] = None
                
                try:
                    metrics["davies_bouldin_score"] = float(davies_bouldin_score(X_train_scaled, train_labels))
                except Exception as e:
                    print(f"计算Davies-Bouldin指数失败: {e}")
                    metrics["davies_bouldin_score"] = None
                
                try:
                    metrics["calinski_harabasz_score"] = float(calinski_harabasz_score(X_train_scaled, train_labels))
                except Exception as e:
                    print(f"计算Calinski-Harabasz指数失败: {e}")
                    metrics["calinski_harabasz_score"] = None
            
            # 构建结果字典
            result = {
                "model": self.model,
                "scaler": self.scaler,
                "metrics": metrics,
                "message": "层次聚类完成"
            }
            
            # 如果需要返回模型得分
            if is_return_model_score:
                result["labels"] = train_labels.tolist()
                result["n_clusters"] = len(np.unique(train_labels))
                
                # 如果有测试集，进行预测（注意：这只是近似方法）
                if X_test is not None:
                    X_test_scaled = pd.DataFrame(
                        self.scaler.transform(X_test),
                        index=X_test.index,
                        columns=X_test.columns
                    )
                    # 为测试集创建新的聚类模型
                    test_model = AgglomerativeClustering(**params)
                    test_labels = test_model.fit_predict(X_test_scaled)
                    result["test_labels"] = test_labels.tolist()
            
            # 添加树状图（如果样本数量合理）
            if self.linkage_matrix is not None and X_train_scaled.shape[0] <= 100:
                try:
                    result["dendrogram"] = self._generate_dendrogram()
                except Exception as e:
                    print(f"生成树状图失败: {e}")
            
            return result
        except Exception as e:
            return {
                "error": str(e)
            }