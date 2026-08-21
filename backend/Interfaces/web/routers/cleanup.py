"""
backend/Interfaces/web/routers/cleanup.py
/api/cleanup/*：清理任务（run / run-step / status / stats）
"""

import logging

from fastapi import APIRouter, HTTPException

from backend.Infrastructures.storage import temp_storage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["清理任务"])


@router.post("/run")
async def run_cleanup():
    """立即执行清理任务（全量清理临时存储）"""
    try:
        stats = temp_storage.clear_all()
        return {"status": "success", "message": "清理任务执行完成", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理任务执行失败: {str(e)}")


@router.post("/run-step")
async def run_step_cleanup(step: str):
    """立即执行指定步骤的清理任务（跨会话清理该阶段临时文件）"""
    try:
        stats = temp_storage.clear_stage_globally(step)
        return {"status": "success", "message": f"步骤 {step} 的清理任务执行完成", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"步骤 {step} 的清理任务执行失败: {str(e)}")


@router.get("/status")
async def get_cleanup_status():
    """获取清理任务状态"""
    return {
        "status": "available",
    }


@router.get("/stats")
async def get_cleanup_stats():
    """获取清理统计信息"""
    # 清理任务是瞬时操作，不保存状态（与原契约一致）
    return {"message": "清理任务是瞬时操作，没有持续的统计信息"}
