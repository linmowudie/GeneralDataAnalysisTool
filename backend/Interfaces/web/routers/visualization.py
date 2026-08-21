"""
backend/Interfaces/web/routers/visualization.py
/api/visualization/*：数据可视化（generate-chart / available-charts）
"""

import json
import pickle
from typing import Optional

from fastapi import APIRouter, HTTPException, Form

from backend.Interfaces.controllers import session_controller
from backend.shared.types import StepName, DomainError
from backend.Interfaces.web.errors import to_http_error
from backend.Interfaces.web.utils import sample_regression_df
from backend.Infrastructures.storage import temp_storage

router = APIRouter()


def _ensure_analysis_result(session_id: str) -> bool:
    """无分析结果时写入示例结果（与原 api 兜底行为一致），返回是否为示例数据"""
    path = temp_storage._stage_path(session_id, "analyzed")
    if path.exists():
        return False

    df = sample_regression_df()
    sample = {
        'task_type': 'regression',
        'trained_model': None,
        'X_test': df[['x']],
        'y_test': df['y'],
        'predictions': df['y'],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(sample, f)
    return True


@router.post("/generate-chart")
async def generate_chart(
    session_id: str = Form(...),
    chart_type: str = Form(...),
    parameters: Optional[str] = Form("{}")
):
    """生成图表"""
    try:
        # 解析参数
        try:
            params = json.loads(parameters) if parameters else {}
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"参数解析失败: {str(e)}")

        session_controller.get_context(session_id)
        is_sample = _ensure_analysis_result(session_id)

        # 示例兜底时同步补齐分析步骤状态，保证可视化前置条件满足（与原兜底行为一致）
        if is_sample:
            ctx = session_controller.get_context(session_id)
            ctx.steps.complete(StepName.ANALYSIS)
            ctx.steps.lock(StepName.ANALYSIS)

        # 示例数据时使用与原 api 一致的显式参数
        viz_params = {}
        if is_sample:
            df = sample_regression_df()
            viz_params = {
                "param_dict": {
                    "task_type": "regression",
                    "model_name": "linearregression",
                    "feature": df[['x']],
                    "target": df['y'],
                    "predict": df['y'],
                }
            }

        artifact = session_controller.execute_step(session_id, StepName.VISUALIZATION, viz_params)

        return {
            "session_id": session_id,
            "chart_type": chart_type,
            "parameters": params,
            "chart_data": str(artifact.charts),  # 与原契约一致：字符串化
            "status": "success"
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
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
