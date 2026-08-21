"""
backend/Interfaces/web/routers/agent.py
/api/agent/*：Agent 闭环五端点
（data-profile / recommend-methods / evaluate / auto-analyze / decision）
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.Interfaces.controllers import session_controller, AgentController
from backend.shared.types import DomainError
from backend.Interfaces.web.errors import to_http_error
from backend.Interfaces.web.utils import to_jsonable

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Agent 自动分析"])

agent_controller = AgentController(session_controller)


@router.get("/data-profile")
async def data_profile(
    session_id: str = Query(..., description="会话ID"),
    target_col: Optional[str] = Query(None, description="目标列（可选）")
):
    """数据画像：分析数据结构、类型分布与任务类型"""
    try:
        profile = agent_controller.data_profile(session_id, target_col=target_col)
        return {"status": "success", "session_id": session_id, "profile": to_jsonable(profile)}
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据画像失败: {str(e)}")


@router.post("/recommend-methods")
async def recommend_methods(
    session_id: str = Query(..., description="会话ID"),
    target_col: Optional[str] = Query(None, description="目标列（可选）")
):
    """根据画像推荐分析方法（按优先级排序）"""
    try:
        candidates = agent_controller.recommend_methods(session_id, target_col=target_col)
        return {
            "status": "success",
            "session_id": session_id,
            "candidates": to_jsonable(candidates),
            "count": len(candidates),
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"方法推荐失败: {str(e)}")


@router.post("/evaluate")
async def evaluate_analysis(
    session_id: str = Query(..., description="会话ID")
):
    """评估当前分析结果（指标 + 结论）"""
    try:
        report = agent_controller.evaluate(session_id)
        return {"status": "success", "session_id": session_id, "evaluation": to_jsonable(report)}
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析评估失败: {str(e)}")


@router.post("/auto-analyze")
async def auto_analyze(
    session_id: str = Query(..., description="会话ID"),
    max_candidates: int = Query(3, description="最大候选方法数"),
    target_col: Optional[str] = Query(None, description="目标列（可选）"),
    timeout_sec: int = Query(300, description="超时时间（秒）")
):
    """自动分析闭环：画像 -> 推荐 -> 逐候选执行 -> 评估 -> 择优"""
    try:
        decision = agent_controller.auto_analyze(
            session_id,
            max_candidates=max_candidates,
            target_col=target_col,
            timeout_sec=timeout_sec,
        )
        return {"status": "success", "session_id": session_id, "decision": to_jsonable(decision)}
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自动分析失败: {str(e)}")


@router.get("/decision")
async def get_decision(
    session_id: str = Query(..., description="会话ID")
):
    """查询最近一次自动分析的决策结果"""
    try:
        decision = agent_controller.get_decision(session_id)
        return {
            "status": "success",
            "session_id": session_id,
            "decision": to_jsonable(decision) if decision is not None else None,
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询决策结果失败: {str(e)}")
