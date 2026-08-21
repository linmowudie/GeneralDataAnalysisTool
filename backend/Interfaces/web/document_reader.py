"""
backend/Interfaces/web/document_reader.py
文档读取器（/api/docs/* 端点使用，逻辑迁移自原 api/document_reader.py）
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import markdown
from fastapi.responses import HTMLResponse

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


class DocumentReader:
    """文档读取器（以项目根目录为基准）"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root or str(_PROJECT_ROOT)

    def read_project_docs(self) -> HTMLResponse:
        """读取项目文档（根目录 README.md）"""
        readme_path = os.path.join(self.project_root, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
            html_content = html_content.replace(
                'href="', 'href="/api/docs/project?file='
            ).replace(
                'src="', 'src="/api/docs/project?file='
            )
            html_content += '<hr><p><a href="/api/docs/project">返回上级目录</a></p>'
            return HTMLResponse(content=self._generate_html("项目文档", html_content))
        return HTMLResponse(content="<h1>文档未找到</h1><p>未找到项目文档文件。</p>")

    def read_technical_docs(self, file: Optional[str] = None) -> HTMLResponse:
        """读取技术文档（TechnicalDocuments 目录）"""
        if file:
            base_path = os.path.join(self.project_root, "TechnicalDocuments")
            requested_path = os.path.normpath(os.path.join(base_path, file))

            # 防止路径遍历攻击
            if not requested_path.startswith(base_path):
                return HTMLResponse(content="<h1>访问被拒绝</h1><p>您请求的文件不在允许的目录中。</p>")

            if os.path.exists(requested_path) and os.path.isfile(requested_path):
                if requested_path.endswith('.md'):
                    with open(requested_path, "r", encoding="utf-8") as f:
                        md_content = f.read()
                    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
                    html_content = html_content.replace(
                        'href="ModuleInterfaces/', 'href="/api/docs/technical?file=ModuleInterfaces/'
                    ).replace(
                        'src="', 'src="/api/docs/technical?file='
                    )
                    html_content += '<hr><p><a href="/api/docs/technical">返回上级目录</a></p>'
                    return HTMLResponse(content=self._generate_html("技术文档", html_content))
                else:
                    with open(requested_path, "r", encoding="utf-8") as f:
                        return HTMLResponse(content=f.read())
            else:
                return HTMLResponse(content="<h1>文件未找到</h1><p>您请求的文件不存在。</p>")

        tech_docs_path = os.path.join(self.project_root, "TechnicalDocuments", "API文档.md")
        if os.path.exists(tech_docs_path):
            with open(tech_docs_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
            html_content = html_content.replace(
                'href="ModuleInterfaces/', 'href="/api/docs/technical?file=ModuleInterfaces/'
            ).replace(
                'src="', 'src="/api/docs/technical?file='
            )
            return HTMLResponse(content=self._generate_html("技术文档", html_content))

        return HTMLResponse(content="<h1>文档未找到</h1><p>未找到技术文档文件。</p>")

    @staticmethod
    def _generate_html(title: str, content: str) -> str:
        """生成HTML页面"""
        return f"""
        <html>
            <head>
                <title>{title}</title>
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
                {content}
            </body>
        </html>
        """
