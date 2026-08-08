"""
GeneralDataAnalysisTool 包初始化文件

该文件为外部工具提供访问核心功能的接口。
五层架构：Interfaces / Services / Cores / Models / Infrastructures
"""

try:
    from backend.Services import ManualWorkflow, AgentWorkflow, WorkflowBuilder

    __all__ = [
        'ManualWorkflow',
        'AgentWorkflow',
        'WorkflowBuilder',
    ]

except ImportError:
    # 如果导入失败，则不暴露相关接口
    __all__ = []
