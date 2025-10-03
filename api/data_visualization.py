from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, List, Optional
import os
import sys
import json

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Src.DataAnalyzer.Visualization.interactive import InteractiveVisualization

router = APIRouter()

@router.post("/generate-chart")
async def generate_chart(
    chart_type: str = Form(...),
    parameters: Optional[str] = Form("{}")
):
    """生成图表"""
    try:
        # 解析参数
        params = json.loads(parameters) if parameters else {}
        
        # 创建示例数据
        data = {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10],
            "category": ["A", "B", "A", "B", "A"]
        }
        
        # 设置可视化参数
        viz_params = {
            "data": data,
            "x": "x",
            "y": "y",
            "title": f"{chart_type} Chart",
            "color": "category"
        }
        
        # 创建可视化对象
        viz = InteractiveVisualization(viz_params)
        
        # 根据图表类型生成图表
        if chart_type == "scatter":
            fig = viz.scatter_plot()
        elif chart_type == "line":
            fig = viz.line_plot()
        elif chart_type == "bar":
            fig = viz.bar_plot()
        else:
            raise ValueError(f"不支持的图表类型: {chart_type}")
        
        # 将图表转换为JSON格式
        chart_data = fig.to_json()
        
        return {
            "chart_type": chart_type,
            "parameters": params,
            "chart_data": chart_data,
            "status": "success"
        }
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