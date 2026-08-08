import uvicorn
import os
import sys

# 将当前目录添加到Python路径中
sys.path.append(os.path.dirname(__file__))

from backend.Interfaces.web.app import app

def start_server(host="127.0.0.1", port=8000):
    """启动FastAPI服务器"""
    print(f"正在启动服务器 http://{host}:{port}")
    print(f"API文档地址: http://{host}:{port}/api/documentation")
    uvicorn.run("run_api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start_server()

# 为了 uvicorn 命令行运行时能导入 app
app = app
