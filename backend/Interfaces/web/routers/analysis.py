"""
backend/Interfaces/web/routers/analysis.py
/api/analysis/*：数据分析（run-analysis / available-models / model-config / data-columns/{session_id}）
"""

import json
import pickle

from fastapi import APIRouter, Form, HTTPException

from backend.Interfaces.controllers import session_controller
from backend.shared.types import StepName, DomainError
from backend.Interfaces.web.errors import to_http_error
from backend.Infrastructures.serialization import make_serializable
from backend.Infrastructures.storage import temp_storage
from backend.Models.registry import model_registry

router = APIRouter()


def _load_analysis_result(session_id: str) -> dict:
    """读取分析步骤落盘的完整结果（含模型实例）"""
    path = temp_storage._stage_path(session_id, "analyzed")
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return pickle.load(f)


@router.post("/run-analysis")
async def run_analysis(
    session_id: str = Form(...),
    model_type: str = Form(...),
    parameters: str = Form("{}")
):
    """运行数据分析"""
    try:
        # 解析参数
        try:
            params_dict = json.loads(parameters) if parameters else {}
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"参数解析失败: {str(e)}")

        # 执行分析步骤（参数与前端契约一一对应）
        session_controller.execute_step(session_id, StepName.ANALYSIS, {
            "model_type": model_type,
            **params_dict,
        })

        # 读取完整分析结果并序列化（跳过 trained_model 实例，与原契约一致）
        try:
            result = _load_analysis_result(session_id)
            result.pop("trained_model", None)
            serializable_result = make_serializable(result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"结果序列化失败: {str(e)}")

        return {
            "session_id": session_id,
            "model_type": model_type,
            "message": "数据分析完成",
            "result": serializable_result
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/available-models")
async def get_available_models():
    """获取可用的分析模型"""
    try:
        return {
            "models": model_registry.list_models()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取可用模型失败: {str(e)}")


@router.get("/data-columns/{session_id}")
async def get_data_columns(session_id: str):
    """获取会话对应数据的列信息（清洗后优先，回落导入数据）"""
    try:
        session_controller.get_context(session_id)

        df = temp_storage.load_dataframe(session_id, "cleaned")
        if df is None:
            df = temp_storage.load_dataframe(session_id, "imported")
        if df is None:
            raise HTTPException(status_code=400, detail="未找到数据，请先导入数据")

        return {
            "columns": list(df.columns)
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据列信息失败: {str(e)}")


@router.get("/model-config")
async def get_model_config():
    """获取模型配置信息"""
    try:
        return {
            "config": model_registry.get_full_config()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取模型配置失败: {str(e)}")
