# DataProcessingEngine 核心引擎接口文档

## 概述

`DataProcessingEngine` 是整个数据分析工具的核心类，提供统一的接口来执行完整的数据分析流程。该引擎封装了数据导入、清洗、分析、可视化及报告生成等阶段，通过状态管理方式维护各阶段中间结果，确保流程有序执行。

## 类：DataProcessingEngine

### 构造函数

```python
DataProcessingEngine()
```

初始化数据处理引擎，创建中间数据状态和临时存储管理器。

### 属性

- `imported_data` (Optional[pd.DataFrame]): 导入的数据
- `cleaned_data` (Optional[pd.DataFrame]): 清洗后的数据
- `analyzed_data` (Optional[dict]): 分析结果数据
- `visualized_plot` (Optional[Dict[str, Figure]]): 可视化图表
- `report_data` (Optional[Dict]): 报告数据
- `temp_storage` (TempStorageManager): 临时存储管理器

### 方法

#### import_data()

导入数据，支持文件或数据库表。

```python
import_data(
    resource_path: Union[Path, str],
    resource_type: str,
    db_connection_string: Optional[str] = None,
    query: Optional[str] = None,
    is_database: bool = False
) -> None
```

**参数说明：**
- `resource_path` (Union[Path, str]): 文件路径或资源标识
- `resource_type` (str): 资源类型，如 'csv', 'excel', 'json', 'db'
- `db_connection_string` (Optional[str]): 数据库连接字符串（仅用于数据库）
- `query` (Optional[str]): SQL 查询语句（仅用于数据库）
- `is_database` (bool): 是否为数据库源

**异常：**
- `ValueError`: 当数据库连接字符串为空但 is_database 为 True 时抛出

#### clean_data()

执行数据清洗操作。

```python
clean_data(
    select_mode: str,
    params_list: List[str],
    is_freedom_params: bool = False
) -> None
```

**参数说明：**
- `select_mode` (str): 清洗模式（如 'standard', 'strict', 'relaxed'）
- `params_list` (List[str]): 参数列表，如要处理的列名或规则
- `is_freedom_params` (bool): 是否为自由格式参数

**异常：**
- `ValueError`: 当未导入数据或清洗失败时抛出

#### analyze_data()

执行数据分析操作。

```python
analyze_data(
    model: str,
    random_state: int = 42,
    is_split: bool = True,
    split_ratio: float = 0.8,
    feature_cols: Optional[List[str]] = None,
    target_col: Optional[str] = None,
    is_return_model_param: bool = False,
    metrics_list: Optional[List[str]] = None,
    is_return_model_score: bool = True,
    is_return_training_set: bool = False,
    is_return_model_predicting_set: bool = False,
    feature_cols_encoding: str = 'onehot',
    target_col_encoding: str = 'label',
    test_set: Optional[pd.DataFrame] = None,
    model_params: Optional[Dict[str, Any]] = None
) -> None
```

**参数说明：**
- `model` (str): 机器学习模型名称
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

**异常：**
- `ValueError`: 当未清洗数据或分析失败时抛出

#### visualize_data()

执行数据可视化操作。

```python
visualize_data(param_dict: Optional[Dict[str, Any]] = None) -> None
```

**参数说明：**
- `param_dict` (Optional[Dict[str, Any]]): 可视化参数字典，如果为 None 则使用分析结果中的默认参数

**异常：**
- `ValueError`: 当未分析数据或可视化失败时抛出

#### generate_report()

生成分析报告。

```python
generate_report() -> None
```

#### get_report()

获取生成的报告数据。

```python
get_report() -> Optional[Dict]
```

**返回值：**
- `Optional[Dict]`: 报告数据字典或 None（如果尚未生成报告）

#### run_complete_process()

运行完整的数据处理流程。

```python
run_complete_process(
    import_params: Dict[str, Any],
    clean_params: Dict[str, Any],
    analyze_params: Dict[str, Any],
    visualize_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**参数说明：**
- `import_params` (Dict[str, Any]): 数据导入参数
- `clean_params` (Dict[str, Any]): 数据清洗参数
- `analyze_params` (Dict[str, Any]): 数据分析参数
- `visualize_params` (Optional[Dict[str, Any]]): 数据可视化参数（可选）

**返回值：**
- `Dict[str, Any]`: 包含所有处理结果的字典

#### cleanup()

清理中间数据和优化内存。

```python
cleanup() -> None
```

### 使用示例

#### 基本使用流程

```python
from Src.DataAnalyzer.core import DataProcessingEngine

# 创建引擎实例
engine = DataProcessingEngine()

# 1. 数据导入
engine.import_data("data.csv", "csv")

# 2. 数据清洗
engine.clean_data("standard", [])

# 3. 数据分析
engine.analyze_data(
    model="LinearRegression",
    target_col="target",
    feature_cols=["feature1", "feature2"]
)

# 4. 数据可视化
engine.visualize_data()

# 5. 生成报告
engine.generate_report()

# 6. 获取报告
report = engine.get_report()
```

#### 完整流程使用

```python
from Src.DataAnalyzer.core import DataProcessingEngine

# 创建引擎实例
engine = DataProcessingEngine()

# 定义各阶段参数
import_params = {
    "resource_path": "data.csv",
    "resource_type": "csv"
}

clean_params = {
    "select_mode": "standard",
    "params_list": []
}

analyze_params = {
    "model": "LogisticRegression",
    "target_col": "target",
    "feature_cols": ["feature1", "feature2"],
    "metrics_list": ["accuracy"]
}

# 运行完整流程
result = engine.run_complete_process(
    import_params=import_params,
    clean_params=clean_params,
    analyze_params=analyze_params
)

# 访问结果
imported_data = result["imported_data"]
cleaned_data = result["cleaned_data"]
analyzed_data = result["analyzed_data"]
report = result["report"]
```

#### 数据库导入示例

```python
from Src.DataAnalyzer.core import DataProcessingEngine

# 创建引擎实例
engine = DataProcessingEngine()

# 从数据库导入数据
engine.import_data(
    resource_path="table_name",
    resource_type="sqlite",
    db_connection_string="sqlite:///database.db",
    query="SELECT * FROM table_name",
    is_database=True
)

# 后续处理步骤...
```