# DataImport 模块接口文档

## 概述

`DataImport` 模块提供统一的数据导入接口，支持从文件和数据库导入数据。该模块使用组合模式，避免多重继承带来的问题，并支持大文件读取优化。

## 类：DataImport

### 构造函数

```python
DataImport(
    file_resource: Union[str, Path],
    resource_type: str,
    db_connection_string: Optional[str] = None,
    is_database: bool = False
)
```

**参数说明：**
- `file_resource` (Union[str, Path]): 文件路径或数据库表名（根据模式决定）
- `resource_type` (str): 文件类型（csv/json/xlsx）或数据库类型（sqlite/postgresql）
- `db_connection_string` (Optional[str]): 数据库连接字符串（仅数据库模式需要）
- `is_database` (bool): 是否从数据库导入，默认为 False

**异常：**
- `ValueError`: 当 `is_database` 为 True 但未提供 `db_connection_string` 时抛出

### 方法

#### import_data()

执行数据导入操作。

```python
import_data(chunksize: Optional[int] = None, **kwargs) -> Optional[pd.DataFrame]
```

**参数说明：**
- `chunksize` (Optional[int]): 分块读取大小，用于大文件处理
- `**kwargs`: 传递给具体导入方法的参数

**返回值：**
- `Optional[pd.DataFrame]`: 成功时返回 Pandas DataFrame，失败时返回 None

**说明：**
- 对于大于 100MB 的文件，会自动启用分块读取（默认块大小为 10000 行）
- 支持 with 语句上下文管理器自动关闭数据库连接

#### close_connection()

关闭数据库连接（如果是数据库模式）。

```python
close_connection() -> None
```

### 使用示例

#### 文件导入示例

```python
from Src.DataAnalyzer.ModuleInterfaces.data_import import DataImport

# CSV 文件导入
importer = DataImport("data.csv", "csv")
df = importer.import_data()

# 大文件导入（手动指定分块大小）
importer = DataImport("large_data.csv", "csv")
df = importer.import_data(chunksize=5000)
```

#### 数据库导入示例

```python
from Src.DataAnalyzer.ModuleInterfaces.data_import import DataImport

# SQLite 数据库导入
importer = DataImport(
    "table_name", 
    "sqlite", 
    db_connection_string="sqlite:///database.db",
    is_database=True
)
df = importer.import_data(query="SELECT * FROM table_name")
```

#### 使用上下文管理器

```python
from Src.DataAnalyzer.ModuleInterfaces.data_import import DataImport

# 自动管理数据库连接
with DataImport(
    "table_name", 
    "sqlite", 
    db_connection_string="sqlite:///database.db",
    is_database=True
) as importer:
    df = importer.import_data(query="SELECT * FROM table_name")
    # 连接会自动关闭
```