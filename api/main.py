from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import sys
import markdown

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

@app.get("/api/docs/project", response_class=HTMLResponse, tags=["文档"])
async def project_docs():
    """项目文档"""
    # 读取API目录下的README.md
    api_readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(api_readme_path):
        with open(api_readme_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
            # 修复相对链接
            html_content = html_content.replace(
                'href="', 
                'href="/api/docs/project?file='
            ).replace(
                'src="', 
                'src="/api/docs/project?file='
            )
            return f"""
            <html>
                <head>
                    <title>API文档</title>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                        h1, h2, h3 {{ color: #333; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
            </html>
            """
    
    # 如果API目录下没有README.md，则尝试读取项目根目录下的README.md
    root_readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
    if os.path.exists(root_readme_path):
        with open(root_readme_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
            # 修复相对链接
            html_content = html_content.replace(
                'href="', 
                'href="/api/docs/project?file='
            ).replace(
                'src="', 
                'src="/api/docs/project?file='
            )
            return f"""
            <html>
                <head>
                    <title>项目文档</title>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                        h1, h2, h3 {{ color: #333; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
            </html>
            """
    
    return "<h1>文档未找到</h1><p>未找到项目文档文件。</p>"

@app.get("/api/docs/technical", response_class=HTMLResponse, tags=["文档"])
async def technical_docs(file: str = None):
    """技术文档"""
    # 如果请求特定文件
    if file:
        # 安全检查，确保文件在TechnicalDocuments目录下
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "TechnicalDocuments")
        requested_path = os.path.normpath(os.path.join(base_path, file))
        
        # 确保请求的文件在base_path内，防止路径遍历攻击
        if not requested_path.startswith(base_path):
            return "<h1>访问被拒绝</h1><p>您请求的文件不在允许的目录中。</p>"
        
        if os.path.exists(requested_path) and os.path.isfile(requested_path):
            # 如果是Markdown文件，转换为HTML
            if requested_path.endswith('.md'):
                with open(requested_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
                    # 修复相对链接
                    html_content = html_content.replace(
                        'href="ModuleInterfaces/', 
                        'href="/api/docs/technical?file=ModuleInterfaces/'
                    ).replace(
                        'src="', 
                        'src="/api/docs/technical?file='
                    )
                    return f"""
                    <html>
                        <head>
                            <title>技术文档</title>
                            <meta charset="utf-8">
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                                h1, h2, h3 {{ color: #333; }}
                                table {{ border-collapse: collapse; width: 100%; }}
                                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                th {{ background-color: #f2f2f2; }}
                            </style>
                        </head>
                        <body>
                            {html_content}
                        </body>
                    </html>
                    """
            else:
                # 其他文件直接返回内容
                with open(requested_path, "r", encoding="utf-8") as f:
                    return f.read()
        else:
            return "<h1>文件未找到</h1><p>您请求的文件不存在。</p>"
    
    # 读取TechnicalDocuments目录下的API文档.md
    tech_docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "TechnicalDocuments", "API文档.md")
    if os.path.exists(tech_docs_path):
        with open(tech_docs_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
            # 修复相对链接
            html_content = html_content.replace(
                'href="ModuleInterfaces/', 
                'href="/api/docs/technical?file=ModuleInterfaces/'
            ).replace(
                'src="', 
                'src="/api/docs/technical?file='
            )
            return f"""
            <html>
                <head>
                    <title>技术文档</title>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                        h1, h2, h3 {{ color: #333; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
            </html>
            """
    
    return "<h1>文档未找到</h1><p>未找到技术文档文件。</p>"

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    cleanup_task.stop()