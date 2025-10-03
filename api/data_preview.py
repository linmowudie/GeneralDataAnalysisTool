from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import os
import sys

# 将Src目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Src'))

from Src.DataAnalyzer.Analysis import analyzer

router = APIRouter()

@router.get("/data-preview")
async def get_data_preview():
    """获取数据预览"""
    try:
        # 这里需要根据实际实现来获取数据预览
        # 暂时返回示例数据
        preview_data = {
            "success": True,
            "file_name": "sample_data.csv",
            "total_rows": 150,
            "total_columns": 5,
            "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"],
            "preview_data": [
                {
                    "sepal_length": 5.1,
                    "sepal_width": 3.5,
                    "petal_length": 1.4,
                    "petal_width": 0.2,
                    "species": "setosa"
                }
            ]
        }
        return preview_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据预览失败: {str(e)}")

@router.get("/dataset-info")
async def get_dataset_info():
    """获取数据集信息"""
    try:
        # 示例数据
        dataset_info = {
            "dataset_name": "示例数据集",
            "total_records": 150,
            "features_count": 4,
            "target_variable": "species",
            "data_types": {
                "sepal_length": "float",
                "sepal_width": "float",
                "petal_length": "float",
                "petal_width": "float",
                "species": "string"
            }
        }
        return dataset_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据集信息失败: {str(e)}")