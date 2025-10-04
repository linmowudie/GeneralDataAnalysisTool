"""
定期清理任务
用于定期清理过期的临时文件和会话
"""

import time
import threading
from typing import Callable
from .session_manager import session_manager


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


# 全局清理任务实例
cleanup_task = CleanupTask()