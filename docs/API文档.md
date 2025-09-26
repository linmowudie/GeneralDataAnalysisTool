# 通用数据分析工具 API 文档

## 概述

通用数据分析工具是一个完整的数据分析解决方案，提供从数据导入、清洗、分析到可视化的全流程功能。该工具采用模块化设计，每个功能模块都有清晰的接口和职责。

本文档提供了整个系统的API概览。有关各模块的详细接口文档，请参阅以下专门的文档：

- [DataImport 模块](modules/data_import.md) - 数据导入功能
- [DataCleaning 模块](modules/data_cleaning.md) - 数据清洗功能
- [DataAnalysis 模块](modules/data_analysis.md) - 数据分析功能
- [DataVisualization 模模块](modules/data_visualization.md) - 数据可视化功能
- [DataProcessingEngine 核心引擎](modules/core_engine.md) - 核心处理引擎
- [Reporting 报告生成](modules/reporting.md) - 报告生成功能

## 核心模块

### 1. DataProcessingEngine (数据处理引擎)

这是整个工具的核心类，提供统一的接口来执行完整的数据分析流程。

#### 构造函数

```python
DataProcessingEngine()
```

#### 方法

##### import_data()

从文件或数据库导入数据。

**参数:**
- `resource_path` (Union[Path, str]): 文件路径或资源标识
- `resource_type` (str): 资源类型，如 'csv', 'excel', 'json', 'db'
- `db_connection_string` (Optional[str]): 数据库连接字符串（仅用于数据库）
- `query` (Optional[str]): SQL 查询语句（仅用于数据库）
- `is_database` (bool): 是否为数据库源，默认为 False

##### clean_data()

执行数据清洗操作。

**参数:**
- `select_mode` (str): 清洗模式（如 'auto', 'manual'）
- `params_list` (List[str]): 参数列表，如要处理的列名或规则
- `is_freedom_params` (bool): 是否为自由格式参数，默认为 False

##### analyze_data()

执行数据分析操作。

**参数:**
- `model` (str): 机器学习模型实例（如 sklearn 模型）
- `random_state` (int): 随机种子，默认为 42
- `is_split` (bool): 是否划分训练/测试集，默认为 True
- `split_ratio` (float): 训练集比例，默认为 0.8
- `feature_cols` (Optional[List[str]]): 特征列名列表
- `target_col` (Optional[str]): 目标列名
- `is_return_model_param` (bool): 是否返回模型超参，默认为 False
- `metrics_list` (Optional[List[str]]): 评估指标列表，如 ['accuracy', 'f1']
- `is_return_model_score` (bool): 是否返回模型评分，默认为 True
- `is_return_training_set` (bool): 是否返回训练集，默认为 False
- `is_return_model_predicting_set` (bool): 是否返回预测结果，默认为 False
- `feature_cols_encoding` (str): 特征列编码映射，默认为 'onehot'
- `target_col_encoding` (str): 标签列编码映射，默认为 'label'
- `test_set` (Optional[pd.DataFrame]): 外部测试集（可选）
- `model_params` (Optional[Dict[str, Any]]): 模型参数字典，用于覆盖默认参数

##### visualize_data()

执行数据可视化操作。

**参数:**
- `param_dict` (Optional[Dict[str, Any]]): 可视化参数字典，如果为None则使用分析结果中的默认参数
  - `interactive` (bool): 是否使用交互式可视化，默认为 False

##### generate_report()

生成分析报告。

##### get_report()

获取生成的报告数据。

**返回:**
- Optional[Dict]: 报告数据字典或None（如果尚未生成报告）

##### run_complete_process()

运行完整的数据处理流程。

**参数:**
- `import_params` (Dict[str, Any]): 数据导入参数
- `clean_params` (Dict[str, Any]): 数据清洗参数
- `analyze_params` (Dict[str, Any]): 数据分析参数
- `visualize_params` (Optional[Dict[str, Any]]): 数据可视化参数（可选）

**返回:**
- Dict[str, Any]: 包含所有处理结果的字典

### 2. DataImport (数据导入)

负责从文件或数据库导入数据。

#### 构造函数

```python
DataImport(file_resource: Union[str, Path], resource_type: str, db_connection_string: Optional[str] = None, is_database: bool = False)
```

**参数:**
- `file_resource` (Union[str, Path]): 文件路径或数据库表名
- `resource_type` (str): 文件类型（csv/json/xlsx）或数据库类型（sqlite/postgresql）
- `db_connection_string` (Optional[str]): 数据库连接字符串（仅数据库模式需要）
- `is_database` (bool): 是否从数据库导入

#### 方法

##### import_data()

执行数据导入。

**参数:**
- `**kwargs`: 传递给具体导入方法的参数

**返回:**
- Optional[pd.DataFrame]: Pandas DataFrame 或 None

##### close_connection()

关闭数据库连接（如果是数据库模式）。

### 3. CleanDataMode (数据清洗)

提供多种数据清洗模式。

#### 构造函数

```python
CleanDataMode(df: pd.DataFrame, select_mode: str, params_list: list[str], is_freedom_params: bool = False)
```

**参数:**
- `df` (pd.DataFrame): 待清洗的数据
- `select_mode` (str): 清洗模式（如 'standard', 'strict', 'relaxed'）
- `params_list` (list[str]): 参数列表
- `is_freedom_params` (bool): 是否为自由格式参数，默认为 False

#### 方法

##### clean_data()

执行数据清洗。

**返回:**
- pd.DataFrame: 清洗后的数据

### 4. DataAnalyzer (数据分析)

执行数据分析操作。

#### 构造函数

```python
DataAnalyzer(df: pd.DataFrame, model: str, random_state: int = 42, is_split: bool = True, split_ratio: float = 0.8, feature_cols: Optional[List[str]] = None, target_col: Optional[str] = None, is_return_model_param: bool = False, metrics_list: Optional[List[str]] = None, is_return_model_score: bool = True, is_return_training_set: bool = False, is_return_model_predicting_set: bool = False, feature_cols_encoding: str = 'onehot', target_col_encoding: str = 'label', test_set: Optional[pd.DataFrame] = None, model_params: Optional[Dict[str, Any]] = None)
```

**参数:**
- `df` (pd.DataFrame): 待分析的数据集
- `model` (str): 模型名称
- `random_state` (int): 随机种子，默认为 42
- `is_split` (bool): 是否进行数据集分割，默认为 True
- `split_ratio` (float): 数据集分割比例，默认为 0.8
- `feature_cols` (Optional[List[str]]): 特征列名称列表
- `target_col` (Optional[str]): 目标列名称
- `is_return_model_param` (bool): 是否返回模型参数，默认为 False
- `metrics_list` (Optional[List[str]]): 评价指标列表
- `is_return_model_score` (bool): 是否返回模型得分，默认为 True
- `is_return_training_set` (bool): 是否返回训练集，默认为 False
- `is_return_model_predicting_set` (bool): 是否返回模型预测集，默认为 False
- `feature_cols_encoding` (str): 特征列中类别变量的编码方式，默认为 'onehot'
- `target_col_encoding` (str): 目标列编码方式，默认为 'label'
- `test_set` (Optional[pd.DataFrame]): 测试集数据集，默认为 None
- `model_params` (Optional[Dict[str, Any]]): 模型参数字典，用于覆盖默认参数

#### 方法

##### analyze()

执行数据分析并返回结果。

**返回:**
- dict: 分析结果

### 支持的模型及初始化示例

数据分析模块支持多种机器学习模型，以下是每种模型的详细说明和初始化示例：

##### LinearRegression (线性回归)

任务类型: regression

**初始化参数:**
- `fit_intercept` (bool): 是否计算此模型的截距，默认为 True

**示例:**
```python
# 使用默认参数
analyzer = DataAnalyzer(df, model='LinearRegression')

# 指定参数
analyzer = DataAnalyzer(df, model='LinearRegression', model_params={'fit_intercept': False})
```

##### LogisticRegression (逻辑回归)

任务类型: classification

**初始化参数:**
- `C` (float): 正则化强度的倒数，必须为正数，默认为 1.0
- `max_iter` (int): 最大迭代次数，默认为 1000
- `fit_intercept` (bool): 是否计算此模型的截距，默认为 True
- `solver` (str): 优化算法，默认为 'liblinear'

**示例:**
```python
# 使用默认参数
analyzer = DataAnalyzer(df, model='LogisticRegression')

# 指定参数
analyzer = DataAnalyzer(df, model='LogisticRegression', model_params={'C': 0.5, 'max_iter': 500})
```

##### DecisionTreeClassifier (决策树分类器)

任务类型: classification

**初始化参数:**
- `max_depth` (int): 树的最大深度，默认为 None
- `min_samples_split` (int): 分割内部节点所需的最小样本数，默认为 2
- `random_state` (int): 控制随机性，默认为 42

**示例:**
```python
# 使用默认参数
analyzer = DataAnalyzer(df, model='DecisionTreeClassifier')

# 指定参数
analyzer = DataAnalyzer(df, model='DecisionTreeClassifier', model_params={'max_depth': 5, 'min_samples_split': 10})
```

##### KNeighborsClassifier (K近邻分类器)

任务类型: classification

**初始化参数:**
- `n_neighbors` (int): 用于 kneighbors 查询的邻居数量，默认为 5

**示例:**
```python
# 使用默认参数
analyzer = DataAnalyzer(df, model='KNeighborsClassifier')

# 指定参数
analyzer = DataAnalyzer(df, model='KNeighborsClassifier', model_params={'n_neighbors': 3})
```

##### KMeans (K均值聚类)

任务类型: clustering

**初始化参数:**
- `n_clusters` (int): 聚类数，默认为 3
- `random_state` (int): 控制随机性，默认为 42

**示例:**
```python
# 使用默认参数
analyzer = DataAnalyzer(df, model='KMeans')

# 指定参数
analyzer = DataAnalyzer(df, model='KMeans', model_params={'n_clusters': 5})
```

##### MeanShift (均值漂移聚类)

任务类型: clustering

**初始化参数:**
- `bandwidth` (float): RBF 核的带宽参数，默认为 None

**示例:**
```python
# 使用默认参数
analyzer = DataAnalyzer(df, model='MeanShift')

# 指定参数
analyzer = DataAnalyzer(df, model='MeanShift', model_params={'bandwidth': 2.0})
```

##### StandardScaler (标准化缩放器)

任务类型: transformer

**初始化参数:**
- 无特定参数

**示例:**
```python
# 使用默认参数
analyzer = DataAnalyzer(df, model='StandardScaler')
```

##### PCA (主成分分析)

任务类型: transformer

**初始化参数:**
- `n_components` (int): 保留的成分数量，默认为 2

**示例:**
```python
# 使用默认参数
analyzer = DataAnalyzer(df, model='PCA')

# 指定参数
analyzer = DataAnalyzer(df, model='PCA', model_params={'n_components': 3})
```

### 5. DataVisualization (数据可视化)

负责数据可视化操作。

#### 构造函数

```python
DataVisualization(param_dict: Dict[str, Any])
```

**参数:**
- `param_dict` (Dict[str, Any]): 参数字典，包含以下字段：
  - `task_type`: 任务类型 (classification, regression, clustering, transformer)
  - `model_name`: 模型名称 (小写)
  - `feature`: 特征矩阵 (pandas.DataFrame)
  - `target`: 目标值 (pandas.Series, 可选)
  - `predict`: 预测值 (pandas.Series, 可选)
  - `label_style`: 标签样式 {x: str, y: str, title: str}
  - `plot_style`: 绘图风格 (matplotlib风格)
  - `shape_style`: 形状样式 {points: {size: int, colors: list}, lines: {width: float, styles: list}}
  - `font_style`: 字体样式
  - `model_specific`: 模型特定参数 (如聚类中心、解释方差等)
  - `interactive`: 是否使用交互式可视化 (布尔值，默认为False)

#### 方法

##### validate_params()

验证必要参数。

##### plot_chart()

生成图表。

**返回:**
- Dict[str, Union[Figure, go.Figure]]: 生成的图表字典

##### apply_global_styles()

应用全局绘图样式。

### 交互式可视化功能

数据分析工具现在支持交互式可视化功能，基于 Plotly 库实现。通过设置 `interactive=True` 参数，可以生成具有以下特性的交互式图表：

- 鼠标悬停显示详细信息
- 图表缩放和平移
- 数据系列的选择和取消选择
- 3D图表的旋转和视角调整
- 可导出为HTML文件在浏览器中查看

交互式可视化支持以下模型类型：
- 回归模型 (regression): linearregression
- 聚类模型 (clustering): kmeans
- 变换器 (transformer): 3d, surface

### 各模型可视化参数说明

数据分析工具支持多种模型的可视化，每种模型都有其特定的可视化方式和参数。以下是每种模型的可视化参数说明：

#### LinearRegression (线性回归)

可视化类型:
1. 真实值 vs 预测值散点图
2. 残差图

**参数:**
- `target`: 真实值 (pandas.Series)
- `predict`: 预测值 (pandas.Series)
- `label_style`: 标签样式字典
  - `title`: 图表标题
  - `x`: X轴标签
  - `y`: Y轴标签
- `shape_style`: 形状样式字典
  - `points`: 点样式
    - `size`: 点大小，默认为 30
    - `colors`: 颜色列表，默认为 ["blue"]

**示例:**
```python
param_dict = {
    "task_type": "regression",
    "model_name": "linearregression",
    "feature": X_test,
    "target": y_test,
    "predict": y_pred,
    "label_style": {
        "title": "线性回归结果",
        "x": "真实值",
        "y": "预测值"
    },
    "shape_style": {
        "points": {
            "size": 50,
            "colors": ["red"]
        }
    }
}
```

#### LogisticRegression (逻辑回归)

可视化类型:
1. 混淆矩阵热力图
2. ROC曲线 (二分类)
3. 特征系数柱状图

**参数:**
- `target`: 真实值 (pandas.Series)
- `predict`: 预测值 (pandas.Series)
- `feature`: 特征矩阵 (pandas.DataFrame)
- `label_style`: 标签样式字典
- `shape_style`: 形状样式字典
  - `points`: 点样式
    - `colors`: 颜色列表，默认为 ["tab:blue"]
- `model_specific`: 模型特定参数
  - `y_score`: 预测概率 (用于ROC曲线)
  - `trained_model`: 训练好的模型 (用于获取系数)

**示例:**
```python
param_dict = {
    "task_type": "classification",
    "model_name": "logisticregression",
    "feature": X_test,
    "target": y_test,
    "predict": y_pred,
    "label_style": {
        "title": "逻辑回归分类结果"
    },
    "shape_style": {
        "points": {
            "colors": ["green"]
        }
    },
    "model_specific": {
        "y_score": y_prob,
        "trained_model": trained_model
    }
}
```

#### DecisionTreeClassifier (决策树分类器)

可视化类型:
1. 混淆矩阵热力图
2. 特征重要性柱状图
3. 决策树结构图

**参数:**
- `target`: 真实值 (pandas.Series)
- `predict`: 预测值 (pandas.Series)
- `feature`: 特征矩阵 (pandas.DataFrame)
- `label_style`: 标签样式字典
- `shape_style`: 形状样式字典
  - `points`: 点样式
    - `colors`: 颜色列表，默认为 ["tab:blue"]
- `model_specific`: 模型特定参数
  - `trained_model`: 训练好的模型 (用于获取特征重要性和绘制树结构)

**示例:**
```python
param_dict = {
    "task_type": "classification",
    "model_name": "decisiontreeclassifier",
    "feature": X_test,
    "target": y_test,
    "predict": y_pred,
    "label_style": {
        "title": "决策树分类结果"
    },
    "model_specific": {
        "trained_model": trained_model
    }
}
```

#### KNeighborsClassifier (K近邻分类器)

可视化类型:
1. 混淆矩阵热力图
2. ROC曲线 (仅二分类)
3. 决策边界 (仅二维特征)

**参数:**
- `target`: 真实值 (pandas.Series)
- `predict`: 预测值 (pandas.Series)
- `feature`: 特征矩阵 (pandas.DataFrame)
- `label_style`: 标签样式字典
- `shape_style`: 形状样式字典
  - `points`: 点样式
    - `colors`: 颜色列表，默认为 ["tab:blue"]
- `model_specific`: 模型特定参数
  - `trained_model`: 训练好的模型
  - `y_score`: 预测概率 (用于ROC曲线)

**示例:**
```python
param_dict = {
    "task_type": "classification",
    "model_name": "kneighborsclassifier",
    "feature": X_test,
    "target": y_test,
    "predict": y_pred,
    "label_style": {
        "title": "K近邻分类结果"
    },
    "shape_style": {
        "points": {
            "colors": ["orange"]
        }
    },
    "model_specific": {
        "trained_model": trained_model,
        "y_score": y_prob
    }
}
```

#### KMeans (K均值聚类)

可视化类型:
1. 聚类结果散点图 (二维)
2. 聚类大小柱状图
3. 三维特征投影图 (三个或更多特征)

**参数:**
- `feature`: 特征矩阵 (pandas.DataFrame)
- `label_style`: 标签样式字典
- `shape_style`: 形状样式字典
  - `points`: 点样式
    - `size`: 点大小，默认为 50
    - `colors`: 颜色列表，默认为 ["tab:blue", "tab:orange", "tab:green"]
- `model_specific`: 模型特定参数
  - `trained_model`: 训练好的模型 (用于获取标签和聚类中心)

**示例:**
```python
param_dict = {
    "task_type": "clustering",
    "model_name": "kmeans",
    "feature": X,
    "label_style": {
        "title": "KMeans聚类结果",
        "x": "特征1",
        "y": "特征2"
    },
    "shape_style": {
        "points": {
            "size": 60,
            "colors": ["red", "blue", "green"]
        }
    },
    "model_specific": {
        "trained_model": trained_model
    }
}
```

#### MeanShift (均值漂移聚类)

可视化类型:
1. 聚类结果散点图 (二维)
2. 聚类大小柱状图
3. 一维直方图 (仅一维特征)

**参数:**
- `feature`: 特征矩阵 (pandas.DataFrame)
- `label_style`: 标签样式字典
- `shape_style`: 形状样式字典
  - `points`: 点样式
    - `size`: 点大小，默认为 30
- `model_specific`: 模型特定参数
  - `trained_model`: 训练好的模型 (用于获取标签和聚类中心)

**示例:**
```python
param_dict = {
    "task_type": "clustering",
    "model_name": "meanshift",
    "feature": X,
    "label_style": {
        "title": "MeanShift聚类结果"
    },
    "shape_style": {
        "points": {
            "size": 40
        }
    },
    "model_specific": {
        "trained_model": trained_model
    }
}
```

#### StandardScaler (标准化缩放器)

可视化类型:
1. 原始数据与标准化数据分布对比图
2. 标准化后特征的箱线图

**参数:**
- `feature`: 原始特征矩阵 (pandas.DataFrame)
- `model_specific`: 模型特定参数
  - `transformed`: 标准化后的数据矩阵

**示例:**
```python
param_dict = {
    "task_type": "transformer",
    "model_name": "standardscaler",
    "feature": X_original,
    "model_specific": {
        "transformed": X_scaled
    }
}
```

#### PCA (主成分分析)

可视化类型:
1. 方差解释率柱状图和累积曲线
2. 主成分投影散点图 (前两个主成分)

**参数:**
- `feature`: PCA变换后的特征矩阵 (pandas.DataFrame)
- `label_style`: 标签样式字典
- `model_specific`: 模型特定参数
  - `explained_variance_ratio`: 各主成分的方差解释率

**示例:**
```python
param_dict = {
    "task_type": "transformer",
    "model_name": "pca",
    "feature": X_pca,
    "label_style": {
        "title": "PCA结果",
        "x": "第一主成分",
        "y": "第二主成分"
    },
    "model_specific": {
        "explained_variance_ratio": explained_variance_ratio
    }
}
```

#### 3D可视化 (3D Visualization)

可视化类型:
1. 3D散点图
2. 3D曲面图

**参数:**
- `feature`: 特征矩阵 (pandas.DataFrame) - 需要至少3列特征
- `label_style`: 标签样式字典
  - `x`: X轴标签
  - `y`: Y轴标签
  - `z`: Z轴标签
  - `title`: 图表标题

**示例:**
```python
param_dict = {
    "task_type": "transformer",
    "model_name": "3d",
    "feature": pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'z': np.random.randn(100)
    }),
    "label_style": {
        "title": "3D散点图",
        "x": "X轴",
        "y": "Y轴",
        "z": "Z轴"
    }
}
```

### 6. Report (报告生成)

生成数据分析报告。

#### 构造函数

```python
Report(model_params: Optional[Dict] = None, model_scores: Optional[Dict] = None, visualizations: Optional[Dict] = None, model_predictions: Optional[pd.Series] = None)
```

**参数:**
- `model_params` (Optional[Dict]): 模型参数
- `model_scores` (Optional[Dict]): 模型得分
- `visualizations` (Optional[Dict]): 可视化结果
- `model_predictions` (Optional[pd.Series]): 模型预测结果

#### 方法

##### return_report()

返回报告内容。

**返回:**
- Dict: 报告内容