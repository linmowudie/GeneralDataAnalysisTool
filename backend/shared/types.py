"""
backend/shared/types.py
跨层数据契约与领域异常

任何层之间传递的数据结构必须在此定义；
Cores/Models/Infrastructures 不得 import fastapi。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# 枚举
# ---------------------------------------------------------------------------

class StepName(str, Enum):
    """流程步骤（顺序固定）"""
    IMPORT = "import"
    PREVIEW = "preview"
    CLEANING = "cleaning"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    REPORT = "report"


class TaskType(str, Enum):
    """分析任务类型"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    ASSOCIATION = "association"
    UNKNOWN = "unknown"


class CleanMode(str, Enum):
    """清洗模式"""
    AUTO = "auto"
    MANUAL = "manual"
    FREEDOM = "freedom"


class ReportType(str, Enum):
    """报告模板类型"""
    FULL = "full"
    SUMMARY = "summary"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"


class WorkflowMode(str, Enum):
    """工作流模式"""
    MANUAL = "manual"
    AGENT = "agent"


class DecisionStatus(str, Enum):
    """Agent 评估结论"""
    PASS = "pass"
    FAIL = "fail"
    RETRY_NEXT = "retry_next"


# 步骤固定顺序
STEP_ORDER: List[StepName] = [
    StepName.IMPORT,
    StepName.PREVIEW,
    StepName.CLEANING,
    StepName.ANALYSIS,
    StepName.VISUALIZATION,
    StepName.REPORT,
]


# ---------------------------------------------------------------------------
# Artifact 体系（部件产物基类）
# 规则：
# - Artifact 中不得直接携带大 DataFrame；DataFrame 一律落 temp_storage，
#   Artifact 只持 storage_key 与元信息
# - trained_model_ref 为模型存储键，不携带模型实例（序列化安全）
# ---------------------------------------------------------------------------

@dataclass
class Artifact:
    """部件产物基类"""
    step: StepName
    created_at: datetime = field(default_factory=datetime.now)
    storage_key: Optional[str] = None  # temp_storage 中的键，支持断点续跑


@dataclass
class ImportedArtifact(Artifact):
    shape: tuple = (0, 0)
    columns: List[str] = field(default_factory=list)
    dtypes: Dict[str, str] = field(default_factory=dict)
    source: str = ""


@dataclass
class PreviewArtifact(Artifact):
    head_records: List[Dict[str, Any]] = field(default_factory=list)
    dataset_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CleanedArtifact(Artifact):
    shape: tuple = (0, 0)
    columns: List[str] = field(default_factory=list)
    target_col: Optional[str] = None
    clean_summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisArtifact(Artifact):
    task_type: TaskType = TaskType.UNKNOWN
    model_type: str = ""
    model_params: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    predictions: Optional[List[Any]] = None
    trained_model_ref: Optional[str] = None  # 模型存储键（ModelStore），不携带模型实例


@dataclass
class VisualizationArtifact(Artifact):
    charts: Dict[str, Any] = field(default_factory=dict)  # name -> plotly json / figure 描述


@dataclass
class ReportArtifact(Artifact):
    report_id: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Agent 契约
# ---------------------------------------------------------------------------

@dataclass
class ColumnProfile:
    """单列画像"""
    name: str
    dtype: str
    missing_rate: float = 0.0
    unique_count: int = 0
    cardinality: int = 0
    is_numeric: bool = False


@dataclass
class DataProfile:
    """数据画像"""
    n_rows: int
    n_cols: int
    columns: List[ColumnProfile] = field(default_factory=list)
    target_col: Optional[str] = None
    inferred_task_type: TaskType = TaskType.UNKNOWN
    memory_mb: float = 0.0


@dataclass
class PlanCandidate:
    """Planner 推荐的候选分析方案"""
    model_type: str                              # Models 注册表中的 key
    task_type: TaskType
    suggested_params: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1                            # 越小越优先
    reason: str = ""                             # 推荐理由（规则文案或 LLM 输出）


@dataclass
class EvaluationReport:
    """Evaluator 评估报告"""
    status: DecisionStatus
    score: Optional[float] = None                # 归一化 0-1 综合评分
    metrics_evaluated: Dict[str, float] = field(default_factory=dict)
    suggestion: str = ""                         # 文字建议
    next_action: str = "keep"                    # keep / retry_next / abort


@dataclass
class AttemptRecord:
    """Agent 单次尝试记录"""
    model_type: str
    task_type: TaskType
    metrics: Dict[str, float] = field(default_factory=dict)
    evaluation: Optional[EvaluationReport] = None
    error: Optional[str] = None


@dataclass
class AgentDecision:
    """Agent 闭环最终决策"""
    session_id: str
    profile: Optional[DataProfile] = None
    attempts: List[AttemptRecord] = field(default_factory=list)
    best: Optional[AttemptRecord] = None
    finished_at: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# 领域异常（Interfaces 层统一映射为 HTTP 状态码）
# ---------------------------------------------------------------------------

class DomainError(Exception):
    """领域异常基类"""
    http_status: int = 500


class SessionNotFound(DomainError):
    http_status = 404


class SessionTimeout(DomainError):
    http_status = 410


class StepLocked(DomainError):
    http_status = 423


class WorkflowOrderError(DomainError):
    """步骤顺序非法"""
    http_status = 400


class InvalidModelParams(DomainError):
    http_status = 400


class ComponentExecutionError(DomainError):
    http_status = 500


class ImportError_(DomainError):
    """数据读取失败（避免与内建 ImportError 冲突）"""
    http_status = 400
