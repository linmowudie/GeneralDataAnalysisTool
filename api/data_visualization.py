from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, List, Optional
import os
import sys
import json

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .session_manager import session_manager

router = APIRouter()

@router.post("/generate-chart")
async def generate_chart(
    session_id: str = Form(...),
    chart_type: str = Form(...),
    parameters: Optional[str] = Form("{}")
):
    """生成图表"""
    try:
        # 解析参数
        params = json.loads(parameters) if parameters else {}
        
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 如果引擎中没有分析数据，使用示例数据
        if engine.analyzed_data is None:
            # 创建示例数据
            import pandas as pd
            data = {
                "x": [1, 2, 3, 4, 5],
                "y": [2, 4, 6, 8, 10],
                "category": ["A", "B", "A", "B", "A"]
            }
            
            df = pd.DataFrame(data)
            
            # 设置分析结果到引擎中
            engine.analyzed_data = {
                'task_type': 'regression',
                'trained_model': None,
                'X_test': df[['x']],
                'y_test': df['y'],
                'predictions': df['y']  # 简化处理，使用实际值作为"预测值"
            }
        
        # 设置可视化参数
        viz_params = {
            "task_type": "regression",
            "model_name": "linearregression",
            "feature": engine.analyzed_data.get('X_test'),
            "target": engine.analyzed_data.get('y_test'),
            "predict": engine.analyzed_data.get('predictions')
        }
        
        # 执行可视化操作
        engine.visualize_data(viz_params)
        
        # 获取可视化结果
        chart_data = engine.visualized_plot
        
        return {
            "session_id": session_id,
            "chart_type": chart_type,
            "parameters": params,
            "chart_data": str(chart_data),  # 简化处理
            "status": "success"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图表生成失败: {str(e)}")

@router.get("/available-charts")
async def get_available_charts():
    """获取可用的图表类型"""
    try:
        chart_types = ["scatter", "line", "bar", "histogram", "box", "violin"]
        return {
            "chart_types": chart_types,
            "count": len(chart_types)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取图表类型列表失败: {str(e)}")