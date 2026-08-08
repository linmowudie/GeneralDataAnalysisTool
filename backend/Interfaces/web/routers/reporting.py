"""
backend/Interfaces/web/routers/reporting.py
/api/reporting/*：数据报表（generate / export / templates / save-config）

补齐前端 reportingService.ts 已调用的四个端点。
"""

import json
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from backend.Interfaces.controllers import session_controller
from backend.shared.types import StepName, DomainError
from backend.Interfaces.web.errors import to_http_error
from backend.Infrastructures.storage import report_store

logger = logging.getLogger(__name__)

router = APIRouter(tags=["数据报表"])

# 报告模板定义（与前端模板选择契约对应）
REPORT_TEMPLATES = [
    {"name": "full", "label": "完整报告", "description": "包含分析、可视化与结论的完整报告"},
    {"name": "summary", "label": "摘要报告", "description": "仅包含核心结论的摘要"},
    {"name": "technical", "label": "技术报告", "description": "侧重模型与参数细节的技术报告"},
    {"name": "executive", "label": "高管报告", "description": "面向管理层的简明报告"},
]


@router.post("/generate")
async def generate_report(
    session_id: str = Query(..., description="会话ID"),
    report_type: str = Query("full", description="报告类型")
):
    """生成数据报表"""
    try:
        artifact = session_controller.execute_step(session_id, StepName.REPORT, {
            "report_type": report_type,
        })
        return {
            "status": "success",
            "session_id": session_id,
            "report_id": artifact.report_id,
            "report_type": report_type,
            "message": "报告生成成功",
        }
    except HTTPException:
        raise
    except DomainError as e:
        raise to_http_error(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.get("/export/{report_id}")
async def export_report(
    report_id: str,
    format: str = Query("html", description="导出格式（html/pdf/excel，首版仅 html）")
):
    """导出报表文件"""
    try:
        content = report_store.load_report(report_id, fmt=format)
        if content is None:
            raise HTTPException(status_code=404, detail=f"报告 {report_id} 不存在")

        media_types = {
            "html": "text/html",
            "pdf": "application/pdf",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        media_type = media_types.get(format, "text/html")
        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={report_id}.{format}"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告导出失败: {str(e)}")


@router.get("/templates")
async def get_report_templates():
    """获取可用的报告模板"""
    return {"templates": REPORT_TEMPLATES}


@router.post("/save-config")
async def save_report_config(config: Dict[str, Any]):
    """保存报告配置"""
    try:
        config_path = report_store.base_dir / "_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return {
            "status": "success",
            "message": "报告配置保存成功",
            "config": config,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告配置保存失败: {str(e)}")
