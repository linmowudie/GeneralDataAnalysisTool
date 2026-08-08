"""
backend/Interfaces/web/schemas/common.py
通用请求/响应模型
"""

from typing import Any, Dict, List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    message: str


class SessionResponse(BaseModel):
    """会话创建响应"""
    session_id: str
    message: str


class StepStatusResponse(BaseModel):
    """步骤状态响应"""
    session_id: str
    status: Dict[str, Any]


class ReportConfigRequest(BaseModel):
    """报告配置请求（允许任意扩展字段）"""
    model_config = {"extra": "allow"}

    report_type: str = "full"
    title: str = ""
    sections: List[str] = []
