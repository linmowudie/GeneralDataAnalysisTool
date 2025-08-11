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
from Src.data_analyzer.core import DataAnalyzer

# 创建数据分析器实例
analyzer = DataAnalyzer(data_source='Data/iris.csv')

# 执行数据分析
result = analyzer.run_analysis(model='kmeans', n_clusters=3)

# 可视化结果
figures = analyzer.visualize()
```

### Web API 服务

启动Web服务：
```bash
uvicorn main:app --reload
```

访问 `http://localhost:8000` 查看API文档。

### 更多示例

请查看 [examples/](examples/) 目录下的示例代码，了解如何使用各种功能。

## 项目结构

```
GeneralDataAnalysisTool/
├── Data/                 # 数据文件目录
├── Src/                  # 源代码目录
│   └── data_analyzer/    # 数据分析核心模块
│       ├── analysis/     # 分析算法模块
│       ├── cleaning/     # 数据清洗模块
│       ├── importer/     # 数据导入模块
│       └── visualization/ # 数据可视化模块
├── tests/                # 测试文件目录
├── examples/             # 使用示例目录
└── docs/                 # 文档目录
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
from Src.data_analyzer.core import DataAnalyzer

# 创建数据分析器实例
analyzer = DataAnalyzer(data_source='Data/iris.csv')

# 执行数据分析
result = analyzer.run_analysis(model='kmeans', n_clusters=3)

# 可视化结果
figures = analyzer.visualize()
```

### Web API 服务

启动Web服务：
```bash
uvicorn main:app --reload
```

访问 `http://localhost:8000` 查看API文档。

### 更多示例

请查看 [examples/](examples/) 目录下的示例代码，了解如何使用各种功能。

## 项目结构

```
GeneralDataAnalysisTool/
├── Data/                 # 数据文件目录
├── Src/                  # 源代码目录
│   └── data_analyzer/    # 数据分析核心模块
│       ├── analysis/     # 分析算法模块
│       ├── cleaning/     # 数据清洗模块
│       ├── importer/     # 数据导入模块
│       └── visualization/ # 数据可视化模块
├── tests/                # 测试文件目录
├── examples/             # 使用示例目录
└── docs/                 # 文档目录
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