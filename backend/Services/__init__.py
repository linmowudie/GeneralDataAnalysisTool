"""backend.Services：服务层（工作流组装 + 功能部件）"""
from .workflows.context import WorkflowContext, StepStateMachine
from .workflows.builder import WorkflowBuilder
from .workflows.manual_workflow import ManualWorkflow
from .workflows.agent_workflow import AgentWorkflow
from .components import (
    ImportComponent, PreviewComponent, CleaningComponent,
    AnalysisComponent, VisualizationComponent, ReportingComponent,
)
from .components.base_component import BaseComponent

__all__ = [
    "WorkflowContext", "StepStateMachine",
    "WorkflowBuilder", "ManualWorkflow", "AgentWorkflow",
    "BaseComponent",
    "ImportComponent", "PreviewComponent", "CleaningComponent",
    "AnalysisComponent", "VisualizationComponent", "ReportingComponent",
]
