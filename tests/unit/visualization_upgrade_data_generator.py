import numpy as np
import pandas as pd
from sklearn.datasets import make_classification, make_regression, make_blobs
from sklearn.model_selection import train_test_split


class DataGenerator:
    """数据生成器

    该类用于生成数据，用于测试可视化功能。
    """

    def __init__(self) -> None:
        pass

    def load_data(self, file_path):
        """加载数据

        Args:
            file_path (str): 数据文件路径

        Returns:
            pd.DataFrame: 数据
        """
        return pd.read_csv(file_path)

    def generate_data(self, num_samples=1000):
        """生成数据

        Args:
            num_samples (int, optional): 生成数据的样本数. Defaults to 1000.

        Returns:
            pd.DataFrame: 生成的数据
        """
        data = pd.DataFrame({
            'x': np.random.rand(num_samples),
            'y': np.random.rand(num_samples),
        })
        return data

    def generate_classification_data(self, n_samples=1000, n_features=20, n_classes=2, n_informative=10):
        """生成分类数据

        Args:
            n_samples (int): 样本数量
            n_features (int): 特征数量
            n_classes (int): 类别数量
            n_informative (int): 有用特征数量

        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        X, y = make_classification(n_samples=n_samples, n_features=n_features, n_classes=n_classes,
                                   n_informative=n_informative, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        return X_train, X_test, y_train, y_test

    def generate_regression_data(self, n_samples=1000, n_features=5):
        """生成回归数据

        Args:
            n_samples (int): 样本数量
            n_features (int): 特征数量

        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        X, y = make_regression(n_samples=n_samples, n_features=n_features, noise=0.1, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        return X_train, X_test, y_train, y_test

    def generate_clustering_data(self, n_samples=1000, n_features=2, centers=3):
        """生成聚类数据

        Args:
            n_samples (int): 样本数量
            n_features (int): 特征数量
            centers (int): 中心数量

        Returns:
            array: X数据
        """
        X, _ = make_blobs(n_samples=n_samples, n_features=n_features, centers=centers, random_state=42)
        return X