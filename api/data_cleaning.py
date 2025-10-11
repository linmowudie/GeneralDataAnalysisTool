from fastapi import APIRouter, Form, HTTPException
from typing import Dict, Any, List, Optional
import json
import sys
import os

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .session_manager import session_manager

# 配置API日志
from Src.DataAnalyzer.Configs.log_setting import get_component_logger
api_logger = get_component_logger('api', 'data_cleaning')

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
        api_logger.info(f"开始数据清洗，模式: {mode}，会话ID: {session_id}")
        
        # 解析参数
        try:
            params_dict = json.loads(parameters) if parameters else {}
        except json.JSONDecodeError as e:
            api_logger.error(f"参数解析失败: {str(e)}")
            raise HTTPException(status_code=400, detail=f"参数解析失败: {str(e)}")
        
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 执行数据清洗
        custom_params = params_dict.get("custom_params", [])
        engine.clean_data(
            select_mode=mode,
            params_list=custom_params if is_custom else [],
            is_freedom_params=is_custom,
            target_col=target_col
        )
        
        # 标记清洗步骤为完成并锁定
        engine.mark_step_completed('cleaning')
        engine.lock_step('cleaning')
        
        api_logger.info("数据清洗完成")
        return {
            "session_id": session_id,
            "mode": mode,
            "message": "数据清洗完成"
        }
    except ValueError as e:
        api_logger.error(f"会话错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        api_logger.error(f"数据清洗失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"数据清洗失败: {str(e)}")

@router.get("/cleaning-modes")
async def get_cleaning_modes():
    """获取可用的清洗模式"""
    try:
        api_logger.info("获取清洗模式列表")
        # 这里应该从实际的清洗模块获取模式列表
        modes = ["standard", "strict", "relaxed", "custom"]
        api_logger.info(f"清洗模式列表: {modes}")
        return {
            "modes": modes
        }
    except Exception as e:
        api_logger.error(f"获取清洗模式失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"获取清洗模式失败: {str(e)}")