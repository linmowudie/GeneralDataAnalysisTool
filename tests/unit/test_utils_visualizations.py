"""
测试utils目录下的可视化工具函数
"""

import unittest
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# 获取项目根目录 - 修复路径计算
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 验证PROJECT_ROOT路径
print(f"计算得到的PROJECT_ROOT: {PROJECT_ROOT}")

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 添加utils目录到sys.path
UTILS_PATH = os.path.join(PROJECT_ROOT, 'Src', 'DataAnalyzer', 'DataVisualisationUpgrade', 'utils')
if UTILS_PATH not in sys.path:
    sys.path.insert(0, UTILS_PATH)


class TestUtilsVisualizations(unittest.TestCase):
    """测试utils目录下的各种可视化工具函数"""

    def setUp(self):
        """测试前的准备工作"""
        np.random.seed(42)
        
    def tearDown(self):
        """测试后清理"""
        plt.close('all')
        
    def test_plot_confusion_matrix(self):
        """测试混淆矩阵绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_confusion_matrix import plot_confusion_matrix
        y_true = [0, 1, 0, 1, 0, 1]
        y_pred = [0, 1, 1, 1, 0, 0]
        
        fig, ax = plot_confusion_matrix(y_true, y_pred, class_names=['Class 0', 'Class 1'])
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), '混淆矩阵')
        
    def test_plot_roc_curve_binary(self):
        """测试二分类ROC曲线绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_roc_curve import plot_roc_curve
        y_true = [0, 1, 0, 1, 0, 1]
        y_pred_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.9, 0.1], [0.3, 0.7], [0.8, 0.2], [0.4, 0.6]])
        
        fig, ax = plot_roc_curve(y_true, y_pred_proba)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertIn('ROC曲线', ax.get_title())
        
    def test_plot_precision_recall_curve_binary(self):
        """测试二分类精确率-召回率曲线绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_precision_recall_curve import plot_precision_recall_curve
        y_true = [0, 1, 0, 1, 0, 1]
        y_pred_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.9, 0.1], [0.3, 0.7], [0.8, 0.2], [0.4, 0.6]])
        
        fig, ax = plot_precision_recall_curve(y_true, y_pred_proba)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertIn('精确率-召回率曲线', ax.get_title())
        
    def test_plot_feature_importance(self):
        """测试特征重要性图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_feature_importance import plot_feature_importance
        importances = np.array([0.1, 0.3, 0.2, 0.4])
        feature_names = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']
        
        fig, ax = plot_feature_importance(importances, feature_names)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), '特征重要性')
        
    def test_plot_coefficients(self):
        """测试系数图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_coefficients import plot_coefficients
        coefficients = np.array([0.5, -0.3, 0.8, -0.1])
        feature_names = ['Coef 1', 'Coef 2', 'Coef 3', 'Coef 4']
        
        fig, ax = plot_coefficients(coefficients, feature_names)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), '模型系数')
        
    def test_plot_actual_vs_predicted(self):
        """测试真实值vs预测值散点图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_actual_vs_predicted import plot_actual_vs_predicted
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 2.2, 2.8, 4.1, 4.9])
        
        fig, ax = plot_actual_vs_predicted(y_true, y_pred)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), '真实值 vs 预测值')
        
    def test_plot_residuals(self):
        """测试残差图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_residuals import plot_residuals
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 2.2, 2.8, 4.1, 4.9])
        
        fig, ax = plot_residuals(y_true, y_pred)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), '残差图')
        
    def test_plot_silhouette(self):
        """测试轮廓系数图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_silhouette import plot_silhouette
        # 创建测试数据
        cluster1 = np.random.randn(10, 2) + [2, 2]
        cluster2 = np.random.randn(10, 2) + [-2, -2]
        X = np.vstack([cluster1, cluster2])
        labels = np.array([0]*10 + [1]*10)
        
        fig, ax = plot_silhouette(X, labels)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), '轮廓系数图')
        
    def test_plot_dendrogram(self):
        """测试树状图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_dendrogram import plot_dendrogram
        # 创建简单的linkage矩阵
        linkage_matrix = np.array([
            [0, 1, 0.5, 2],
            [2, 3, 0.7, 2],
            [4, 5, 0.9, 4]
        ])
        
        fig, ax = plot_dendrogram(linkage_matrix)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), '层次聚类树状图')
        
    def test_plot_before_after_distribution(self):
        """测试变换前后分布对比图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_before_after_distribution import plot_before_after_distribution
        X_before = np.random.randn(100, 2)
        X_after = np.random.randn(100, 2) * 0.5
        
        fig, axes = plot_before_after_distribution(X_before, X_after, 
                                                  feature_names=['Feature 1', 'Feature 2'])
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(axes)
        
    def test_plot_embedding_scatter_2d(self):
        """测试2D嵌入空间散点图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_embedding_scatter import plot_embedding_scatter
        embedding = np.random.randn(50, 2)
        labels = np.random.randint(0, 3, 50)
        
        fig, ax = plot_embedding_scatter(embedding, labels)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertIn('嵌入空间散点图', ax.get_title())
        
    def test_plot_embedding_scatter_3d(self):
        """测试3D嵌入空间散点图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_embedding_scatter import plot_embedding_scatter
        embedding = np.random.randn(50, 3)
        labels = np.random.randint(0, 3, 50)
        
        fig, ax = plot_embedding_scatter(embedding, labels)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertIn('3D嵌入空间散点图', ax.get_title())
        
    def test_plot_missing_value_matrix(self):
        """测试缺失值矩阵绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_missing_value_matrix import plot_missing_value_matrix
        data = np.random.randn(20, 5)
        # 添加一些缺失值
        data[0, 0] = np.nan
        data[5, 2] = np.nan
        
        fig, ax = plot_missing_value_matrix(data)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), '缺失值矩阵（白色表示缺失值）')
        
    def test_plot_word_cloud(self):
        """测试词云图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_word_cloud import plot_word_cloud
        frequencies = {
            'Python': 100,
            'Java': 80,
            'C++': 60,
            'JavaScript': 70,
            'Go': 40
        }
        
        fig, ax = plot_word_cloud(frequencies)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertIn('词频统计', ax.get_title())
        
    def test_plot_gauge_chart(self):
        """测试仪表盘图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_gauge_chart import plot_gauge_chart
        fig, ax = plot_gauge_chart(75, 100, "测试仪表盘")
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), "测试仪表盘")
        
    def test_plot_waterfall(self):
        """测试瀑布图绘制"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_waterfall import plot_waterfall
        contributions = [10, -5, 15, -3, 7]
        labels = ['A', 'B', 'C', 'D', 'E']
        
        fig, ax = plot_waterfall(contributions, labels, "测试瀑布图")
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertEqual(ax.get_title(), "测试瀑布图")
        
    def test_save_all_plots_to_test_images(self):
        """测试保存所有图形到TestImages目录"""
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_confusion_matrix import plot_confusion_matrix
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_feature_importance import plot_feature_importance
        from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_coefficients import plot_coefficients
        
        test_images_dir = os.path.join(PROJECT_ROOT, 'TestImages')
        print(f"测试图片保存目录: {test_images_dir}")
        if not os.path.exists(test_images_dir):
            os.makedirs(test_images_dir)
            print("已创建测试图片目录")
        print(f"目录存在: {os.path.exists(test_images_dir)}")
            
        # 测试保存部分图形
        # 1. 混淆矩阵
        y_true = [0, 1, 0, 1, 0, 1]
        y_pred = [0, 1, 1, 1, 0, 0]
        fig, _ = plot_confusion_matrix(y_true, y_pred)
        file_path = os.path.join(test_images_dir, 'confusion_matrix_utils_test.png')
        print(f"保存混淆矩阵到: {file_path}")
        fig.savefig(file_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # 2. 特征重要性
        importances = np.array([0.1, 0.3, 0.2, 0.4])
        feature_names = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']
        fig, _ = plot_feature_importance(importances, feature_names)
        file_path = os.path.join(test_images_dir, 'feature_importance_utils_test.png')
        print(f"保存特征重要性图到: {file_path}")
        fig.savefig(file_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # 3. 系数图
        coefficients = np.array([0.5, -0.3, 0.8, -0.1])
        fig, _ = plot_coefficients(coefficients, feature_names)
        file_path = os.path.join(test_images_dir, 'coefficients_utils_test.png')
        print(f"保存系数图到: {file_path}")
        fig.savefig(file_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # 验证文件是否保存成功
        conf_matrix_path = os.path.join(test_images_dir, 'confusion_matrix_utils_test.png')
        feat_import_path = os.path.join(test_images_dir, 'feature_importance_utils_test.png')
        coeff_path = os.path.join(test_images_dir, 'coefficients_utils_test.png')
        
        print(f"混淆矩阵文件存在: {os.path.exists(conf_matrix_path)}")
        print(f"特征重要性文件存在: {os.path.exists(feat_import_path)}")
        print(f"系数图文件存在: {os.path.exists(coeff_path)}")
        
        # 列出目录内容
        print("\n目录内容:")
        for file in os.listdir(test_images_dir):
            print(f"- {file}")
        
        self.assertTrue(os.path.exists(conf_matrix_path))
        self.assertTrue(os.path.exists(feat_import_path))
        self.assertTrue(os.path.exists(coeff_path))


if __name__ == '__main__':
    unittest.main()