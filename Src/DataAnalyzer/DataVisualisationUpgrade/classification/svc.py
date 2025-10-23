"""
支持向量机分类模型可视化策略
"""

from typing import Dict, Any
from .base import ClassificationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class SVCStrategy(ClassificationStrategy):
    """
    支持向量机分类模型可视化策略
    """
    
    def generate_static_charts(self):
        """
        生成静态图表
        """
        charts = {}
        
        # 生成混淆矩阵
        charts.update(self.generate_confusion_matrix())
        
        # 生成ROC曲线
        charts.update(self.generate_roc_curve())
        
        # 生成支持向量分布图
        charts.update(self.generate_support_vectors())
        
        # 生成决策边界图
        charts.update(self.generate_decision_boundary())
            
        return charts
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def validate_params(self) -> None:
        """
        验证支持向量机分类模型参数
        """
        super().validate_params()

    def generate_confusion_matrix(self) -> Dict[str, Figure]:
        """
        生成混淆矩阵图
        """
        from ..utils.plot_confusion_matrix import plot_confusion_matrix
        
        y_test = self.params["y_test"]
        y_pred, _ = self._get_model_predictions()
        
        self.apply_styles()
        fig, ax = plot_confusion_matrix(y_test, y_pred, figsize=(8, 6))
        ax.set_title('支持向量机混淆矩阵')
        
        return {"svc_confusion_matrix": fig}

    def generate_roc_curve(self) -> Dict[str, Figure]:
        """
        生成ROC曲线图
        """
        from ..utils.plot_roc_curve import plot_roc_curve
        
        y_test = self.params["y_test"]
        _, y_pred_proba = self._get_model_predictions()
        
        if y_pred_proba is None:
            raise ValueError("模型不支持概率预测，无法绘制ROC曲线")
        
        self.apply_styles()
        fig, ax = plot_roc_curve(y_test, y_pred_proba, figsize=(8, 6))
        ax.set_title('支持向量机ROC曲线')
        
        return {"svc_roc_curve": fig}

    def generate_support_vectors(self) -> Dict[str, Figure]:
        """
        生成支持向量分布图（仅适用于二维特征）
        """
        import matplotlib.pyplot as plt
        
        model = self.params["model"]
        X_train = self.params["X_train"]
        y_train = self.params["y_train"]
        
        # 检查特征维度
        if X_train.shape[1] != 2:
            raise ValueError("支持向量分布图仅适用于二维特征数据")
        
        if not hasattr(model, "support_vectors_"):
            raise ValueError("模型没有support_vectors_属性")
        
        support_vectors = model.support_vectors_
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 绘制训练样本
        scatter = ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap='viridis', alpha=0.6)
        
        # 绘制支持向量
        ax.scatter(support_vectors[:, 0], support_vectors[:, 1], 
                  s=100, facecolors='none', edgecolors='red', linewidth=2, label='支持向量')
        
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('支持向量机支持向量分布')
        ax.legend()
        plt.colorbar(scatter)
        
        return {"svc_support_vectors": fig}

    def generate_decision_boundary(self) -> Dict[str, Figure]:
        """
        生成决策边界图（仅适用于二维特征）
        """
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        
        model = self.params["model"]
        X_train = self.params["X_train"]
        y_train = self.params["y_train"]
        
        # 检查特征维度
        if X_train.shape[1] != 2:
            raise ValueError("决策边界图仅适用于二维特征数据")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 创建网格
        h = 0.02
        x_min, x_max = X_train[:, 0].min() - 1, X_train[:, 0].max() + 1
        y_min, y_max = X_train[:, 1].min() - 1, X_train[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                             np.arange(y_min, y_max, h))
        
        # 预测网格点
        Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        
        # 绘制决策边界
        cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
        ax.contourf(xx, yy, Z, cmap=cmap_light, alpha=0.5)
        
        # 绘制训练样本
        scatter = ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap='viridis', edgecolors='black')
        
        # 如果模型有支持向量，也绘制出来
        if hasattr(model, "support_vectors_"):
            support_vectors = model.support_vectors_
            ax.scatter(support_vectors[:, 0], support_vectors[:, 1], 
                      s=100, facecolors='none', edgecolors='red', linewidth=2, label='支持向量')
        
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('支持向量机决策边界')
        ax.legend()
        plt.colorbar(scatter)
        
        return {"svc_decision_boundary": fig}