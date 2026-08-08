"""
backend/Interfaces/web/routers/preview.py
/api/preview/*：数据预览（data-preview / dataset-info，无数据时回落示例数据）
"""

from fastapi import APIRouter, HTTPException, Query

from backend.Interfaces.controllers import session_controller
from backend.shared.types import DomainError
from backend.Interfaces.web.errors import to_http_error
from backend.Interfaces.web.utils import sample_iris_df
from backend.Infrastructures.storage import temp_storage

router = APIRouter()


@router.get("/data-preview")
async def get_data_preview(session_id: str = Query(...)):
    """获取数据预览"""
    try:
        session_controller.get_context(session_id)

        df = temp_storage.load_dataframe(session_id, "imported")
        if df is None:
            df = sample_iris_df()
            file_name = "sample_data.csv"
        else:
            file_name = session_controller.get_last_imported_file(session_id) or "imported_data.csv"

        return {
            "session_id": session_id,
            "success": True,
            "file_name": file_name,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "preview_data": df.head().to_dict(orient='records')
        }
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据预览失败: {str(e)}")


@router.get("/dataset-info")
async def get_dataset_info(session_id: str = Query(...)):
    """获取数据集信息"""
    try:
        session_controller.get_context(session_id)

        df = temp_storage.load_dataframe(session_id, "imported")
        if df is None:
            df = sample_iris_df()
            dataset_name = "示例数据集"
        else:
            dataset_name = "导入的数据集"

        return {
            "session_id": session_id,
            "dataset_name": dataset_name,
            "total_records": len(df),
            "features_count": len(df.columns) - 1 if len(df.columns) > 0 else 0,
            "target_variable": df.columns[-1] if len(df.columns) > 0 else None,
            "data_types": {col: str(df[col].dtype) for col in df.columns}
        }
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据集信息失败: {str(e)}")
