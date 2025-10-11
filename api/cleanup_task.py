"""
定期清理任务
用于定期清理过期的临时文件和会话
"""

import time
import threading
import shutil
import logging
from pathlib import Path
from typing import Callable
from .session_manager import session_manager

# 配置API日志
from Src.DataAnalyzer.Configs.log_setting import get_component_logger
api_logger = get_component_logger('api', 'cleanup_task')

class CleanupTask:
    """
    定期清理任务
    """
    
    def __init__(self, interval: int = 300):  # 默认5分钟执行一次
        """
        初始化清理任务
        
        Args:
            interval: 清理间隔（秒）
        """
        self.interval = interval
        self.running = False
        self.thread = None
    
    def start(self):
        """
        启动清理任务
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("定期清理任务已启动")
    
    def stop(self):
        """
        停止清理任务
        """
        self.running = False
        if self.thread:
            self.thread.join()
        print("定期清理任务已停止")
    
    def _run(self):
        """
        运行清理任务
        """
        while self.running:
            try:
                # 清理会话管理器中的过期会话
                cleaned_sessions = session_manager.cleanup_expired_sessions()
                if cleaned_sessions > 0:
                    print(f"清除了 {cleaned_sessions} 个过期会话")
                
                # 等待下一个清理周期
                time.sleep(self.interval)
            except Exception as e:
                print(f"清理任务执行出错: {e}")
                time.sleep(self.interval)
    
    def cleanup_temp_directories(self):
        """
        清理临时数据目录
        """
        try:
            # 清理APIOutput目录
            api_output_dir = Path("APIOutput")
            if api_output_dir.exists():
                for item in api_output_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                api_logger.info("APIOutput目录清理完成")
            
            # 清理临时存储目录
            temp_storage_dir = Path("Src/DataAnalyzer/TempStorage")
            if temp_storage_dir.exists():
                for stage in ['imported', 'cleaned', 'analyzed', 'visualized']:
                    stage_path = temp_storage_dir / stage
                    if stage_path.exists():
                        for item in stage_path.iterdir():
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item)
                api_logger.info("临时存储目录清理完成")
        except Exception as e:
            api_logger.error(f"清理临时目录时出错: {e}")


# 全局清理任务实例
cleanup_task = CleanupTask()