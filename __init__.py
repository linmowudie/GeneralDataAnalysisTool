"""
GeneralDataAnalysisTool 包初始化文件

该文件为外部工具提供访问核心功能的接口。
"""

try:
    # 尝试从Src.data_analyzer导入核心模块
    from Src.data_analyzer.core import DataProcessingEngine
    
    __all__ = [
        'DataProcessingEngine'
    ]
    
except ImportError:
    # 如果导入失败，则不暴露相关接口
    __all__ = []