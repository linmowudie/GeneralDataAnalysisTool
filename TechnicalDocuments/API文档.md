# 数据分析工具 API

为通用数据分析工具提供后端API服务。后端已重构为五层架构（Interfaces / Services / Cores / Models / Infrastructures），入口位于 `backend/Interfaces/web/app.py`。

## 目录结构

```
backend/
├── shared/                          # 跨层契约（类型/异常/常量）
├── Infrastructures/                 # 基础设施（存储/导入/序列化/配置/日志/LLM网关）
├── Models/                          # 模型层（注册表/工厂/封装 + 清洗/分析/可视化/报表模型）
├── Cores/                           # 核心层：Agent（画像/规划/评估）
├── Services/                        # 服务层：工作流编排 + 功能部件（手动流程/Agent闭环/上下文）
└── Interfaces/
    ├── controllers/                 # 控制器（Web 与 SDK 共用）
    ├── web/
    │   ├── app.py                   # FastAPI 应用入口
    │   ├── routers/                 # 11 个 router
    │   ├── schemas/                 # 请求/响应模型
    │   ├── errors.py                # 领域异常 -> HTTP 映射
    │   ├── utils.py / document_reader.py
    └── sdk/                         # Python SDK（不依赖 fastapi）
```

## 启动API服务

```bash
python run_api.py
```

或者使用uvicorn命令：

```bash
uvicorn backend.Interfaces.web.app:app --reload
```

## API文档

启动服务后，可以通过以下地址访问API文档：

- Swagger UI: http://127.0.0.1:8000/api/documentation
- ReDoc: http://127.0.0.1:8000/api/documentation/redoc

## 接口说明

### 会话管理
- `POST /api/session/create` - 创建新的会话
- `POST /api/session/reset-step` - 重置指定步骤及其后续步骤（级联重置）
- `POST /api/session/reset-all` - 重置会话中的所有数据
- `GET /api/session/step-status` - 获取步骤状态
- `POST /api/session/end` - 结束会话并清理资源

### 数据导入
- `POST /api/import/upload-file` - 上传文件
- `POST /api/import/streaming-upload-file` - 流式上传大文件（CSV 分块读取）
- `POST /api/import/import-from-database` - 从数据库导入数据

### 数据预览
- `GET /api/preview/data-preview` - 获取数据预览（无数据时回落示例数据）
- `GET /api/preview/dataset-info` - 获取数据集信息

### 数据分析
- `POST /api/analysis/run-analysis` - 运行数据分析
- `GET /api/analysis/available-models` - 获取可用分析模型
- `GET /api/analysis/model-config` - 获取模型配置信息
- `GET /api/analysis/data-columns/{session_id}` - 获取数据列信息（清洗后优先，回落导入数据）

### 数据可视化
- `POST /api/visualization/generate-chart` - 生成图表（无分析结果时回落示例数据）
- `GET /api/visualization/available-charts` - 获取可用图表类型

### 数据清洗
- `POST /api/cleaning/clean-data` - 清洗数据
- `GET /api/cleaning/cleaning-modes` - 获取可用的数据清洗模式

### 数据报表（新增）
- `POST /api/reporting/generate` - 生成报表（Query: session_id, report_type）
- `GET /api/reporting/export/{report_id}` - 导出报表文件（Query: format，首版支持 html）
- `GET /api/reporting/templates` - 获取报表模板（full/summary/technical/executive）
- `POST /api/reporting/save-config` - 保存报告配置（JSON body）

### Agent 自动分析（新增）
- `GET /api/agent/data-profile` - 数据画像（Query: session_id, target_col）
- `POST /api/agent/recommend-methods` - 推荐分析方法（按优先级排序）
- `POST /api/agent/evaluate` - 评估当前分析结果
- `POST /api/agent/auto-analyze` - 自动分析闭环（画像→推荐→逐候选执行→评估→择优；Query: session_id, max_candidates, target_col, timeout_sec）
- `GET /api/agent/decision` - 查询最近一次自动分析的决策结果

### 模型管理
- `POST /api/model/transfer` - 转移模型（修复了原双重 prefix 导致 404 的问题）
- `POST /api/model/manage` - 管理自动保存的模型
- `GET /api/model/list` - 列出自动保存的模型

### 清理任务
- `POST /api/cleanup/run` - 立即执行清理任务（全量清理临时存储）
- `POST /api/cleanup/run-step` - 立即执行指定步骤的清理任务（跨会话）
- `GET /api/cleanup/status` - 获取清理任务状态
- `GET /api/cleanup/stats` - 获取清理统计信息

### 步骤锁管理
- `POST /api/step/lock` - 锁定步骤
- `POST /api/step/unlock` - 解锁步骤
- `GET /api/step/status` - 获取步骤锁定状态
- `POST /api/step/lock-multiple` - 同时锁定多个步骤

### 健康检查和文档
- `GET /api/health` - 健康检查端点
- `GET /api/docs/project` - 项目文档
- `GET /api/docs/technical` - 技术文档

## SDK 使用（不依赖 fastapi）

```python
from backend.Interfaces.sdk import DataAnalysisClient

client = DataAnalysisClient()
sid = client.create_session()
client.import_file(sid, "Data/iris.csv")
client.clean(sid, mode="standard", target_col="target")
client.analyze(sid, "logisticregression", target_col="target")

# Agent 闭环
decision = client.auto_analyze(sid, target_col="target")
print(decision.best.model_type, decision.best.evaluation.score)
```

## CORS配置

当前API允许所有来源的跨域请求，在生产环境中应该限制具体的域名。

## 注意事项

1. 该API为数据分析工具的前端提供后端服务支持，前端接口契约与重构前完全一致
2. 所有接口都以`/api`为前缀
3. 会话并发隔离：每会话独立锁；步骤锁状态由 StepStateMachine 唯一管理
4. 临时数据布局：`TempStorage/{session_id}/{stage}.pkl`，服务启动时全量清理
5. 接口详细信息请参考 Swagger 文档（/api/documentation）
