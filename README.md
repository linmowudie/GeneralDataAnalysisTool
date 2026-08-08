# 通用数据分析工具 (General Data Analysis Tool)

一个功能强大的数据分析和可视化工具包，支持多种机器学习算法和数据处理功能。

## 功能特性

### 数据处理
- 数据清洗和预处理
- 多种数据源导入（CSV, Excel, JSON, 数据库等）
- 数据类型自动识别和转换

### 机器学习算法支持
- 线性回归 (Linear Regression)
- 逻辑回归 (Logistic Regression)
- KMeans 聚类 (KMeans Clustering)
- 决策树分类 (Decision Tree Classifier)
- K近邻分类 (K-Nearest Neighbors)
- PCA 降维 (Principal Component Analysis)
- Mean Shift 聚类
- 标准化处理 (Standard Scaler)

### 数据可视化
- 自动生成各类模型的可视化图表
- 支持散点图、折线图、柱状图等多种图表类型
- 可自定义图表样式和标签
- 高质量图像输出（PNG, SVG等格式）
- **交互式可视化支持**（新增）
  - 基于Plotly的交互式图表
  - 3D可视化功能
  - 支持缩放、旋转、悬停等交互操作

### 模型管理
- 自动保存训练完成的模型
- 模型版本管理
- 模型转移功能（从自动保存目录到用户提取目录）
- 自动清理过期模型文件，防止存储空间占用过多

### 会话和步骤管理
- 用户会话状态跟踪和管理
- 步骤完成状态自动标记
- 参数锁定机制防止误操作
- 灵活的步骤重置功能

### 系统特性
- 模块化设计，易于扩展
- 完整的测试覆盖
- 详细的日志记录
- 清晰的错误处理机制
- 支持Web API接口（基于FastAPI）

## 安装指南

### 环境要求
- Python 3.12 或更高版本
- 支持 uv 包管理器

### 安装步骤

1. 克隆项目代码：
```bash
git clone <项目地址>
cd GeneralDataAnalysisTool
```

2. 使用 uv 安装依赖：
```bash
uv sync
```

3. 或者使用 pip 安装依赖：
```bash
pip install -r requirements.txt
```

## 主要依赖

- **数据处理**: pandas, numpy, pyarrow
- **机器学习**: scikit-learn, scipy, statsmodels
- **可视化**: matplotlib, seaborn, plotly
- **Web框架**: fastapi, uvicorn
- **数据导入/导出**: openpyxl, requests
- **日志系统**: loguru
- **网页抓取**: scrapy, selenium

## 使用示例

### 基本用法

```python
from backend.Services import ManualWorkflow
from backend.Services.workflows.context import WorkflowContext
from backend.shared.types import StepName

# 创建工作流与会话上下文
workflow = ManualWorkflow()
context = WorkflowContext("my_session")

# 导入数据
workflow.execute_step(context, StepName.IMPORT, {
    "resource_path": "Data/iris.csv", "resource_type": "csv"
})

# 清洗数据（标准模式）
workflow.execute_step(context, StepName.CLEANING, {
    "select_mode": "standard", "params_list": []
})

# 清洗数据（自定义模式）
# params = [
#     "handle_missing='fill'",
#     "fill_method='median'",
#     "outlier_method='iqr'"
# ]
# workflow.execute_step(context, StepName.CLEANING, {
#     "select_mode": "custom", "params_list": params
# })

# 分析数据
result = workflow.execute_step(context, StepName.ANALYSIS, {
    "model_type": "kmeans", "target_col": "target"
})

# 可视化结果
workflow.execute_step(context, StepName.VISUALIZATION, {})

# 生成报告
workflow.execute_step(context, StepName.REPORT, {})

# 查看步骤状态
status = context.steps.status()
print(f"已完成步骤: {status['completed_steps']}")
print(f"已锁定步骤: {status['locked_steps']}")

# 重置分析步骤及其后续步骤
context.reset_step(StepName.ANALYSIS)
```

### 脚本工具使用

项目包含多个实用脚本，可以直接从命令行使用：

#### 数据转换脚本
```bash
# 单文件转换
python PythonScripts/data_converter.py Data/iris.csv -o iris.json -f json

# 批量转换
python PythonScripts/batch_converter.py Data ScriptsOutput/Batch -f csv json xlsx

# 模型管理
python PythonScripts/model_extractor.py --transfer          # 转移最新的自动保存模型
python PythonScripts/model_extractor.py --transfer model_name.pkl  # 转移指定模型
python PythonScripts/model_extractor.py --manage           # 管理自动保存的模型数量
```

### Web API 服务

启动Web服务：
```bash
python run_api.py
```

访问 `http://localhost:8000/api/documentation` 查看API文档。

API提供了以下模型管理端点：
- `POST /api/model/transfer` - 转移模型
- `POST /api/model/manage` - 管理自动保存的模型
- `GET /api/model/list` - 列出自动保存的模型
- `GET /api/model/auto-save-count` - 获取自动保存模型数量

API还提供了以下会话管理端点：
- `POST /api/import/create-session` - 创建新会话
- `POST /api/import/reset-step` - 重置指定步骤
- `GET /api/import/step-status` - 获取步骤状态
- `POST /api/import/end-session` - 结束会话

### 更多示例

请查看 [Example/](Example/) 目录下的示例代码，了解如何使用各种功能：
- [core_example.py](Example/core_example.py) - 工作流完整流程示例
- [comprehensive_dataset_analysis.py](Example/comprehensive_dataset_analysis.py) - 综合数据集分析示例
- [mongodb_data_analysis_example.py](Example/mongodb_data_analysis_example.py) - MongoDB数据分析示例
- [interactive_visualization_example.py](Example/interactive_visualization_example.py) - 交互式可视化示例
- [database_import_example.py](Example/database_import_example.py) - 数据库导入示例

## 项目结构

```
GeneralDataAnalysisTool/
├── Data/                 # 数据文件目录
├── backend/              # 后端（四层架构 + 契约层）
│   ├── Interfaces/       # 接口层：Web API（FastAPI）、控制器、SDK
│   ├── Services/         # 服务层：工作流编排 + 功能部件（导入/清洗/分析/可视化/报表）
│   ├── Cores/            # 核心层：Agent（数据画像、规划器、决策器）
│   ├── Models/           # 模型层：机器学习/清洗/可视化/报表等可调用模型
│   ├── Infrastructures/  # 基础设施层：配置、存储、导入器、日志
│   └── shared/           # 跨层契约层
├── frontend/             # 前端（React + TypeScript + Vite + Ant Design）
├── tests/                # 测试文件目录
├── Example/              # 使用示例目录
├── PythonScripts/        # 实用脚本目录
├── ModelOutput/          # 模型输出目录
│   ├── 自动保存/          # 自动保存的模型
│   └── 用户提取/          # 用户手动提取的模型
└── TechnicalDocuments/   # 文档目录
```

## 测试

运行所有测试：
```bash
python -m pytest tests/
```

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请联系：1711406673@qq.com

## 致谢

- 感谢所有开源项目的贡献者
- 特别感谢 scikit-learn、pandas、numpy 和 matplotlib 等优秀库