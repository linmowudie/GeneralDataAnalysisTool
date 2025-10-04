from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api import data_import, data_analysis, data_visualization, data_preview, data_cleaning, model_extractor
from api.cleanup_task import cleanup_task

app = FastAPI(
    title="通用数据分析工具 API",
    description="为通用数据分析工具提供后端API服务",
    version="0.1.0"
)

# 启动定期清理任务
cleanup_task.start()

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
    return {"status": "healthy", "message": "数据分析工具API服务运行正常"}

@app.get("/api/")
async def root():
    """API根路径"""
    return {"message": "欢迎使用通用数据分析工具API", "version": "0.1.0"}

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    cleanup_task.stop()