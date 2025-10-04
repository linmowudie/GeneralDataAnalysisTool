"""
模型提取 API 模块
提供模型转移和管理功能的API接口
"""

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import sys
import os

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 导入PythonScripts中的模型管理功能
from PythonScripts.model_extractor import transfer_model, manage_auto_saved_models

router = APIRouter(
    prefix="/api/model",
    tags=["模型管理"]
)

@router.post("/transfer", summary="转移模型")
async def transfer_model_endpoint(
    model_name: str = Query(None, description="要转移的模型文件名，不指定则转移最新的模型")
):
    """
    将自动保存的模型转移到用户提取目录
    
    - **model_name**: 指定要转移的模型文件名，如果不指定则转移最新的模型
    """
    try:
        project_root = Path(__file__).parent.parent
        auto_save_dir = project_root / "ModelOutput" / "自动保存"
        user_extract_dir = project_root / "ModelOutput" / "用户提取"
        
        result = transfer_model(auto_save_dir, user_extract_dir, model_name)
        if result:
            return {
                "success": True, 
                "message": f"模型 '{model_name or 'latest'}' 已成功转移"
            }
        else:
            raise HTTPException(status_code=400, detail="模型转移失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型转移过程中发生错误: {str(e)}")

@router.post("/manage", summary="管理自动保存的模型")
async def manage_models_endpoint(
    max_models: int = Query(5, description="自动保存目录中最大模型文件数量")
):
    """
    管理自动保存目录中的模型数量，删除多余的旧模型文件
    
    - **max_models**: 自动保存目录中最大模型文件数量，默认为5
    """
    try:
        project_root = Path(__file__).parent.parent
        auto_save_dir = project_root / "ModelOutput" / "自动保存"
        
        removed_files = manage_auto_saved_models(auto_save_dir, max_models)
        
        return {
            "success": True,
            "message": f"自动保存目录管理完成，删除了 {len(removed_files)} 个旧模型文件",
            "removed_files": removed_files,
            "max_models": max_models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型管理过程中发生错误: {str(e)}")

@router.get("/list", summary="列出自动保存的模型")
async def list_auto_saved_models():
    """
    列出自动保存目录中的所有模型文件
    """
    try:
        project_root = Path(__file__).parent.parent
        auto_save_dir = project_root / "ModelOutput" / "自动保存"
        
        # 确保目录存在
        auto_save_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有模型文件
        model_files = []
        for file_path in auto_save_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.pkl', '.pickle']:
                stat = file_path.stat()
                model_files.append({
                    "name": file_path.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        
        # 按修改时间排序（最新的在前）
        model_files.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "success": True,
            "models": model_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表时发生错误: {str(e)}")