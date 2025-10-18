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
    清理任务类
    负责清理临时数据和重置会话状态
    """
    
    def __init__(self):
        """
        初始化清理任务
        """
        # 使用相对路径指定临时存储管理器的存储路径
        self.temp_storage_manager = TempStorageManager("Src/DataAnalyzer/TempStorage")
        self.step_data_manager = StepDataManager(self.temp_storage_manager)
        
        # 配置API日志
        from Src.DataAnalyzer.Configs.log_setting import get_component_logger
        self.logger = get_component_logger('api', 'cleanup_task')

    async def reset_all_data(self, session_id: str) -> Dict[str, Any]:
        """
        重置会话中的所有数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            重置结果
        """
        try:
            self.logger.info(f"开始重置会话 {session_id} 的所有数据")
            
            # 获取会话对应的引擎实例
            engine = session_manager.get_engine(session_id)
            
            # 重置引擎中的所有数据
            engine.cleanup()
            
            # 清理所有临时目录
            stats = self.temp_storage_manager.clear_all_temp_directories()
            self.logger.info(f"临时目录清理完成: {stats}")
            
            return {
                "session_id": session_id,
                "message": "所有数据重置成功",
                "stats": stats
            }
                
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
        except Exception as e:
            self.logger.error(f"数据重置失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"数据重置失败: {str(e)}")

    async def reset_step_data(self, session_id: str, step: str) -> Dict[str, Any]:
        """
        重置会话中的特定步骤数据
        
        Args:
            session_id: 会话ID
            step: 要重置的步骤名称
            
        Returns:
            重置结果
        """
        try:
            self.logger.info(f"开始重置会话 {session_id} 的 {step} 步骤数据")
            
            # 获取会话对应的引擎实例
            engine = session_manager.get_engine(session_id)
            
            # 重置引擎中的特定步骤数据
            engine.reset_step_and_following(step)
            
            # 清理对应步骤的临时文件
            stats = self.step_data_manager.cleanup_step_temp_files(step)
            self.logger.info(f"步骤 {step} 的临时文件清理完成: {stats}")
            
            return {
                "session_id": session_id,
                "step": step,
                "message": f"步骤 {step} 数据重置成功",
                "stats": stats
            }
                
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
        except Exception as e:
            self.logger.error(f"步骤数据重置失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"步骤数据重置失败: {str(e)}")

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
        stats = cleanup_task.temp_storage_manager.clear_all_temp_directories()
        return {"status": "success", "message": "清理任务执行完成", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理任务执行失败: {str(e)}")

@cleanup_task_router.post("/run-step")
async def run_step_cleanup(step: str):
    """
    立即执行指定步骤的清理任务
    """
    try:
        stats = cleanup_task.step_data_manager.cleanup_step_temp_files(step)
        return {"status": "success", "message": f"步骤 {step} 的清理任务执行完成", "stats": stats}
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
    # 这里返回一个默认的空统计信息，因为清理任务是瞬时操作，不保存状态
    return {"message": "清理任务是瞬时操作，没有持续的统计信息"}
