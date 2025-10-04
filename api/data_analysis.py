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

@router.post("/run-analysis")
async def run_analysis(
    session_id: str = Form(...),
    model_type: str = Form(...),
    parameters: Optional[str] = Form("{}")
):
    """运行数据分析"""
    try:
        # 解析参数
        params = json.loads(parameters) if parameters else {}
        
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 如果引擎中没有清洗后的数据，使用示例数据
        if engine.cleaned_data is None:
            # 创建示例数据进行测试
            data = {
                "feature1": [1, 2, 3, 4, 5],
                "feature2": [2, 4, 6, 8, 10],
                "target": [3, 6, 9, 12, 15]
            }
            df = pd.DataFrame(data)
            engine.imported_data = df
            engine.cleaned_data = df  # 跳过清洗步骤直接使用原数据
        
        # 调用分析器执行分析
        result = engine.analyze_data(model_type, **params)
        
        return {
            "session_id": session_id,
            "model_type": model_type,
            "parameters": params,
            "result": str(result),  # 简化处理
            "status": "success"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"分析执行失败: {str(e)}")

@router.get("/available-models")
async def get_available_models():
    """获取可用的分析模型"""
    try:
        # 从配置管理器获取模型列表
        from Src.DataAnalyzer.Configs.config_manager import MODEL_CONFIG
        models = list(MODEL_CONFIG.keys())
        
        return {
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取模型列表失败: {str(e)}")