"""
清理任务
用于清理临时文件和会话
"""

import time
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List
from .session_manager import session_manager
from fastapi import APIRouter, HTTPException

# 配置API日志
from Src.DataAnalyzer.Configs.log_setting import get_component_logger
api_logger = get_component_logger('api', 'cleanup_task')

# 从TempStorageManager导入清理功能
from Src.DataAnalyzer.TempStorage.manager import TempStorageManager, StepDataManager

class CleanupTask:
    """
    清理任务
    """

    step: List[str] = ["imported", "cleaned", "analyzed", "visualized"]
    
    def __init__(self):
        """
        初始化清理任务
        """
        # 统计信息
        self.stats = {
            "files_removed": 0,
            "space_freed": 0,  # 以字节为单位
            "sessions_closed": 0,
            "last_run": None
        }
        # 初始化临时存储管理器
        self.temp_storage_manager = TempStorageManager("Src/DataAnalyzer/TempStorage")
        self.step_data_manager = StepDataManager(self.temp_storage_manager)
    
    def cleanup_all_temp_directories(self):
        """
        清理临时数据目录
        """
        try:
            stats = self.temp_storage_manager.clear_all_temp_directories()
            # 更新统计信息
            self.stats["files_removed"] += stats["files_removed"]
            self.stats["space_freed"] += stats["space_freed"]
            self.stats["last_run"] = time.time()
        except Exception as e:
            api_logger.error(f"清理临时目录时出错: {e}")

    def cleanup_step_temp_files(self, step: str):
        """
        清理指定步骤的临时文件
        
        Args:
            step: 步骤名称 ('import', 'preview', 'cleaning', 'analysis', 'visualization', 'report')
        """
        try:
            stats = self.step_data_manager.cleanup_step_temp_files(step)
            # 更新统计信息
            self.stats["files_removed"] += stats["files_removed"]
            self.stats["space_freed"] += stats["space_freed"]
            self.stats["last_run"] = time.time()
        except Exception as e:
            api_logger.error(f"清理步骤 {step} 的临时文件时出错: {e}")
            raise


# 全局清理任务实例
cleanup_task = CleanupTask()


# API路由部分
# ==============================================================================


# 创建清理任务API路由
cleanup_task_router = APIRouter(tags=["清理任务"])

@cleanup_task_router.post("/run")
async def run_cleanup():
    """
    立即执行清理任务
    """
    try:
        cleanup_task.cleanup_all_temp_directories()
        return {"status": "success", "message": "清理任务执行完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理任务执行失败: {str(e)}")

@cleanup_task_router.post("/run-step")
async def run_step_cleanup(step: str):
    """
    立即执行指定步骤的清理任务
    """
    try:
        cleanup_task.cleanup_step_temp_files(step)
        return {"status": "success", "message": f"步骤 {step} 的清理任务执行完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"步骤 {step} 的清理任务执行失败: {str(e)}")

@cleanup_task_router.get("/status")
async def get_cleanup_status():
    """
    获取清理任务状态
    """
    return {
        "status": "available",
    }

@cleanup_task_router.get("/stats")
async def get_cleanup_stats():
    """
    获取清理统计信息
    """
    return cleanup_task.stats