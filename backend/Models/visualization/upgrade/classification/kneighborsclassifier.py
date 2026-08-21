"""
K近邻分类模型可视化策略
"""

from typing import Dict, Any
from .base import ClassificationStrategy
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np


class KNeighborsClassifierStrategy(ClassificationStrategy):
    """
    K近邻分类模型可视化策略
    """
    
    def generate_static_charts(self):
        """
        生成静态图表
        """
        charts = {}
        
        # 生成混淆矩阵
        charts.update(self.generate_confusion_matrix())
            
        # 生成决策边界图
        charts.update(self.generate_decision_boundary())
            
        # 生成邻居分布图
        charts.update(self.generate_neighbors_distribution())
            
        return charts
        
    def generate_interactive_charts(self):
        """
        生成交互式图表
        """
        # 默认实现，可以被子类覆盖
        return {}

    def validate_params(self) -> None:
        """
        验证K近邻分类模型参数
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
        ax.set_title('K近邻分类混淆矩阵')
        
        return {"knn_confusion_matrix": fig}

    def generate_neighbors_distribution(self) -> Dict[str, Figure]:
        """
        生成邻居分布图
        """
        import matplotlib.pyplot as plt
        from sklearn.neighbors import NearestNeighbors
        
        X_train = self.params["X_train"]
        X_test = self.params["X_test"]
        y_train = self.params["y_train"]
        y_test = self.params["y_test"]
        
        # 创建邻居查找器
        nbrs = NearestNeighbors(n_neighbors=5).fit(X_train)
        distances, indices = nbrs.kneighbors(X_test[:10])  # 只显示前10个测试样本的邻居
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制训练样本
        scatter = ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap='viridis', alpha=0.6, label='训练样本')
        
        # 绘制测试样本及其邻居
        for i in range(len(X_test[:10])):
            # 绘制测试样本
            ax.scatter(X_test[i, 0], X_test[i, 1], c=[y_test[i]], cmap='viridis', marker='s', s=100, edgecolors='black')
            
            # 绘制邻居
            for j in indices[i]:
                ax.scatter(X_train[j, 0], X_train[j, 1], c=[y_train[j]], cmap='viridis', marker='^', s=80, edgecolors='red')
        
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('K近邻分类器邻居分布图')
        plt.colorbar(scatter)
        
        return {"knn_neighbors_distribution": fig}

    def generate_decision_boundary(self) -> Dict[str, Figure]:
        """
        生成决策边界图（仅适用于二维特征）
        """
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        
        model = self.params["model"]
        X_test = self.params["X_test"]
        y_test = self.params["y_test"]
        
        # 检查特征维度
        if X_test.shape[1] != 2:
            raise ValueError("决策边界图仅适用于二维特征数据")
        
        self.apply_styles()
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 创建网格
        h = 0.02
        x_min, x_max = X_test[:, 0].min() - 1, X_test[:, 0].max() + 1
        y_min, y_max = X_test[:, 1].min() - 1, X_test[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                             np.arange(y_min, y_max, h))
        
        # 预测网格点
        Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        
        # 绘制决策边界
        cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
        ax.contourf(xx, yy, Z, cmap=cmap_light, alpha=0.5)
        
        # 绘制测试样本
        scatter = ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap='viridis', edgecolors='black')
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.set_title('K近邻分类器决策边界')
        plt.colorbar(scatter)
        
        return {"knn_decision_boundary": fig}