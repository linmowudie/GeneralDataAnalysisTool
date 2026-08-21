"""
backend/Interfaces/controllers/session_registry.py
SessionRegistry：会话注册表

持有 Dict[session_id, WorkflowContext]，内置 per-session asyncio.Lock
（同一会话请求串行化，修复原会话无并发锁缺陷）。
"""

from __future__ import annotations

import sys
import time
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.Services.workflows.context import WorkflowContext  # noqa: E402
from backend.shared.types import SessionNotFound, SessionTimeout  # noqa: E402

logger = logging.getLogger(__name__)


class SessionRegistry:
    """会话注册表（含 per-session 并发锁）"""

    def __init__(self, session_timeout: int = 3600):
        self.session_timeout = session_timeout
        self._contexts: Dict[str, WorkflowContext] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._meta: Dict[str, Dict[str, Any]] = {}
        logger.info("SessionRegistry 初始化完成，超时时间: %d秒", session_timeout)

    # ---------------------------------------------------------------- 创建
    def create(self) -> WorkflowContext:
        session_id = str(uuid.uuid4())
        ctx = WorkflowContext(session_id)
        self._contexts[session_id] = ctx
        self._locks[session_id] = asyncio.Lock()
        self._meta[session_id] = {"last_imported_file": None}
        logger.info("SessionRegistry: 创建会话 %s", session_id)
        return ctx

    # ---------------------------------------------------------------- 获取
    def get(self, session_id: str, touch: bool = True) -> WorkflowContext:
        """获取上下文；不存在抛 SessionNotFound，超时抛 SessionTimeout"""
        ctx = self._contexts.get(session_id)
        if ctx is None:
            raise SessionNotFound(f"会话ID {session_id} 不存在")
        if time.time() - ctx.last_accessed > self.session_timeout:
            self.remove(session_id)
            raise SessionTimeout(f"会话ID {session_id} 已超时")
        if touch:
            ctx.touch()
        return ctx

    def peek(self, session_id: str) -> Optional[WorkflowContext]:
        """只读获取（不校验超时、不刷新访问时间）"""
        return self._contexts.get(session_id)

    def lock(self, session_id: str) -> asyncio.Lock:
        """per-session 并发锁"""
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]

    def meta(self, session_id: str) -> Dict[str, Any]:
        return self._meta.setdefault(session_id, {})

    # ---------------------------------------------------------------- 删除
    def remove(self, session_id: str) -> bool:
        ctx = self._contexts.pop(session_id, None)
        self._locks.pop(session_id, None)
        self._meta.pop(session_id, None)
        if ctx is not None:
            ctx.reset_all()
            logger.info("SessionRegistry: 删除会话 %s", session_id)
            return True
        return False

    # ---------------------------------------------------------------- 维护
    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [
            sid for sid, ctx in self._contexts.items()
            if now - ctx.last_accessed > self.session_timeout
        ]
        for sid in expired:
            self.remove(sid)
        if expired:
            logger.info("SessionRegistry: 清理过期会话 %d 个", len(expired))
        return len(expired)

    def session_ids(self) -> List[str]:
        return list(self._contexts.keys())
