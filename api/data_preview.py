from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import os
import sys

# 将Src目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .session_manager import session_manager

router = APIRouter()

@router.get("/data-preview")
async def get_data_preview(session_id: str = Query(...)):
    """获取数据预览"""
    try:
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 尝试从引擎中获取导入的数据
        imported_data = engine.imported_data
        
        # 如果引擎中没有数据，尝试从临时存储加载
        if imported_data is None:
            imported_data = engine.temp_storage.load_data('imported', 'imported_data.pkl')
        
        # 如果仍然没有数据，则使用示例数据
        if imported_data is None:
            import pandas as pd
            # 创建示例数据
            data = {
                "sepal_length": [5.1, 4.9, 4.7, 4.6, 5.0],
                "sepal_width": [3.5, 3.0, 3.2, 3.1, 3.6],
                "petal_length": [1.4, 1.4, 1.3, 1.5, 1.4],
                "petal_width": [0.2, 0.2, 0.2, 0.2, 0.2],
                "species": ["setosa", "setosa", "setosa", "setosa", "setosa"]
            }
            imported_data = pd.DataFrame(data)
            file_name = "sample_data.csv"
        else:
            file_name = getattr(engine, '_last_imported_file', 'imported_data.csv')
        
        # 构建预览数据
        preview_data = {
            "session_id": session_id,
            "success": True,
            "file_name": file_name,
            "total_rows": len(imported_data),
            "total_columns": len(imported_data.columns),
            "columns": list(imported_data.columns),
            "preview_data": imported_data.head().to_dict(orient='records')
        }
        
        return preview_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据预览失败: {str(e)}")

@router.get("/dataset-info")
async def get_dataset_info(session_id: str = Query(...)):
    """获取数据集信息"""
    try:
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 尝试从引擎中获取导入的数据
        imported_data = engine.imported_data
        
        # 如果引擎中没有数据，尝试从临时存储加载
        if imported_data is None:
            imported_data = engine.temp_storage.load_data('imported', 'imported_data.pkl')
        
        # 如果仍然没有数据，则使用示例数据
        if imported_data is None:
            import pandas as pd
            # 创建示例数据
            data = {
                "sepal_length": [5.1, 4.9, 4.7, 4.6, 5.0],
                "sepal_width": [3.5, 3.0, 3.2, 3.1, 3.6],
                "petal_length": [1.4, 1.4, 1.3, 1.5, 1.4],
                "petal_width": [0.2, 0.2, 0.2, 0.2, 0.2],
                "species": ["setosa", "setosa", "setosa", "setosa", "setosa"]
            }
            imported_data = pd.DataFrame(data)
            dataset_name = "示例数据集"
        else:
            dataset_name = "导入的数据集"
        
        # 构建数据集信息
        dataset_info = {
            "session_id": session_id,
            "dataset_name": dataset_name,
            "total_records": len(imported_data),
            "features_count": len(imported_data.columns) - 1 if len(imported_data.columns) > 0 else 0,  # 假设最后一列是目标变量
            "target_variable": imported_data.columns[-1] if len(imported_data.columns) > 0 else None,
            "data_types": {col: str(imported_data[col].dtype) for col in imported_data.columns}
        }
        
        return dataset_info
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据集信息失败: {str(e)}")