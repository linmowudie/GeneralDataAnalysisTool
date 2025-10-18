# 数据分析工具 API

为通用数据分析工具提供后端API服务。

## 目录结构

```
api/
├── __init__.py
├── main.py              # API主入口
├── data_import.py       # 数据导入相关接口
├── data_preview.py      # 数据预览相关接口
├── data_analysis.py     # 数据分析相关接口
├── data_visualization.py # 数据可视化相关接口
├── data_cleaning.py     # 数据清洗相关接口
├── model_extractor.py   # 模型提取相关接口
├── session_manager.py   # 会话管理模块
├── cleanup_task.py      # 清理任务模块
├── document_reader.py   # 文档读取模块
├── step_lock.py         # 步骤锁管理模块
└── README.md            # API文档
```

## 启动API服务

```bash
python run_api.py
```

或者使用uvicorn命令：

```bash
uvicorn api.main:app --reload
```

## API文档

启动服务后，可以通过以下地址访问API文档：

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 接口说明

### 会话管理
- `POST /api/session/create` - 创建新的会话
- `POST /api/session/reset-step` - 重置指定步骤及其后续步骤
- `POST /api/session/reset-all` - 重置会话中的所有数据
- `GET /api/session/step-status` - 获取步骤状态
- `POST /api/session/end` - 结束会话并清理资源

### 数据导入
- `POST /api/import/upload-file` - 上传文件
- `POST /api/import/streaming-upload-file` - 流式上传大文件
- `POST /api/import/import-from-database` - 从数据库导入数据

### 数据预览
- `GET /api/preview/data-preview` - 获取数据预览
- `GET /api/preview/dataset-info` - 获取数据集信息

### 数据分析
- `POST /api/analysis/run-analysis` - 运行数据分析
- `GET /api/analysis/available-models` - 获取可用分析模型

### 数据可视化
- `POST /api/visualization/generate-chart` - 生成图表
- `GET /api/visualization/available-charts` - 获取可用图表类型

### 数据清洗
- `POST /api/cleaning/clean-data` - 清洗数据
- `GET /api/cleaning/cleaning-modes` - 获取可用的数据清洗模式

### 模型管理
- `POST /api/model/transfer` - 转移模型
- `POST /api/model/manage` - 管理自动保存的模型
- `GET /api/model/list` - 列出自动保存的模型

### 清理任务
- `POST /api/cleanup/run` - 立即执行清理任务
- `POST /api/cleanup/run-step` - 立即执行指定步骤的清理任务
- `GET /api/cleanup/status` - 获取清理任务状态
- `GET /api/cleanup/stats` - 获取清理统计信息

### 步骤锁管理
- `POST /lock-step` - 锁定步骤
- `POST /unlock-step` - 解锁步骤
- `GET /step-status` - 获取步骤锁定状态

### 健康检查和文档
- `GET /api/health` - 健康检查端点
- `GET /api/docs/project` - 项目文档
- `GET /api/docs/technical` - 技术文档

## CORS配置

当前API允许所有来源的跨域请求，在生产环境中应该限制具体的域名。

## 注意事项

1. 该API为数据分析工具的前端提供后端服务支持
2. 所有接口都以`/api`为前缀
3. 接口详细信息请参考API文档