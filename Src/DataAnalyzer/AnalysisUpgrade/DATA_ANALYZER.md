# 数据分析模块2.0版本文档

## 模块功能描述

本模块提供自动化数据分析能力，支持多种学习类型与模型组合，能够完成数据划分、特征编码、模型训练、评估打分等全流程操作。

返回结果可用于前端展示及下游可视化模块升级版的参数输入，具备良好的扩展性与模块化设计。

核心设计采用 工厂模式 + 策略模式，通过 DataAnalysisUpgrade 公共接口统一入口，动态调度具体实现模块。

## 公共接口：DataAnalysisUpgrade

### 位置

`Src/DataAnalyzer/ModuleInterfaces/data_analysis_upgrade_interface.py`

### 描述

该接口为数据分析模块的统一入口，负责接收外部调用参数，并执行基础空值校验（Null Check）。校验通过后，调用 analyze 方法触发下级分析流程。

🔍 注："空值校验"指检查必填参数是否为 None 或空容器（如空 DataFrame、空列表），并记录日志。若发现关键参数缺失，将记录 ERROR 级别日志并抛出异常，阻止后续执行。

## 配置文件说明

### model_analysis.json

该配置文件位于 `Src/DataAnalyzer/Configs/model_analysis.json`，是数据分析模块的核心配置文件，定义了支持的模型、参数结构和评估方法。

主要包含以下配置项：
- `support_ML_models`: 支持的机器学习模型列表
- `ML_model_special_params`: 各模型的超参数配置，按任务类型组织
- `ML_model_evaluation_methods`: 各任务类型的评估指标定义和说明
- `preprocessing_methods`: 支持的预处理方法列表
- `preprocessing_special_params`: 各预处理方法的参数配置

该配置文件被工厂类和策略类用于动态创建和配置模型实例，确保系统具有良好的扩展性和维护性。

## 输入参数

| 参数名 | 参数类型 | 是否必填 | 可为空 | 默认值 | 参数描述 |
| ------ | -------- | -------- | ------ | ------ | -------- |
| df | pd.DataFrame | 是 | 否 | - | 输入数据集，不能为空 |
| learn_type | str | 是 | 否 | - | 学习类型，如 "ML"（机器学习）或 "DL"（深度学习） |
| model_type | str | 是 | 否 | - | 模型类别，如 "classification"、"regression"、"clustering" |
| model | str | 是 | 否 | - | 模型名称，如 "random_forest"、"xgboost" |
| random_state | int | 否 | 是 | 42 | 随机种子，用于复现实验结果 |
| is_split | bool | 否 | 是 | True | 是否自动划分训练/测试集 |
| split_ratio | float | 否 | 是 | 0.2 | 测试集占比，范围 (0,1)，仅当 is_split=True 时生效 |
| feature_cols | list[str] | 是 | 否 | - | 特征列名列表，不能为空 |
| target_col | str | 是 | 否 | - | 目标列名，不能为空 |
| metrics_list | list[str] | 否 | 是 | []（使用默认指标） | 评价指标列表，如 ["accuracy", "f1"] |
| is_return_model_score | bool | 否 | 是 | True | 是否返回模型评估得分 |
| feature_cols_encoding | str | 否 | 是 | "auto" | 特征列编码方式，支持 "onehot"、"label"、"ordinal"、"target"、"none" 等 |
| target_col_encoding | str | 否 | 是 | "auto" | 目标列编码方式，分类任务常用 "label"，回归为 "none" |
| test_set | pd.DataFrame | 否 | 是 | None | 外部传入的测试集，仅当 is_split=False 时使用 |
| model_params | dict | 否 | 是 | {} | 模型特定超参数，如 {"n_estimators": 100, "max_depth": 10} |

📌 参数依赖说明：

1. 若 is_split=False，则 test_set 必须提供且非空。
2. split_ratio 仅在 is_split=True 时生效。

## 返回参数

| 参数 | 类型 | 说明 |
| ---- | ---- | ---- |
| model | object | 训练完成的模型对象，可用于预测或持久化 |
| model_score | dict \| list[dict] | 模型评估得分，格式为 {"metric_name": score_value}；若含多阶段评估（如验证集+测试集），返回 list |
| train_set | pd.DataFrame | 实际用于训练的特征-标签数据集 |
| test_set | pd.DataFrame | 实际用于测试的数据集（可能由系统划分或外部传入） |
| feature_cols | list[str] | 经过预处理（如降维、筛选）后的最终特征列名 |
| encoding_method | dict | 编码方式记录，格式：{"features": "onehot", "target": "label"}，供下游模块核对 |

✅ 拼写修正：原 ecoding_method 已更正为 encoding_method

## 参数校验机制

本模块在调用 analyze 方法前，执行基础空值校验，确保关键参数有效。具体规则如下：

### 校验逻辑

对标记为"必填"的参数进行非空判断：
- None 值 → 判定为空
- 容器类型（list, dict, DataFrame）→ 使用 len() 或 .empty 判断是否为空
- 不进行类型校验或值域校验（由下游模块负责）

### 日志输出规范

| 情况 | 日志级别 | 示例消息 |
| ---- | -------- | -------- |
| 必填参数为空 | ERROR | "Required parameter 'df' is None or empty." |
| 可选参数为空 | INFO | "Optional parameter 'test_set' not provided, using split strategy." |
| 校验通过 | INFO | "All required parameters validated successfully." |

## 三层架构设计

数据分析模块2.0版本采用了清晰的三层架构设计，包括接口层、工厂层和策略层：

### 接口层 (Interface Layer)
- 由 `DataAnalysisUpgrade` 类实现
- 负责接收用户请求和参数
- 执行参数验证和预处理
- 调用工厂层创建分析器实例

### 工厂层 (Factory Layer)
- 由 `AnalyzerFactory` 及其子工厂类实现
- 实现两级路由机制：
  - 第一级：根据 `learn_type` 选择工厂（ML或DL）
  - 第二级：根据 `model_type` 选择任务类型工厂
- 负责创建具体的分析器实例

### 策略层 (Strategy Layer)
- 由 `AnalysisStrategy` 基类及其子类实现
- 控制分析流程的执行顺序和逻辑
- 根据任务类型选择对应的策略实现
- 处理任务特定的执行逻辑

## 基类 `base_analyzer.BaseAnalyzer`
  
💡所有`Analyzer`类除`DataAnalysisUpgrade`都必须继承自此基类。

### 供子类共用的方法

| 方法名 | 描述 |
| ---- | ---- |
| feature_set_encoding | 特征集编码方法，支持 "onehot"、"label"、"ordinal"、"target"、"none"、"auto" 等编码方式，自动识别类别型变量并执行相应编码，返回编码后数据及编码器对象 |
| target_col_encoding | 目标列编码方法，根据任务类型（分类/回归）及指定编码方式对目标变量进行编码，分类任务默认使用 "label" 编码，回归任务默认为 "none" |
| split_data_set | 数据集划分方法，根据 is_split 和 split_ratio 参数将数据划分为训练集和测试集，支持分类任务的分层抽样（stratify） |
| validate_cols_exist | 列存在性校验方法，检查 feature_cols 和 target_col 是否均存在于输入 DataFrame 中，缺失时报错并提示具体列名 |
| fill_missing_values | 缺失值填充方法，支持均值、中位数、众数、前向填充等策略，可针对数值型和类别型特征分别处理 |
| build_model_instance | 根据 model 名称和 model_params 参数从模型注册表中实例化对应模型对象，确保模型创建过程统一可控 |
| evaluate_model | 通用模型评估方法，接收模型、测试数据和 metrics_list，统一调用对应评分函数计算性能指标 |
|load_config | 加载配置文件方法，从指定路径加载配置文件，返回字典格式的配置信息 |

### 子类必须覆写的方法

| 方法名 | 描述 |
| ---- | ---- |
| analyzer | 执行完整分析流程的核心方法，包括数据预处理、模型训练、评估打分等步骤，返回标准化结果字典，是工厂调度的入口方法 |
| validate_params | 参数校验方法，检查当前任务所需的特定参数是否合法（如列名是否存在、模型参数范围等），校验失败时记录日志并抛出异常 |
| preprocess | 数据预处理方法，定义任务特定的特征工程逻辑，如标准化、归一化、特征选择、降维等，必须在训练前调用 |
| train | 模型训练方法，使用训练集数据拟合模型，需处理模型收敛、超参适配等细节，确保训练过程稳定 |
| postprocess | 训练后处理方法，用于执行特征重要性提取、模型解释（如 SHAP）、结果缓存或中间状态保存等操作 |
| get_feature_importance | 获取特征重要性或权重的方法，返回可解释的特征排序结果，用于下游可视化模块展示 |
| predict | 封装的预测方法，接收新数据并输出模型预测结果，支持概率输出（分类）或数值预测（回归） |
| save_model_artifacts | 模型产物持久化方法，负责将模型文件、编码器、特征列表等关键信息序列化保存，支持后续加载与部署 |
| load_params | 从配置文件中加载任务参数，如模型名称、超参数、特征列、目标列等，并返回字典 | 
| get_default_metrics | 根据 model_type 从 model_analysis.json 配置文件中加载默认评估指标列表，如分类任务返回 ["accuracy", "f1"]，回归任务返回 ["rmse", "r2"] |

## 异常处理

若必填参数为空，记录 ERROR 日志并抛出 ValueError。
推荐捕获异常并做统一错误响应处理。

```python
if df is None or df.empty:
    logger.error("Required parameter 'df' is None or empty.")
    raise ValueError("Parameter 'df' cannot be None or empty.")
```

## 传参流程

1. 调用方通过实例化` DataAnalysisUpgrade `创建分析器对象，并传入参数。
2. 接口执行空值校验，失败则记录日志并抛出异常。
3. 调用` analyze() `方法，将参数传递给` AnalyzerFactory.processing_selector()`。
4. `processing_selector` 根据 `learn_type` 选择对应的学习类型工厂类。
   - `learn_type` 为 `ML` 时，选择 `MachineLearningFactory`
   - `learn_type` 为 `DL` 时，选择 `DeepLearningFactory`（预留，当前版本可能未完全实现）
   `MachineLearningFactory`根据 `model_type` 选择对应的工厂类。
   - `model_type` 支持 "classification"、"regression"、"clustering"、"dimensionality_reduction" 等
5. 子模块工厂根据 `model` 名称实例化具体分析器。
   - `model` 名称根据 `model_analysis.json` 配置确定，用于和传入的模型名称匹配和执行对应的模型分析器
6. 具体分析器根据传入参数进行数据预处理、模型训练和评估。
7. 评估指标将根据 `model_type` 从 `model_analysis.json` 配置文件中获取：
   - 分类任务支持 accuracy、precision、recall、f1_score、roc_auc 等指标
   - 回归任务支持 mse、rmse、mae、r2_score 等指标
   - 聚类任务支持 silhouette_score、calinski_harabasz_score 等指标
8. 整个流程结合 `strategy.Strategy` 类控制训练、评估等执行策略，确保流程一致性。
   💡每个工厂都会有个与之对应的`strategy.Strategy`。
9. 最终返回包含模型、评估结果等信息的字典。

### 传参流程示意图

🔄 设计优势：新增模型无需修改主接口，只需在对应子工厂中注册即可，符合开闭原则。

## 支持的编码方式（参考）

| 编码方式 | 适用对象 | 说明 |
| -------- | -------- | ---- |
| onehot | 特征 | One-Hot 编码，适用于无序分类变量 |
| label | 特征/目标 | Label Encoding，适用于有序或二分类 |
| ordinal | 特征 | Ordinal Encoding，带顺序的分类变量 |
| target | 特征 | Target Encoding，用目标均值编码 |
| none | 任意 | 不编码 |
| auto | 任意 | 自动推断最佳编码方式 |

## 异常处理说明

| 异常类型 | 触发条件 | 建议处理方式 |
| -------- | -------- | ------------ |
| ValueError | 必填参数为空 | 检查输入数据与调用逻辑 |
| KeyError | 列名不存在于 DataFrame | 核对 feature_cols 和 target_col |
| NotImplementedError | 所选模型未实现 | 检查 model 名称拼写或确认是否已注册 |
| 自定义异常 | （可扩展） | 如 ModelTrainingFailedError |

## 版本变更说明（v2.0）

| 变更项 | 说明 |
| ------ | ---- |
| 接口统一 | 引入 DataAnalysisUpgrade 作为唯一公共接口 |
| 工厂增强 | 支持基于 learn_type + model_type 的两级路由 |
| 编码解耦 | 编码方式独立配置，支持灵活组合 |
| 日志规范 | 明确校验日志输出标准 |
| 向后兼容 | 不兼容 v1.0，需重构调用方式 |

## 使用示例

```python
from Src.DataAnalyzer.ModuleInterfaces.data_analysis_upgrade_interface import DataAnalysisUpgrade

# 构造数据
import pandas as pd
df = pd.read_csv("data.csv")

# 初始化分析器
analyzer = DataAnalysisUpgrade(
    df=df,
    learn_type="ML",
    model_type="classification",
    model="random_forest",
    feature_cols=["age", "income", "gender"],
    target_col="churn",
    metrics_list=["accuracy", "f1"],
    is_split=True,
    split_ratio=0.3,
    feature_cols_encoding="onehot",
    target_col_encoding="label",
    random_state=42,
    model_params={"n_estimators": 100}
)

# 执行分析
result = analyzer.analyze()

# 输出结果
print("Model Score:", result["model_score"])
print("Features Used:", result["feature_cols"])
```


📅 最后更新：2025年10月24日

👤 维护团队：linmowudie、lingma Agent （AI）