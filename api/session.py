from fastapi import APIRouter, Form, HTTPException, Query
from typing import Dict, Any
import sys
import os

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .session_manager import session_manager

# 配置API日志
from Src.DataAnalyzer.Configs.log_setting import get_component_logger
api_logger = get_component_logger('api', 'session')

router = APIRouter(
    tags=["会话管理"]
)

@router.post("/create")
async def create_session():
    """创建新的会话"""
    try:
        api_logger.info("创建新的会话")
        session_id = session_manager.create_session()
        api_logger.info(f"会话创建成功: {session_id}")
        return {
            "session_id": session_id,
            "message": "会话创建成功"
        }
    except Exception as e:
        api_logger.error(f"会话创建失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话创建失败: {str(e)}")

@router.post("/reset-step")
async def reset_step(
    session_id: str = Form(...),
    step: str = Form(...)
):
    """重置指定步骤及其后续步骤"""
    try:
        api_logger.info(f"重置步骤: {step}，会话ID: {session_id}")
        success = session_manager.reset_session_step(session_id, step)
        if success:
            api_logger.info(f"步骤 {step} 重置成功")
            return {
                "session_id": session_id,
                "step": step,
                "message": f"步骤 {step} 重置成功"
            }
        else:
            api_logger.warning(f"步骤 {step} 重置失败")
            raise HTTPException(status_code=400, detail=f"步骤 {step} 重置失败")
    except ValueError as e:
        api_logger.error(f"会话错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        api_logger.error(f"重置步骤失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"重置步骤失败: {str(e)}")

@router.post("/reset-all")
async def reset_all(
    session_id: str = Form(...)
):
    """重置会话中的所有数据"""
    try:
        api_logger.info(f"重置所有数据，会话ID: {session_id}")
        success = session_manager.reset_all_session_data(session_id)
        if success:
            api_logger.info(f"会话 {session_id} 所有数据重置成功")
            return {
                "session_id": session_id,
                "message": f"会话 {session_id} 所有数据重置成功"
            }
        else:
            api_logger.warning(f"会话 {session_id} 所有数据重置失败")
            raise HTTPException(status_code=400, detail=f"会话 {session_id} 所有数据重置失败")
    except ValueError as e:
        api_logger.error(f"会话错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        api_logger.error(f"重置所有数据失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"重置所有数据失败: {str(e)}")

@router.get("/step-status")
async def get_step_status(
    session_id: str = Query(...)
):
    """获取步骤状态"""
    try:
        api_logger.info(f"获取步骤状态，会话ID: {session_id}")
        status = session_manager.get_session_step_status(session_id)
        api_logger.info(f"步骤状态获取成功: {status}")
        return {
            "session_id": session_id,
            "status": status
        }
    except ValueError as e:
        api_logger.error(f"会话错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        api_logger.error(f"获取步骤状态失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"获取步骤状态失败: {str(e)}")

@router.post("/end")
async def end_session(
    session_id: str = Form(...)
):
    """结束会话并清理资源"""
    try:
        api_logger.info(f"结束会话: {session_id}")
        success = session_manager.delete_session(session_id)
        if success:
            api_logger.info(f"会话结束成功: {session_id}")
            return {
                "session_id": session_id,
                "message": "会话结束成功"
            }
        else:
            api_logger.warning(f"会话ID不存在: {session_id}")
            raise HTTPException(status_code=400, detail=f"会话ID {session_id} 不存在")
    except Exception as e:
        api_logger.error(f"会话结束失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话结束失败: {str(e)}")