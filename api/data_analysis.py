from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, List, Optional
import os
import sys
import json
import pandas as pd

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Src.DataAnalyzer.AnalysisModule.analyzer import analyze_data, AnalyzeData

router = APIRouter()

@router.post("/run-analysis")
async def run_analysis(
    model_type: str = Form(...),
    parameters: Optional[str] = Form("{}")
):
    """运行数据分析"""
    try:
        # 解析参数
        params = json.loads(parameters) if parameters else {}
        
        # 创建示例数据进行测试
        # 在实际应用中，这些数据应该从数据库或文件中加载
        data = {
            "feature1": [1, 2, 3, 4, 5],
            "feature2": [2, 4, 6, 8, 10],
            "target": [3, 6, 9, 12, 15]
        }
        df = pd.DataFrame(data)
        
        # 调用分析器执行分析
        result = analyze_data(df, model_type, **params)
        
        return {
            "model_type": model_type,
            "parameters": params,
            "result": result,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"分析执行失败: {str(e)}")

@router.get("/available-models")
async def get_available_models():
    """获取可用的分析模型"""
    try:
        analyzer = AnalyzeData(pd.DataFrame(), "linearregression")  # 创建实例以获取模型列表
        models = analyzer.get_supported_models()
        return {
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取模型列表失败: {str(e)}")