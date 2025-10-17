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
    
    def cleanup_all_temp_directories(self):
        """
        清理临时数据目录
        """
        try:
            # 清理APIOutput目录
            api_output_dir = Path("APIOutput")
            if api_output_dir.exists():
                for item in api_output_dir.iterdir():
                    try:
                        if item.is_file():
                            size = item.stat().st_size
                            item.unlink()
                            self.stats["files_removed"] += 1
                            self.stats["space_freed"] += size
                        elif item.is_dir():
                            size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                            shutil.rmtree(item)
                            self.stats["space_freed"] += size
                    except Exception as e:
                        api_logger.error(f"清理APIOutput目录中的项目失败 {item}: {e}")
                api_logger.info("APIOutput目录清理完成")
            
            # 清理临时存储目录
            temp_storage_dir = Path("Src/DataAnalyzer/TempStorage")
            if temp_storage_dir.exists():
                for stage in ['imported', 'cleaned', 'analyzed', 'visualized']:
                    stage_path = temp_storage_dir / stage
                    if stage_path.exists():
                        for item in stage_path.iterdir():
                            try:
                                if item.is_file():
                                    size = item.stat().st_size
                                    item.unlink()
                                    self.stats["files_removed"] += 1
                                    self.stats["space_freed"] += size
                                elif item.is_dir():
                                    size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                                    shutil.rmtree(item)
                                    self.stats["space_freed"] += size
                            except Exception as e:
                                api_logger.error(f"清理临时存储目录中的项目失败 {item}: {e}")
                api_logger.info("临时存储目录清理完成")
                
            # 更新上次运行时间
            self.stats["last_run"] = time.time()
        except Exception as e:
            api_logger.error(f"清理临时目录时出错: {e}")

    def cleanup_step_temp_files(self, step: str):
        """
        清理指定步骤的临时文件
        
        Args:
            step: 步骤名称 ('import', 'preview', 'cleaning', 'analysis', 'visualization', 'report')
        """
        step_map = {
            'import': 'imported',
            'preview': 'imported',  # preview使用imported的数据
            'cleaning': 'cleaned',
            'analysis': 'analyzed',
            'visualization': 'visualized',
            'report': 'visualized'  # report使用visualized的数据
        }
        
        try:
            if step not in step_map:
                raise ValueError(f"不支持的步骤: {step}")
                
            stage = step_map[step]
            
            # 清理对应的临时存储目录
            temp_storage_dir = Path("Src/DataAnalyzer/TempStorage") / stage
            if temp_storage_dir.exists():
                for item in temp_storage_dir.iterdir():
                    try:
                        if item.is_file():
                            size = item.stat().st_size
                            item.unlink()
                            self.stats["files_removed"] += 1
                            self.stats["space_freed"] += size
                        elif item.is_dir():
                            size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                            shutil.rmtree(item)
                            self.stats["space_freed"] += size
                    except Exception as e:
                        api_logger.error(f"清理临时存储目录中的项目失败 {item}: {e}")
                api_logger.info(f"步骤 {step} 的临时文件清理完成")
                
            # 如果是导入步骤，还需要清理API输出目录
            if step == 'import':
                api_output_dir = Path("APIOutput")
                if api_output_dir.exists():
                    for item in api_output_dir.iterdir():
                        try:
                            if item.is_file():
                                size = item.stat().st_size
                                item.unlink()
                                self.stats["files_removed"] += 1
                                self.stats["space_freed"] += size
                            elif item.is_dir():
                                size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                                shutil.rmtree(item)
                                self.stats["space_freed"] += size
                        except Exception as e:
                            api_logger.error(f"清理API输出目录中的项目失败 {item}: {e}")
                    api_logger.info("API输出目录清理完成")
                
            # 更新上次运行时间
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