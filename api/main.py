from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional
import os
import sys
import logging

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.document_reader import DocumentReader

from api import data_import, data_analysis, data_visualization, data_preview, data_cleaning, model_extractor
from api.cleanup_task import cleanup_task

# 配置API日志
from Src.DataAnalyzer.Configs.log_setting import get_component_logger
api_logger = get_component_logger('api', 'api_main')

# 在启动时清理临时数据
cleanup_task.cleanup_temp_directories()

doc_reader = DocumentReader(os.path.dirname(__file__))

app = FastAPI(
    title="通用数据分析工具 API",
    description="为通用数据分析工具提供后端API服务",
    version="0.1.0"
)

# 启动定期清理任务
cleanup_task.start()
api_logger.info("定期清理任务已启动")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(data_import.router, prefix="/api/import", tags=["数据导入"])
app.include_router(data_preview.router, prefix="/api/preview", tags=["数据预览"])
app.include_router(data_analysis.router, prefix="/api/analysis", tags=["数据分析"])
app.include_router(data_visualization.router, prefix="/api/visualization", tags=["数据可视化"])
app.include_router(data_cleaning.router, prefix="/api/cleaning", tags=["数据清洗"])
app.include_router(model_extractor.router, prefix="/api/model", tags=["模型管理"])

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    api_logger.info("健康检查请求")
    return {"status": "healthy", "message": "数据分析工具API服务运行正常"}

@app.get("/api/")
async def root():
    """API根路径"""
    api_logger.info("API根路径访问")
    return {"message": "欢迎使用通用数据分析工具API", "version": "0.1.0"}

@app.get("/api/docs/project", response_class=HTMLResponse, tags=["文档"])
async def project_docs():
    """项目文档"""
    api_logger.info("访问项目文档")
    return doc_reader.read_project_docs()

@app.get("/api/docs/technical", response_class=HTMLResponse, tags=["文档"])
async def technical_docs(file: Optional[str] = None):
    """技术文档"""
    api_logger.info(f"访问技术文档: {file}")
    return doc_reader.read_technical_docs(file)

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    api_logger.info("API服务启动")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    api_logger.info("API服务关闭")
    cleanup_task.stop()