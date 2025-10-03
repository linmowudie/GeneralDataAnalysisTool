from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, List, Optional
import os
import sys
import json
import pandas as pd

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Src.DataAnalyzer.ModuleInterfaces.data_cleaning import CleanDataMode

router = APIRouter()

@router.post("/clean-data")
async def clean_data(
    mode: str = Form(...),
    parameters: Optional[str] = Form("{}"),
    is_custom: bool = Form(False)
):
    """清洗数据"""
    try:
        # 解析参数
        params = json.loads(parameters) if parameters else {}
        
        # 创建示例数据进行测试
        # 在实际应用中，这些数据应该从数据库或文件中加载
        data = {
            "feature1": [1, 2, None, 4, 5],
            "feature2": [2, 4, 6, None, 10],
            "target": [3, 6, 9, 12, None]
        }
        df = pd.DataFrame(data)
        
        # 解析清洗参数
        params_list = []
        if is_custom and "custom_params" in params:
            params_list = params["custom_params"]
        
        # 创建清洗器实例
        cleaner = CleanDataMode(df, mode, params_list, is_custom)
        cleaned_df = cleaner.clean_data()
        
        # 将清洗后的数据转换为字典格式
        cleaned_data = cleaned_df.to_dict(orient='records')
        
        return {
            "mode": mode,
            "is_custom": is_custom,
            "parameters": params,
            "cleaned_data": cleaned_data,
            "status": "success"
        }
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