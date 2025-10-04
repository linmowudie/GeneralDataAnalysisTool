from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, List, Optional
import os
import sys
import json
import pandas as pd

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .session_manager import session_manager

router = APIRouter()

@router.post("/clean-data")
async def clean_data(
    session_id: str = Form(...),
    mode: str = Form(...),
    parameters: Optional[str] = Form("{}"),
    is_custom: bool = Form(False)
):
    """清洗数据"""
    try:
        # 解析参数
        params = json.loads(parameters) if parameters else {}
        
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 如果引擎中没有导入的数据，使用示例数据
        if engine.imported_data is None:
            # 创建示例数据进行测试
            data = {
                "feature1": [1, 2, None, 4, 5],
                "feature2": [2, 4, 6, None, 10],
                "target": [3, 6, 9, 12, None]
            }
            df = pd.DataFrame(data)
            engine.imported_data = df
        
        # 解析清洗参数
        params_list = []
        if is_custom and "custom_params" in params:
            params_list = params["custom_params"]
        
        # 执行清洗操作
        engine.clean_data(
            select_mode=mode,
            params_list=params_list,
            is_freedom_params=is_custom
        )
        
        # 获取清洗后的数据
        cleaned_df = engine.cleaned_data
        
        # 将清洗后的数据转换为字典格式
        cleaned_data = cleaned_df.to_dict(orient='records')
        
        return {
            "session_id": session_id,
            "mode": mode,
            "is_custom": is_custom,
            "parameters": params,
            "cleaned_data": cleaned_data,
            "status": "success"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据清洗失败: {str(e)}")

@router.get("/cleaning-modes")
async def get_cleaning_modes():
    """获取可用的数据清洗模式"""
    try:
        modes = ["standard", "strict", "relaxed"]
        return {
            "modes": modes,
            "count": len(modes)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取清洗模式列表失败: {str(e)}")