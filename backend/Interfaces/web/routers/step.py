"""
backend/Interfaces/web/routers/step.py
/api/step/*：步骤锁管理（绝对路径注册，Query 参数，契约与原 api/step_lock.py 一致）
"""

from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Query

from backend.Interfaces.controllers import session_controller, StepController
from backend.shared.types import DomainError
from backend.Interfaces.web.errors import to_http_error

router = APIRouter(tags=["步骤锁管理"])

step_controller = StepController(session_controller)


@router.post("/api/step/lock", response_model=Dict[str, Any])
async def lock_step(
    session_id: str = Query(..., description="会话ID"),
    step: str = Query(..., description="要锁定的步骤名称")
):
    """锁定指定的步骤（可用步骤：import/preview/cleaning/analysis/visualization/report）"""
    try:
        return step_controller.lock(session_id, step)
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"锁定步骤时发生错误: {str(e)}")


@router.post("/api/step/unlock", response_model=Dict[str, Any])
async def unlock_step(
    session_id: str = Query(..., description="会话ID"),
    step: str = Query(..., description="要解锁的步骤名称")
):
    """解锁指定的步骤"""
    try:
        return step_controller.unlock(session_id, step)
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解锁步骤时发生错误: {str(e)}")


@router.get("/api/step/status", response_model=Dict[str, Any])
async def get_step_status(
    session_id: str = Query(..., description="会话ID")
):
    """获取会话中所有步骤的状态"""
    try:
        status = step_controller.status(session_id)
        return {
            "status": "success",
            "data": status
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取步骤状态时发生错误: {str(e)}")


@router.post("/api/step/lock-multiple", response_model=Dict[str, Any])
async def lock_multiple_steps(
    session_id: str = Query(..., description="会话ID"),
    steps: List[str] = Query(..., description="要锁定的步骤名称列表")
):
    """同时锁定多个步骤"""
    try:
        return step_controller.lock_multiple(session_id, steps)
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"锁定多个步骤时发生错误: {str(e)}")
