"""
backend/Interfaces/web/routers/cleaning.py
/api/cleaning/*：数据清洗（clean-data / cleaning-modes）
"""

import json
from typing import Optional

from fastapi import APIRouter, Form, HTTPException

from backend.Interfaces.controllers import session_controller
from backend.shared.types import StepName, DomainError
from backend.Interfaces.web.errors import to_http_error

router = APIRouter()


@router.post("/clean-data")
async def clean_data(
    session_id: str = Form(...),
    mode: str = Form(...),
    is_custom: bool = Form(False),
    parameters: str = Form("{}"),
    target_col: Optional[str] = Form(None)
):
    """数据清洗"""
    try:
        # 解析参数
        try:
            params_dict = json.loads(parameters) if parameters else {}
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"参数解析失败: {str(e)}")

        custom_params = params_dict.get("custom_params", [])
        session_controller.execute_step(session_id, StepName.CLEANING, {
            "select_mode": mode,
            "params_list": custom_params if is_custom else [],
            "is_freedom_params": is_custom,
            "target_col": target_col,
        })

        return {
            "session_id": session_id,
            "mode": mode,
            "message": "数据清洗完成"
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据清洗失败: {str(e)}")


@router.get("/cleaning-modes")
async def get_cleaning_modes():
    """获取可用的清洗模式"""
    try:
        modes = ["standard", "strict", "relaxed", "custom"]
        return {
            "modes": modes
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取清洗模式失败: {str(e)}")
