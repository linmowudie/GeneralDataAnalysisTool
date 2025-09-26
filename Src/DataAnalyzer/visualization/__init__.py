"""
Src/DataAnalyzer/visualization/__init__.py
数据可视化模块初始化文件

该文件负责初始化可视化模块并导入所有子模块。
"""

# 确保导入所有可视化插件
from . import plots

__all__ = ['plots']