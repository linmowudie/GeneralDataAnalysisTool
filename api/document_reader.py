"""
文档读取模块
用于分离main.py中的文档读取功能
"""

import os
import markdown
from fastapi.responses import HTMLResponse
from typing import Optional


class DocumentReader:
    """文档读取器类"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        
    def read_project_docs(self) -> HTMLResponse:
        """读取项目文档"""
        # 读取API目录下的README.md
        api_readme_path = os.path.join(self.base_dir, "README.md")
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
                # 添加返回上级链接
                html_content += '<hr><p><a href="/api/docs/project">返回上级目录</a></p>'
                return HTMLResponse(content=self._generate_html("API文档", html_content))
        
        # 如果API目录下没有README.md，则尝试读取项目根目录下的README.md
        root_readme_path = os.path.join(os.path.dirname(self.base_dir), "README.md")
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
                # 添加返回上级链接
                html_content += '<hr><p><a href="/api/docs/project">返回上级目录</a></p>'
                return HTMLResponse(content=self._generate_html("项目文档", html_content))
        
        return HTMLResponse(content="<h1>文档未找到</h1><p>未找到项目文档文件。</p>")
    
    def read_technical_docs(self, file: Optional[str] = None) -> HTMLResponse:
        """读取技术文档"""
        # 如果请求特定文件
        if file:
            # 安全检查，确保文件在TechnicalDocuments目录下
            base_path = os.path.join(os.path.dirname(self.base_dir), "TechnicalDocuments")
            requested_path = os.path.normpath(os.path.join(base_path, file))
            
            # 确保请求的文件在base_path内，防止路径遍历攻击
            if not requested_path.startswith(base_path):
                return HTMLResponse(content="<h1>访问被拒绝</h1><p>您请求的文件不在允许的目录中。</p>")
            
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
                        # 添加返回上级链接
                        html_content += '<hr><p><a href="/api/docs/technical">返回上级目录</a></p>'
                        return HTMLResponse(content=self._generate_html("技术文档", html_content))
                else:
                    # 其他文件直接返回内容
                    with open(requested_path, "r", encoding="utf-8") as f:
                        return HTMLResponse(content=f.read())
            else:
                return HTMLResponse(content="<h1>文件未找到</h1><p>您请求的文件不存在。</p>")
        
        # 读取TechnicalDocuments目录下的API文档.md
        tech_docs_path = os.path.join(os.path.dirname(self.base_dir), "TechnicalDocuments", "API文档.md")
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
                return HTMLResponse(content=self._generate_html("技术文档", html_content))
        
        return HTMLResponse(content="<h1>文档未找到</h1><p>未找到技术文档文件。</p>")
    
    def _generate_html(self, title: str, content: str) -> str:
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