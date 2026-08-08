"""
backend/Interfaces/web/routers/data_import.py
/api/import/*：数据导入（upload-file / streaming-upload-file / import-from-database）
"""

import shutil

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.Interfaces.controllers import session_controller
from backend.shared.types import StepName, DomainError
from backend.Interfaces.web.errors import to_http_error
from backend.Infrastructures.storage.temp_storage import PROJECT_ROOT

router = APIRouter()

# 上传文件落地目录（与原 api 一致）
API_OUTPUT_DIR = PROJECT_ROOT / "APIOutput"
API_OUTPUT_DIR.mkdir(exist_ok=True)


def _run_import(session_id: str, params: dict, filename: str):
    """会话校验 -> 记录文件名 -> 级联重置后执行导入步骤"""
    ctx = session_controller.get_context(session_id)
    # 重新导入：级联清理后续步骤状态与数据
    ctx.reset_step(StepName.IMPORT)
    session_controller.set_last_imported_file(session_id, filename)
    return session_controller.execute_step(session_id, StepName.IMPORT, params)


@router.post("/upload-file")
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """上传并导入文件"""
    try:
        if not file.filename:
            raise ValueError("文件名为空")
        file_path = API_OUTPUT_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        _run_import(session_id, {
            "resource_path": str(file_path),
            "resource_type": file.filename.split('.')[-1] if file.filename else 'csv',
        }, file.filename)

        return {"message": f"文件 {file.filename} 上传并导入成功", "session_id": session_id}
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件上传失败: {str(e)}")


@router.post("/streaming-upload-file")
async def streaming_upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """流式上传并导入文件，适用于大文件"""
    try:
        if not file.filename:
            raise ValueError("文件名为空")
        file_path = API_OUTPUT_DIR / file.filename
        file_extension = file.filename.split('.')[-1].lower() if file.filename else 'csv'

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        params = {
            "resource_path": str(file_path),
            "resource_type": file_extension,
        }
        # CSV 大文件走分块流式读取
        if file_extension == 'csv':
            params["chunksize"] = 5000

        _run_import(session_id, params, file.filename)

        return {"message": f"文件 {file.filename} 流式导入成功", "session_id": session_id}
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"流式文件导入失败: {str(e)}")


@router.post("/import-from-database")
async def import_from_database(
    session_id: str = Form(...),
    db_type: str = Form(...),
    host: str = Form(...),
    port: int = Form(...),
    database: str = Form(...),
    table: str = Form(...),
    username: str = Form(None),
    password: str = Form(None)
):
    """从数据库导入数据"""
    try:
        # 构造数据库连接字符串
        if username and password:
            connection_string = f"{db_type}://{username}:{password}@{host}:{port}/{database}"
        else:
            connection_string = f"{db_type}://{host}:{port}/{database}"

        _run_import(session_id, {
            "resource_path": table,
            "resource_type": db_type,
            "db_connection_string": connection_string,
            "query": f"SELECT * FROM {table}",
            "is_database": True,
        }, f"{database}.{table}")

        return {
            "session_id": session_id,
            "db_type": db_type,
            "host": host,
            "database": database,
            "table": table,
            "message": "数据库导入成功",
            "data": "数据导入成功"
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据库导入失败: {str(e)}")
