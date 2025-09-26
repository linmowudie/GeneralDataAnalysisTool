# Reporting 报告生成模块接口文档

## 概述

`Reporting` 模块负责生成数据分析报告，包括结果汇总、图表展示和分析结论等内容。该模块接收模型参数、得分、可视化结果和预测结果等数据，生成结构化的报告。

## 类：Report

### 构造函数

```python
Report(
    model_params: Optional[Dict] = None,
    model_scores: Optional[Dict] = None,
    visualizations: Optional[Dict] = None,
    model_predictions: Optional[pd.Series] = None
)
```

**参数说明：**
- `model_params` (Optional[Dict]): 模型参数
- `model_scores` (Optional[Dict]): 模型得分
- `visualizations` (Optional[Dict]): 可视化结果
- `model_predictions` (Optional[pd.Series]): 模型预测结果

### 方法

#### return_report()

返回报告内容。

```python
return_report() -> Dict
```

**返回值：**
- `Dict`: 包含报告内容的字典，仅包含非空的字段

### 使用示例

#### 基本使用

```python
from Src.DataAnalyzer.reporting import Report
import pandas as pd

# 创建报告数据
model_params = {
    "model": "LogisticRegression",
    "C": 1.0,
    "max_iter": 1000
}

model_scores = {
    "accuracy": 0.95,
    "precision": 0.93,
    "recall": 0.92
}

# 创建报告实例
report = Report(
    model_params=model_params,
    model_scores=model_scores
)

# 生成报告
report_content = report.return_report()
print(report_content)
```

#### 包含可视化结果的报告

```python
from Src.DataAnalyzer.reporting import Report
import pandas as pd
import matplotlib.pyplot as plt

# 创建示例可视化图表
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
ax.set_title("示例图表")

# 创建报告数据
visualizations = {
    "example_plot": fig
}

model_predictions = pd.Series([0, 1, 1, 0, 1])

# 创建报告实例
report = Report(
    visualizations=visualizations,
    model_predictions=model_predictions
)

# 生成报告
report_content = report.return_report()
print(report_content)
```

#### 在核心引擎中使用

```python
from Src.DataAnalyzer.core import DataProcessingEngine

# 创建引擎实例
engine = DataProcessingEngine()

# 执行数据分析流程
engine.import_data("data.csv", "csv")
engine.clean_data("standard", [])
engine.analyze_data(
    model="LogisticRegression",
    target_col="target"
)
engine.visualize_data()
engine.generate_report()

# 获取报告
report = engine.get_report()
if report:
    print("报告内容:")
    for key, value in report.items():
        print(f"- {key}: {type(value)}")
```

### 报告结构

生成的报告是一个字典，包含以下可能的键：

- `model_params`: 模型参数信息
- `model_scores`: 模型评估得分
- `visualizations`: 可视化图表
- `model_predictions`: 模型预测结果

只有在构造函数中提供了相应参数的字段才会出现在最终报告中。