"""
Src/DataAnalyzer/VisualizationModule/InteractivePlots/__init__.py
交互式可视化绘图插件初始化模块

该模块负责自动导入和注册所有交互式可视化绘图插件，
通过pkgutil.iter_modules自动发现并导入InteractivePlots目录下的所有模块。
"""

# 自动导入所有交互式绘图插件
import importlib
import pkgutil

# 自动注册InteractivePlots目录下的所有模块
for _, module_name, _ in pkgutil.iter_modules(path=__path__):
    importlib.import_module('.' + module_name, package='backend.Models.visualization.InteractivePlots')