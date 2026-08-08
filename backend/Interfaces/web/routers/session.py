"""
backend/Interfaces/web/routers/session.py
/api/session/*：会话管理（契约与原 api/session.py 一致）
"""

from fastapi import APIRouter, Form, HTTPException, Query

from backend.Interfaces.controllers import session_controller
from backend.shared.types import DomainError
from backend.Interfaces.web.errors import to_http_error

router = APIRouter(tags=["会话管理"])


@router.post("/create")
async def create_session():
    """创建新的会话"""
    try:
        session_id = session_controller.create_session()
        return {
            "session_id": session_id,
            "message": "会话创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"会话创建失败: {str(e)}")


@router.post("/reset-step")
async def reset_step(
    session_id: str = Form(...),
    step: str = Form(...)
):
    """重置指定步骤及其后续步骤"""
    try:
        success = session_controller.reset_step(session_id, step)
        if success:
            return {
                "session_id": session_id,
                "step": step,
                "message": f"步骤 {step} 重置成功"
            }
        raise HTTPException(status_code=400, detail=f"步骤 {step} 重置失败")
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"重置步骤失败: {str(e)}")


@router.post("/reset-all")
async def reset_all(
    session_id: str = Form(...)
):
    """重置会话中的所有数据"""
    try:
        success = session_controller.reset_all(session_id)
        if success:
            return {
                "session_id": session_id,
                "message": f"会话 {session_id} 所有数据重置成功"
            }
        raise HTTPException(status_code=400, detail=f"会话 {session_id} 所有数据重置失败")
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"重置所有数据失败: {str(e)}")


@router.get("/step-status")
async def get_step_status(
    session_id: str = Query(...)
):
    """获取步骤状态"""
    try:
        status = session_controller.get_step_status(session_id)
        return {
            "session_id": session_id,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取步骤状态失败: {str(e)}")


@router.post("/end")
async def end_session(
    session_id: str = Form(...)
):
    """结束会话并清理资源"""
    try:
        success = session_controller.end_session(session_id)
        if success:
            return {
                "session_id": session_id,
                "message": "会话结束成功"
            }
        raise HTTPException(status_code=400, detail=f"会话ID {session_id} 不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"会话结束失败: {str(e)}")
