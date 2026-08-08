"""
backend/Interfaces/web/errors.py
领域异常 -> HTTP 异常统一映射
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import HTTPException

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import DomainError  # noqa: E402


def to_http_error(e: DomainError) -> HTTPException:
    """按领域异常自带的 http_status 映射"""
    return HTTPException(status_code=e.http_status, detail=str(e))
