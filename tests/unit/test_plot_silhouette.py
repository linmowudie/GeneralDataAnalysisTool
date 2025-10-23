"""
测试plot_silhouette功能
"""

import unittest
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Src.DataAnalyzer.DataVisualisationUpgrade.utils.plot_silhouette import plot_silhouette


class TestPlotSilhouette(unittest.TestCase):
    """测试轮廓系数图功能"""

    def setUp(self):
        """测试前准备"""
        # 创建测试数据
        np.random.seed(42)
        # 创建3个明显的聚类
        cluster1 = np.random.randn(20, 2) + [2, 2]
        cluster2 = np.random.randn(20, 2) + [-2, -2]
        cluster3 = np.random.randn(20, 2) + [2, -2]
        
        self.X = np.vstack([cluster1, cluster2, cluster3])
        self.labels = np.array([0]*20 + [1]*20 + [2]*20)
        
    def tearDown(self):
        """测试后清理"""
        plt.close('all')
        
    def test_plot_silhouette_basic(self):
        """测试基本的轮廓系数图绘制功能"""
        fig, ax = plot_silhouette(self.X, self.labels)
        
        # 检查返回值
        self.assertIsInstance(fig, Figure)
        self.assertIsNotNone(ax)
        
        # 检查图形标题
        self.assertEqual(ax.get_title(), '轮廓系数图')
        
        # 检查坐标轴标签
        self.assertEqual(ax.get_xlabel(), '轮廓系数值')
        self.assertEqual(ax.get_ylabel(), '簇标签')
        
    def test_plot_silhouette_with_custom_figsize(self):
        """测试自定义图形大小"""
        fig, ax = plot_silhouette(self.X, self.labels, figsize=(12, 8))
        
        # 检查图形大小
        self.assertEqual(fig.get_size_inches()[0], 12)
        self.assertEqual(fig.get_size_inches()[1], 8)
        
    def test_plot_silhouette_legend(self):
        """测试图例存在"""
        fig, ax = plot_silhouette(self.X, self.labels)
        
        # 检查图例是否存在
        legend = ax.get_legend()
        self.assertIsNotNone(legend)
        
        # 检查图例文本是否包含平均轮廓系数
        if legend is not None:
            legend_texts = [text.get_text() for text in legend.get_texts()]
            has_avg_silhouette = any('平均轮廓系数' in text for text in legend_texts)
            self.assertTrue(has_avg_silhouette)
        
    def test_plot_silhouette_clusters_count(self):
        """测试簇的数量正确显示"""
        fig, ax = plot_silhouette(self.X, self.labels)
        
        # 检查y轴刻度标签数量是否与簇数量相关
        ytick_labels = ax.get_yticklabels()
        self.assertGreater(len(ytick_labels), 0)
        
    def test_plot_silhouette_children(self):
        """测试图形包含子元素"""
        fig, ax = plot_silhouette(self.X, self.labels)
        
        # 检查axes包含子元素(线条等)
        children = ax.get_children()
        self.assertGreater(len(children), 0)
        
    def test_save_plot_to_test_images(self):
        """测试保存图形到TestImages目录"""
        test_images_dir = os.path.join(PROJECT_ROOT, 'TestImages')
        if not os.path.exists(test_images_dir):
            os.makedirs(test_images_dir)
            
        fig, ax = plot_silhouette(self.X, self.labels)
        
        # 保存图像
        image_path = os.path.join(test_images_dir, 'silhouette_plot.png')
        fig.savefig(image_path, dpi=150, bbox_inches='tight')
        
        # 检查文件是否保存成功
        self.assertTrue(os.path.exists(image_path))
        
        # 清理测试文件
        if os.path.exists(image_path):
            os.remove(image_path)


if __name__ == '__main__':
    unittest.main()