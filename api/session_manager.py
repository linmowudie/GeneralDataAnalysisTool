"""
会话管理模块
用于管理不同用户的会话，确保各API操作可以共享同一份临时存储数据
"""

import uuid
import time
from typing import Dict, Any
from Src.DataAnalyzer.core import DataProcessingEngine

# 配置API日志
from Src.DataAnalyzer.Configs.log_setting import get_component_logger
api_logger = get_component_logger('api', 'session_manager')

class SessionManager:
    """
    会话管理器
    管理所有用户的会话和对应的数据处理引擎实例
    """
    
    def __init__(self, session_timeout: int = 3600):
        """
        初始化会话管理器
        
        Args:
            session_timeout: 会话超时时间（秒），默认1小时
        """
        # 存储会话ID与数据处理引擎实例的映射
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = session_timeout
        api_logger.info("会话管理器初始化完成，超时时间: %d秒", session_timeout)
    
    def create_session(self) -> str:
        """
        创建新的会话
        
        Returns:
            str: 会话ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'engine': DataProcessingEngine(auto_cleanup=True),  # 创建引擎时自动清理旧文件
            'created_at': time.time(),
            'last_accessed': time.time()
        }
        api_logger.info("创建新会话: %s", session_id)
        return session_id
    
    def get_engine(self, session_id: str) -> DataProcessingEngine:
        """
        根据会话ID获取数据处理引擎实例
        
        Args:
            session_id: 会话ID
            
        Returns:
            DataProcessingEngine: 数据处理引擎实例
            
        Raises:
            ValueError: 当会话ID不存在时
        """
        if session_id not in self.sessions:
            api_logger.warning("会话ID不存在: %s", session_id)
            raise ValueError(f"会话ID {session_id} 不存在")
        
        # 检查会话是否超时
        session_info = self.sessions[session_id]
        if time.time() - session_info['last_accessed'] > self.session_timeout:
            self.delete_session(session_id)
            api_logger.warning("会话ID已超时: %s", session_id)
            raise ValueError(f"会话ID {session_id} 已超时")
        
        # 更新最后访问时间
        session_info['last_accessed'] = time.time()
        api_logger.debug("获取会话引擎: %s", session_id)
        return session_info['engine']
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        if session_id in self.sessions:
            # 清理引擎中的数据
            engine = self.sessions[session_id]['engine']
            engine.cleanup()
            # 删除会话
            del self.sessions[session_id]
            api_logger.info("删除会话: %s", session_id)
            return True
        api_logger.warning("尝试删除不存在的会话: %s", session_id)
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        
        Returns:
            int: 清理的会话数量
        """
        current_time = time.time()
        expired_sessions = []
        
        # 找出过期的会话
        for session_id, session_info in self.sessions.items():
            if current_time - session_info['last_accessed'] > self.session_timeout:
                expired_sessions.append(session_id)
        
        # 清理过期会话
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        api_logger.info("清理过期会话完成，共清理 %d 个会话", len(expired_sessions))
        return len(expired_sessions)


# 全局会话管理器实例
session_manager = SessionManager()