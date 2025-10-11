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
api_logger = get_component_logger('api', 'data_analysis')

router = APIRouter()

@router.post("/run-analysis")
async def run_analysis(
    session_id: str = Form(...),
    model_type: str = Form(...),
    parameters: str = Form("{}")
):
    """运行数据分析"""
    try:
        api_logger.info(f"开始数据分析，模型类型: {model_type}，会话ID: {session_id}")
        
        # 解析参数
        try:
            params_dict = json.loads(parameters) if parameters else {}
        except json.JSONDecodeError as e:
            api_logger.error(f"参数解析失败: {str(e)}")
            raise HTTPException(status_code=400, detail=f"参数解析失败: {str(e)}")
        
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 执行数据分析
        result = engine.analyze_data(
            model=model_type,
            random_state=params_dict.get("random_state", 42),
            is_split=params_dict.get("is_split", True),
            split_ratio=params_dict.get("split_ratio", 0.8),
            feature_cols=params_dict.get("feature_cols"),
            target_col=params_dict.get("target_col"),
            is_return_model_param=params_dict.get("is_return_model_param", False),
            metrics_list=params_dict.get("metrics_list"),
            is_return_model_score=params_dict.get("is_return_model_score", True),
            is_return_training_set=params_dict.get("is_return_training_set", False),
            is_return_model_predicting_set=params_dict.get("is_return_model_predicting_set", False),
            feature_cols_encoding=params_dict.get("feature_cols_encoding", "onehot"),
            target_col_encoding=params_dict.get("target_col_encoding", "label"),
            test_set=params_dict.get("test_set"),
            model_params=params_dict.get("model_params")
        )
        
        # 标记分析步骤为完成并锁定
        engine.mark_step_completed('analysis')
        engine.lock_step('analysis')
        
        api_logger.info("数据分析完成")
        return {
            "session_id": session_id,
            "model_type": model_type,
            "message": "数据分析完成",
            "result": result
        }
    except ValueError as e:
        api_logger.error(f"会话错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        api_logger.error(f"数据分析失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"数据分析失败: {str(e)}")

@router.get("/available-models")
async def get_available_models():
    """获取可用的分析模型"""
    try:
        api_logger.info("获取可用模型列表")
        # 从配置管理器获取模型列表
        from Src.DataAnalyzer.Configs.config_manager import MODEL_CONFIG
        model_type: List[str] = list(MODEL_CONFIG.keys())
        api_logger.info(f"可用模型列表: {model_type}")
        return {
            "models": model_type
        }
    except Exception as e:
        api_logger.error(f"获取可用模型失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"获取可用模型失败: {str(e)}")