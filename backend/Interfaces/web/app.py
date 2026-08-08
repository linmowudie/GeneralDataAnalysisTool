"""
backend/Interfaces/web/app.py
FastAPI 应用入口：实例 / CORS / 路由注册 / 启动清理钩子 / 健康检查 / 文档端点

路由 prefix 与原 api/main.py 完全一致，前端零改动；
新增 /api/reporting 与 /api/agent 两组端点。
"""

from __future__ import annotations

import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import HTMLResponse, RedirectResponse  # noqa: E402

from backend.Interfaces.web import document_reader, schemas  # noqa: E402,F401
from backend.Interfaces.web.document_reader import DocumentReader  # noqa: E402
from backend.Interfaces.web.routers import (  # noqa: E402
    session, data_import, preview, cleaning, analysis,
    visualization, model, step, cleanup, reporting, agent,
)
from backend.Infrastructures.storage import temp_storage  # noqa: E402

logger = logging.getLogger(__name__)

doc_reader = DocumentReader()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时清理临时数据（与原 api 启动行为一致）"""
    stats = temp_storage.clear_all()
    logger.info("API服务启动，启动清理完成: %s", stats)
    yield
    logger.info("API服务关闭")


app = FastAPI(
    title="通用数据分析工具 API",
    description="为通用数据分析工具提供后端API服务",
    version="0.2.0",
    docs_url="/api/documentation",       # 与原契约一致
    redoc_url="/api/documentation/redoc",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（prefix 与原 api/main.py 完全一致）
app.include_router(data_import.router, prefix="/api/import", tags=["数据导入"])
app.include_router(preview.router, prefix="/api/preview", tags=["数据预览"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["数据分析"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["数据可视化"])
app.include_router(cleaning.router, prefix="/api/cleaning", tags=["数据清洗"])
app.include_router(model.router, prefix="/api/model", tags=["模型管理"])
app.include_router(step.router, tags=["步骤锁管理"])  # 绝对路径注册 /api/step/*
app.include_router(cleanup.router, prefix="/api/cleanup", tags=["清理任务"])
app.include_router(session.router, prefix="/api/session", tags=["会话管理"])
# 新增端点（设计文档要求补齐）
app.include_router(reporting.router, prefix="/api/reporting", tags=["数据报表"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent 自动分析"])


@app.get("/api/health", response_model=schemas.HealthResponse)
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "数据分析工具API服务运行正常"}


@app.get("/api/")
async def root():
    """API根路径"""
    return {"message": "欢迎使用通用数据分析工具API", "version": "0.2.0"}


@app.get("/api/docs/project", response_class=HTMLResponse, tags=["文档"])
async def project_docs():
    """项目文档"""
    return doc_reader.read_project_docs()


@app.get("/api/docs/technical", response_class=HTMLResponse, tags=["文档"])
async def technical_docs(file: Optional[str] = None):
    """技术文档"""
    return doc_reader.read_technical_docs(file)


@app.get("/", response_class=RedirectResponse, tags=["根路径"])
async def root_redirect():
    """根路径重定向到技术文档"""
    return "/api/docs/technical"
