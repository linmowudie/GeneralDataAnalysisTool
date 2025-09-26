# DataCleaning 模块接口文档

## 概述

`DataCleaning` 模块提供多种数据清洗模式，包括标准、严格和宽松模式，也支持自定义参数进行数据清洗。该模块继承自 `CleanData` 基类。

## 类：CleanDataMode

### 构造函数

```python
CleanDataMode(
    df: pd.DataFrame,
    select_mode: str,
    params_list: list[str],
    is_freedom_params: bool = False
)
```

**参数说明：**
- `df` (pd.DataFrame): 待清洗的数据
- `select_mode` (str): 清洗模式（支持 "standard", "strict", "relaxed"）
- `params_list` (list[str]): 参数列表
- `is_freedom_params` (bool): 是否为自由格式参数，默认为 False

### 方法

#### clean_data()

执行数据清洗操作。

```python
clean_data() -> pd.DataFrame
```

**返回值：**
- `pd.DataFrame`: 清洗后的数据

**异常：**
- `ValueError`: 当清洗模式不支持或清洗过程中发生错误时抛出
- `AttributeError`: 当指定的清洗方法未实现时抛出
- `TypeError`: 当清洗方法返回的不是 DataFrame 时抛出

### 支持的清洗模式

#### standard（标准模式）
标准数据清洗流程，处理常见的数据质量问题，如缺失值、重复值等。

#### strict（严格模式）
严格的清洗流程，会移除更多可能有问题的数据，确保数据质量。

#### relaxed（宽松模式）
宽松的清洗流程，仅处理最明显的数据问题，保留更多原始数据。

### 使用示例

#### 标准清洗模式

```python
from Src.DataAnalyzer.ModuleInterfaces.data_cleaning import CleanDataMode
import pandas as pd

# 创建示例数据
df = pd.DataFrame({
    'A': [1, 2, None, 4, 5],
    'B': ['a', 'b', 'c', 'd', None],
    'C': [1.1, 2.2, 3.3, None, 5.5]
})

# 使用标准清洗模式
cleaner = CleanDataMode(df, "standard", [])
cleaned_df = cleaner.clean_data()
```

#### 自定义清洗模式

```python
from Src.DataAnalyzer.ModuleInterfaces.data_cleaning import CleanDataMode
import pandas as pd

# 创建示例数据
df = pd.DataFrame({
    'A': [1, 2, 3, 4, 5],
    'B': ['a', 'b', 'c', 'd', 'e']
})

# 使用自定义清洗参数
cleaner = CleanDataMode(df, "custom", ["dropna"], is_freedom_params=True)
cleaned_df = cleaner.clean_data()
```

### 扩展自定义清洗方法

可以通过继承 `CleanDataMode` 类并实现自定义方法来扩展清洗功能：

```python
from Src.DataAnalyzer.ModuleInterfaces.data_cleaning import CleanDataMode
import pandas as pd

class CustomCleaner(CleanDataMode):
    def custom_clean_method(self, df):
        # 实现自定义清洗逻辑
        return df.drop_duplicates()

# 使用自定义清洗方法
df = pd.DataFrame({'A': [1, 2, 2, 3], 'B': ['a', 'b', 'b', 'c']})
cleaner = CustomCleaner(df, "custom_clean_method", [], is_freedom_params=True)
cleaned_df = cleaner.clean_data()
```