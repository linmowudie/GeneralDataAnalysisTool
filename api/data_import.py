from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import os
import sys
import logging
import shutil
from pathlib import Path

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .session_manager import session_manager

# 配置API日志
from Src.DataAnalyzer.Configs.log_setting import get_component_logger
api_logger = get_component_logger('api', 'data_import')

# 定义API输出目录
API_OUTPUT_DIR = Path("APIOutput")
API_OUTPUT_DIR.mkdir(exist_ok=True)

router = APIRouter()

@router.post("/create-session")
async def create_session():
    """创建新的会话"""
    try:
        api_logger.info("创建新的会话")
        session_id = session_manager.create_session()
        api_logger.info(f"会话创建成功: {session_id}")
        return {
            "session_id": session_id,
            "message": "会话创建成功"
        }
    except Exception as e:
        api_logger.error(f"会话创建失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话创建失败: {str(e)}")

@router.post("/upload-file")
async def upload_file(
    session_id: str = Form(...), 
    file: UploadFile = File(...)
    ):
    """上传并导入文件"""
    try:
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 保存上传的文件
        if file.filename:
            file_path = API_OUTPUT_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 记录导入的文件名
            engine._last_imported_file = file.filename
            
            # 导入数据
            engine.import_data(
                resource_path=str(file_path),
                resource_type=file.filename.split('.')[-1] if file.filename else 'csv'
            )
            
            return {"message": f"文件 {file.filename} 上传并导入成功", "session_id": session_id}
        else:
            raise ValueError("文件名为空")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件上传失败: {str(e)}")

@router.post("/import-from-database")
async def import_from_database(
    session_id: str = Form(...),
    db_type: str = Form(...),
    host: str = Form(...),
    port: int = Form(...),
    database: str = Form(...),
    table: str = Form(...),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    """从数据库导入数据"""
    try:
        api_logger.info(f"从数据库导入数据: {db_type}://{host}:{port}/{database}.{table}")
        # 构造数据库连接字符串
        if username and password:
            connection_string = f"{db_type}://{username}:{password}@{host}:{port}/{database}"
        else:
            connection_string = f"{db_type}://{host}:{port}/{database}"
        
        # 获取会话对应的引擎实例
        engine = session_manager.get_engine(session_id)
        
        # 记录导入的表名
        engine._last_imported_file = f"{database}.{table}"
        
        # 使用核心引擎从数据库导入数据
        engine.import_data(
            resource_path=table,
            resource_type=db_type,
            db_connection_string=connection_string,
            query=f"SELECT * FROM {table}",
            is_database=True
        )
        api_logger.info("数据库导入成功")
        
        return {
            "session_id": session_id,
            "db_type": db_type,
            "host": host,
            "database": database,
            "table": table,
            "message": "数据库导入成功",
            "data": "数据导入成功"
        }
    except ValueError as e:
        api_logger.error(f"会话错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话错误: {str(e)}")
    except Exception as e:
        api_logger.error(f"数据库导入失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"数据库导入失败: {str(e)}")

@router.post("/end-session")
async def end_session(
    session_id: str = Form(...)
    ):
    """结束会话并清理资源"""
    try:
        api_logger.info(f"结束会话: {session_id}")
        success = session_manager.delete_session(session_id)
        if success:
            api_logger.info(f"会话结束成功: {session_id}")
            return {
                "session_id": session_id,
                "message": "会话结束成功"
            }
        else:
            api_logger.warning(f"会话ID不存在: {session_id}")
            raise HTTPException(status_code=400, detail=f"会话ID {session_id} 不存在")
    except Exception as e:
        api_logger.error(f"会话结束失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"会话结束失败: {str(e)}")