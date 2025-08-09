# data_visualization/__init__.py
from ...data_visualization import DataVisualization

# 自动导入所有绘图插件
import importlib
import pkgutil

# 自动注册plots目录下的所有模块
for _, module_name, _ in pkgutil.iter_modules(path=__path__, prefix='plots.'):
    importlib.import_module('.' + module_name, package=__name__)