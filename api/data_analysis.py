from fastapi import APIRouter, Form, HTTPException
from typing import Dict, Any, List, Optional
import json
import sys
import os
import pandas as pd

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
        try:
            engine = session_manager.get_engine(session_id)
            if engine is None:
                raise ValueError(f"找不到会话ID: {session_id}")
        except Exception as e:
            api_logger.error(f"获取会话引擎失败: {str(e)}")
            raise HTTPException(status_code=404, detail=f"会话不存在: {str(e)}")
        
        # 确保数据可用
        if engine.cleaned_data is None and engine.imported_data is None:
            api_logger.error("会话中没有可用的数据")
            raise HTTPException(status_code=400, detail="会话中没有可用的数据，请先导入或清洗数据")
        
        # 执行数据分析
        try:
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
        except ValueError as e:
            # 模型参数或配置错误
            api_logger.error(f"模型配置错误: {str(e)}")
            raise HTTPException(status_code=400, detail=f"模型配置错误: {str(e)}")
        except Exception as e:
            # 其他分析错误
            api_logger.error(f"数据分析过程中出错: {str(e)}")
            raise HTTPException(status_code=500, detail=f"数据分析过程中出错: {str(e)}")
        
        # 标记分析步骤为完成并锁定
        engine.mark_step_completed('analysis')
        engine.lock_step('analysis')
        
        # 处理结果，移除不可JSON序列化的对象并确保正确的格式
        def make_serializable(data):
            if isinstance(data, dict):
                filtered_data = {}
                for key, value in data.items():
                    # 跳过训练好的模型实例
                    if key == 'trained_model':
                        continue
                    
                    # 确保None值转换为空对象，避免null字段
                    if value is None:
                        filtered_data[key] = {}
                    else:
                        filtered_data[key] = make_serializable(value)
                return filtered_data
            elif isinstance(data, list):
                return [make_serializable(item) for item in data]
            elif isinstance(data, (pd.DataFrame, pd.Series)):
                # 将DataFrame或Series转换为字典
                return data.to_dict()
            elif isinstance(data, np.ndarray):
                # 确保NumPy数组转换为列表
                return data.tolist()
            elif isinstance(data, (np.integer, np.floating)):
                # 转换NumPy标量为Python原生类型
                return data.item()
            else:
                return data
        
        # 处理结果使其可序列化
        try:
            serializable_result = make_serializable(result)
        except Exception as e:
            api_logger.error(f"结果序列化失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"结果序列化失败: {str(e)}")
        
        api_logger.info("数据分析完成")
        return {
            "session_id": session_id,
            "model_type": model_type,
            "message": "数据分析完成",
            "result": serializable_result
        }
    except HTTPException:
        # 已处理的HTTP异常直接抛出
        raise
    except Exception as e:
        # 捕获所有其他未处理的异常
        api_logger.error(f"发生未预期的错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

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

@router.get("/data-columns/{session_id}")
async def get_data_columns(session_id: str):
    """获取会话对应数据的列信息"""
    try:
        api_logger.info(f"获取会话 {session_id} 的数据列信息")
        
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 尝试获取清洗后的数据
        if engine.cleaned_data is None:
            engine.cleaned_data = engine.temp_storage.load_data('cleaned', 'cleaned_data.pkl')
            # 如果清洗数据不存在，尝试加载导入的数据
            if engine.cleaned_data is None:
                engine.imported_data = engine.temp_storage.load_data('imported', 'imported_data.pkl')
                if engine.imported_data is None:
                    raise ValueError("未找到数据，请先导入数据")
                # 使用导入的数据
                engine.cleaned_data = engine.imported_data.copy()
        
        # 获取列名
        columns = list(engine.cleaned_data.columns)
        api_logger.info(f"获取到 {len(columns)} 列数据")
        
        return {
            "columns": columns
        }
    except ValueError as e:
        api_logger.error(f"获取数据列信息失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"获取数据列信息失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"获取数据列信息失败: {str(e)}")

@router.get("/model-config")
async def get_model_config():
    """获取模型配置信息"""
    try:
        api_logger.info("获取模型配置信息")
        
        # 从配置管理器获取模型配置
        from Src.DataAnalyzer.Configs.config_manager import MODEL_CONFIG
        
        api_logger.info("成功获取模型配置")
        return {
            "config": MODEL_CONFIG
        }
    except Exception as e:
        api_logger.error(f"获取模型配置失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"获取模型配置失败: {str(e)}")
