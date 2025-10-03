from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import os
import sys

# 将项目根目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Src.DataAnalyzer.ModuleInterfaces import data_import

router = APIRouter()

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        # 保存上传的文件
        file_location = f"ScriptsOutput/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        # 检查文件名是否存在
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 使用现有的文件导入功能
        importer = data_import.DataImport(file_location, file.filename.split('.')[-1])
        imported_data = importer.import_data()
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "message": "文件上传成功",
            "data": "数据导入成功" if imported_data is not None else "数据导入失败"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件上传失败: {str(e)}")

@router.post("/import-from-database")
async def import_from_database(
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
        # 构造数据库连接字符串
        if username and password:
            connection_string = f"{db_type}://{username}:{password}@{host}:{port}/{database}"
        else:
            connection_string = f"{db_type}://{host}:{port}/{database}"
        
        # 使用现有的数据库导入功能
        importer = data_import.DataImport(table, db_type, connection_string, is_database=True)
        imported_data = importer.import_data(query=f"SELECT * FROM {table}")
        
        return {
            "db_type": db_type,
            "host": host,
            "database": database,
            "table": table,
            "message": "数据库导入成功",
            "data": "数据导入成功" if imported_data is not None else "数据导入失败"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据库导入失败: {str(e)}")