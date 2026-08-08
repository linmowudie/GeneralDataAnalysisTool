# CHANGELOG

## [0.4.1] - 2026-08-08

### 变更（Harness 评审发现修复）
- 修复 `start.ps1` 前端路径指向不存在的 `frontend\dashboard`，改为实际的 `frontend/`
- 修复 `pyproject.toml` console script 指向不存在的 `backend.Engine.core:main`，改为真实入口 `run_api:start_server`（并将 run_api 注册为可安装模块）
- 修复 `pyproject.toml` 中 `[tool.unimport]` exclude 列表字符串未闭合的 TOML 语法错误
- 接入已声明的 Python 质量工具：新增 `[tool.pytest.ini_options]`、`[tool.black]`、`.flake8` 配置；pytest 现可同时收录 `test_*.py` 与遗留 `*_test.py`（收录 161 项）；`tests/run_tests.py` 同步扩展 discover 模式
- 前端引入 vitest 行为级验证：新增 `npm run test`（vitest）与 `src/services/__tests__/apiService.test.ts` 冒烟测试（3 项）
- 迁移纳入版本控制：新实现快照提交与旧 `Src/`、`api/` 删除分阶段提交，建立可回滚检查点
- `.gitignore` 同步：修正 `frontend/dashboard/` 旧路径为 `frontend/`，新增忽略 ModelOutput/、ReportOutput/、TempStorage/、TestImages/、.qoder/ 等生成产物

### 已知事项
- 前端存量 lint 债务（76 处 `@typescript-eslint/no-explicit-any` 等）未在本次清理，lint 仍不通过；build 与新增测试均通过
- `test_data_visualization_upgrade.py::test_histogram_strategy` 全量运行时失败、单独运行通过，属既有测试隔离问题

## [0.4.0] - 2026-08-07

### 变更
- **彻底移除 `backend/Engine` 层**，功能按职责归位四层架构：
  - 功能部件（导入/预览/清洗/分析/可视化/报表）迁入 `backend/Services/components/`，由 `ManualWorkflow` / `AgentWorkflow` 调度，部件直调 Models 层
  - 可调用模型统一归入 `backend/Models/`：`cleaning`（CleanData/CleanDataMode）、`analysis`（DataAnalyzer/analyze_data + upgrade 分析器工厂体系）、`visualization`（DataVisualization 分发器 + Plots/InteractivePlots 插件 + upgrade 策略体系）、`reporting`（Report）
  - 基础设施归入 `backend/Infrastructures/`：`Configs`（配置唯一来源）、`logging`（日志落地）、`importers`（FileImporter / DbImporter / db_handlers 数据库处理器）
- 旧 `DataProcessingEngine` 引擎类删除，由 `backend.Services.ManualWorkflow` + `WorkflowContext` 取代；`main.py` 改为转发 `run_api.start_server`
- tests/ 与 Example/ 全量更新为新路径引用：重导入 `test_core_engine`（改测 ManualWorkflow）、`test_data_import`/`test_file_import`（改测 FileImporter/DbImporter）、`test_temp_storage`（改测会话级 TempStorage）；重写 4 个使用旧引擎的 Example 脚本

### 修复
- DbImporter 读取 sqlite 时未剥离 `sqlite:///` URL 前缀导致 "unable to open database file" 的问题
- matplotlib 兼容：`plt.cm.get_cmap` 已在 3.9 移除，轮廓系数图改用 `plt.colormaps`；测试哈希工具 `canvas.tostring_rgb()` 改用 `buffer_rgba()`
- 修复迁移前即已损坏的单元测试（旧 `Src.*` 引用、不存在的 mock 目标、模型别名 'lr'、HeatmapStrategy 参数名），回归 145 项全部通过
- AnalysisComponent 默认未返回训练集/预测集（`is_return_training_set`/`is_return_model_predicting_set` 默认 False），导致落盘的 analyzed 结果缺少特征数据、可视化始终返回空图表；服务层默认改为 True（调用方仍可显式覆盖）

### 兼容性
- Web API 契约不变，前端零改动；Python SDK 接口不变

## [0.3.0] - 2026-08-07

### 变更
- 旧版分析引擎 `Src/DataAnalyzer/` 整体迁入 `backend/Engine/`，`Src/` 目录已删除，全项目引用统一改为 `backend.Engine`
- 配置文件唯一来源迁至 `backend/Engine/Configs/`（model_config.json / model_mapping_config.json / database_config.json / model_visualization.json）
- `pyproject.toml` 打包范围与入口点同步改为 `backend.*` / `backend.Engine.core:main`
- 前端能力补全（方案第一阶段 P0）：
  - 新增 ErrorBoundary 错误边界、RouteGuard 路由守卫组件
  - 路由级懒加载（React.lazy + Suspense）+ Vite manualChunks 分包，主包从 1.2MB 降至 242KB
  - apiService 增强：ApiError 结构化错误、GET 自动重试、AbortSignal 取消、上传进度回调
  - Vite 配置补全：API proxy、`@/` 路径别名
- 前端模型参数改为后端 model-config 配置驱动的动态表单，移除硬编码默认参数

### 修复
- 前端会话未就绪时发起 session_id 为 null 的 API 请求问题
- Ant Design Table rowKey 弃用警告、React key 缺失警告
- `backend/Models/registry.py` 配置路径指向已删除的 Src/ 目录导致启动失败的问题

### 清理
- 前端：移除未使用的 App.css、data-import/styles/、空模块目录、冗余 getDefaultModelConfig()
- 全项目文档同步更新路径引用（TechnicalDocuments/、README.md、项目架构.txt）

## [0.2.0] - 2026-08-06

### 新增
- 后端重构为五层架构：Interfaces / Services / Cores / Models / Infrastructures，新代码位于 `backend/` 目录，依赖方向单向，`backend/shared` 为跨层契约层
- Agent 自动分析闭环：数据画像 → 方法推荐 → 逐候选执行 → 指标评估 → 择优决策，支持候选耗尽与超时熔断
- 新增 Agent 五端点：`/api/agent/data-profile`、`/api/agent/recommend-methods`、`/api/agent/evaluate`、`/api/agent/auto-analyze`、`/api/agent/decision`
- 补齐数据报表四端点（前端已有调用但后端此前缺失）：`/api/reporting/generate`、`/api/reporting/export/{report_id}`、`/api/reporting/templates`、`/api/reporting/save-config`
- Python SDK（`backend.Interfaces.sdk.DataAnalysisClient`）：不经 HTTP 直调控制器，不依赖 fastapi
- 会话并发隔离：每会话独立 asyncio.Lock；步骤锁状态由 StepStateMachine 唯一管理，消除双轨状态
- 回归测试：`tests/unit/test_backend_api_regression.py`（33 项全通过）、`tests/unit/test_backend_workflow.py`

### 修复
- `/api/model/*` 双重 prefix 导致实际路径为 `/api/model/api/model/*`、前端调用 404 的问题
- 步骤锁与引擎步骤状态双轨不一致问题（统一为 StepStateMachine）
- 会话无并发锁问题
- pandas 2.x 下 `drop(columns=..., axis=1)` 抛 ValueError（Src 三处：base_analyzer / association_rule_learning / dimensionality_reduction）

### 变更
- `run_api.py` 入口指向 `backend.Interfaces.web.app:app`；API 文档地址为 `/api/documentation`
- 临时数据布局调整为 `TempStorage/{session_id}/{stage}.pkl`，服务启动时全量清理
- 删除旧 `api/` 目录（功能已全部迁移至 `backend/Interfaces/web/routers`）
- 更新 `TechnicalDocuments/API文档.md`（新增端点、SDK 用法、架构目录）

### 兼容性
- 前端 API 契约完全兼容，前端零改动

## [0.1.0]

- 初始版本：基于 `api/` + `Src/DataAnalyzer`（现已迁入 `backend/Engine`）的数据分析工具后端
