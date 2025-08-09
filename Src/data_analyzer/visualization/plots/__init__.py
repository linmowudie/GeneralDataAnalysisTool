"""
Src/data_analyzer/visualization/plots/__init__.py
可视化绘图插件初始化模块

该模块负责自动导入和注册所有可视化绘图插件，
通过pkgutil.iter_modules自动发现并导入plots目录下的所有模块。
"""

# visualization/plots/__init__.py
from ...data_visualization import DataVisualization

# 自动导入所有绘图插件
import importlib
import pkgutil

# 自动注册plots目录下的所有模块
for _, module_name, _ in pkgutil.iter_modules(path=__path__, prefix='plots.'):
    importlib.import_module('.' + module_name, package=__name__)