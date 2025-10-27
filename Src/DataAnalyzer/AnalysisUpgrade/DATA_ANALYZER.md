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

📌 注意：异常检测任务类型已在配置文件中定义了评估指标，但目前仅作为占位符，尚未实现具体功能。同时，异常检测模型未列入 `support_ML_models` 列表中。

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
- 由 `MainFactory` 及其子工厂类实现
- 实现两级路由机制：
  - 第一级：根据 `learn_type` 选择工厂（ML或DL）
  - 第二级：根据 `model_type` 选择任务类型工厂
- 负责创建具体的分析器实例

### 策略层 (Strategy Layer)
- 由 `BaseStrategy` 基类及其子类实现
- 控制分析流程的执行顺序和逻辑
- 根据任务类型选择对应的策略实现
- 处理任务特定的执行逻辑

📌 注意：目前策略层支持 classification、regression、clustering 和 dimensionality_reduction 四种任务类型，anomaly_detection（异常检测）任务类型已预留但尚未实现。

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
| load_config | 加载配置文件方法，从指定路径加载配置文件，返回字典格式的配置信息 |

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

## 底层处理器类 {Model}Analyzer 实现指南

### 1. 类的基本结构

所有分析器类都需要继承自 `BaseAnalyzer`，并实现所有抽象方法。以下是一个典型的分析器类结构：

```python
from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

class ModelAnalyzer(BaseAnalyzer):
    """
    模型分析器类
    
    负责执行特定模型的训练、评估和预测等操作。
    """
    
    def __init__(self):
        super().__init__()
        self.model = None  # 初始化模型对象
        # 可在此处添加其他必要的实例变量
    
    # 实现所有必须覆写的方法...
```

### 2. 方法实现详细指南

#### 2.1 load_params 方法

**功能**：加载和处理模型参数，确保参数格式正确且可被模型使用。

**实现步骤**：
1. 接收模型参数字典或 None
2. 检查参数类型，确保返回字典格式
3. 对必要的参数进行类型转换或默认值设置
4. 返回处理后的参数字典

**示例实现**：

```python
def load_params(self, model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    加载和处理模型参数
    
    参数:
        model_params (Dict[str, Any]): 模型参数字典，如果为None则返回空字典
        
    返回:
        Dict[str, Any]: 处理后的参数字典
    """
    # 处理空值情况
    if model_params is None:
        return {}
    
    # 确保是字典类型
    if not isinstance(model_params, dict):
        try:
            model_params = dict(model_params)
        except:
            # 转换失败时返回空字典
            return {}
    
    # 创建参数副本避免修改原始数据
    processed_params = model_params.copy()
    
    # 对特定参数进行类型转换或验证
    # 例如：确保n_components是整数
    if 'n_components' in processed_params:
        try:
            processed_params['n_components'] = int(processed_params['n_components'])
        except (ValueError, TypeError):
            # 如果转换失败，移除该参数或设置默认值
            processed_params.pop('n_components', None)
    
    # 返回处理后的参数
    return processed_params
```

#### 2.2 validate_params 方法

**功能**：验证模型参数的合法性，包括参数名和参数值的范围检查。

**实现步骤**：
1. **从配置文件中读取当前模型支持的参数列表**（推荐方式，而非硬编码）
2. 检查传入参数是否都在支持的列表中
3. 对关键参数进行值域检查
4. 校验失败时记录日志并抛出异常

**示例实现**：

```python
def validate_params(self, model_params: Dict[str, Any]) -> bool:
    """
    验证模型参数的合法性
    
    参数:
        model_params (Dict[str, Any]): 需要验证的模型参数字典
        
    返回:
        bool: 验证通过返回True
        
    异常:
        ValueError: 当参数不合法时抛出
    """
    # 从配置文件中读取支持的参数列表（推荐方式）
    # 1. 首先确保配置已加载到类的属性中
    # 2. 根据模型类型和名称获取支持的参数列表
    
    # 示例：从加载的配置中获取PCA模型的参数列表
    # 假设self.config包含model_analysis.json的内容
    if hasattr(self, 'config') and self.config:
        # 根据任务类型和模型名称获取参数配置
        if self.model_type in self.config.get('ML_model_special_params', {}):
            task_config = self.config['ML_model_special_params'][self.model_type]
            if self.model_name in task_config:
                # 从配置中提取参数名作为支持的参数列表
                supported_params = set(task_config[self.model_name].keys())
                # 排除key_description等元数据键
                supported_params = {p for p in supported_params if not p.startswith('key_')}
    else:
        # 降级方案：如果配置未加载，使用硬编码的默认参数列表
        # 注意：这仅作为降级方案，优先从配置文件读取
        supported_params = {
            'n_components', 'random_state', 'n_jobs', 'verbose'  # 示例参数
        }
    
    # 检查是否有不支持的参数
    for param_name in model_params:
        if param_name not in supported_params:
            # 警告但不中断执行
            logging.warning(f"参数 '{param_name}' 可能不被当前模型支持")
    
    # 值域检查
    # 示例：检查n_components是否为正整数
    if 'n_components' in model_params:
        n_components = model_params['n_components']
        if not isinstance(n_components, int) or n_components <= 0:
            logging.error(f"参数 'n_components' 必须是正整数，当前值: {n_components}")
            raise ValueError("参数 'n_components' 必须是正整数")
    
    # 其他参数的验证...
    
    # 验证通过
    return True
```

#### 2.3 preprocess 方法

**功能**：执行数据预处理，准备模型训练所需的特征数据。

**实现步骤**：
1. 接收输入数据和参数
2. 执行必要的预处理操作（标准化、归一化等）
3. 返回处理后的数据

**示例实现**：

```python
def preprocess(self, X: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    数据预处理方法
    
    参数:
        X (pd.DataFrame): 输入特征数据
        params (Dict[str, Any]): 预处理参数
        
    返回:
        pd.DataFrame: 处理后的特征数据
    """
    # 复制数据避免修改原始数据
    processed_X = X.copy()
    
    # 处理空值参数
    params = params or {}
    
    # 执行必要的预处理操作
    # 示例1: 检查并处理缺失值
    if processed_X.isnull().any().any():
        # 可以根据参数选择不同的填充策略
        fill_strategy = params.get('fill_strategy', 'mean')
        numeric_cols = processed_X.select_dtypes(include=[np.number]).columns
        
        if fill_strategy == 'mean':
            processed_X[numeric_cols] = processed_X[numeric_cols].fillna(processed_X[numeric_cols].mean())
        elif fill_strategy == 'median':
            processed_X[numeric_cols] = processed_X[numeric_cols].fillna(processed_X[numeric_cols].median())
        else:
            # 默认填充0
            processed_X[numeric_cols] = processed_X[numeric_cols].fillna(0)
    
    # 示例2: 标准化/归一化（如果需要）
    # 注意：有些模型（如PCA）需要标准化输入数据
    if params.get('normalize', False):
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        numeric_cols = processed_X.select_dtypes(include=[np.number]).columns
        processed_X[numeric_cols] = scaler.fit_transform(processed_X[numeric_cols])
    
    # 返回处理后的数据
    return processed_X
```

#### 2.4 train 方法

**功能**：训练模型，使用预处理后的数据拟合模型参数。

**实现步骤**：
1. 接收训练数据和参数
2. 创建模型实例并设置参数
3. 执行模型训练
4. 返回训练好的模型

**示例实现**：

```python
def train(self, X_train: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    模型训练方法
    
    参数:
        X_train (pd.DataFrame): 训练特征数据
        params (Dict[str, Any]): 模型训练参数
        
    返回:
        Any: 训练好的模型对象
    """
    # 处理空值参数
    params = params or {}
    
    # 创建模型实例
    # 这里以PCA为例，不同模型需替换相应的导入和实例化
    from sklearn.decomposition import PCA as SklearnPCA
    
    # 创建模型并设置参数
    # 只传递模型支持的参数
    model_params = {}
    for param_name, param_value in params.items():
        # 检查参数是否为模型支持的参数
        # 这里简化处理，实际应根据具体模型检查
        model_params[param_name] = param_value
    
    # 创建模型实例
    model = SklearnPCA(**model_params)
    
    # 执行训练
    try:
        model.fit(X_train)
        # 保存训练好的模型
        self.model = model
        return model
    except Exception as e:
        logging.error(f"模型训练失败: {e}")
        raise RuntimeError(f"模型训练失败: {str(e)}") from e
```

#### 2.5 postprocess 方法

**功能**：训练后的处理操作，如特征重要性提取、模型解释等。

**实现步骤**：
1. 接收训练好的模型和数据
2. 执行必要的后处理操作
3. 返回处理结果

**示例实现**：

```python
def postprocess(self, model: Any, X_train: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    训练后处理方法
    
    参数:
        model (Any): 训练好的模型对象
        X_train (pd.DataFrame): 训练数据
        params (Dict[str, Any]): 后处理参数
        
    返回:
        Dict[str, Any]: 后处理结果字典
    """
    # 处理空值参数
    params = params or {}
    
    # 初始化结果字典
    result = {}
    
    # 示例1: 提取模型属性
    # 对于PCA，可以提取方差解释率
    if hasattr(model, 'explained_variance_ratio_'):
        result['explained_variance_ratio'] = model.explained_variance_ratio_.tolist()
        result['cumulative_explained_variance'] = np.cumsum(model.explained_variance_ratio_).tolist()
    
    # 示例2: 保存中间结果或缓存
    # 根据需要实现
    
    # 示例3: 执行特征重要性分析
    # 可以调用get_feature_importance方法
    result['feature_importance'] = self.get_feature_importance(model, X_train.columns)
    
    return result
```

#### 2.6 get_feature_importance 方法

**功能**：获取特征重要性或权重信息，用于下游可视化。

**实现步骤**：
1. 接收模型和特征名列表
2. 提取特征重要性或权重
3. 格式化返回结果

**示例实现**：

```python
def get_feature_importance(self, model: Any, feature_names: List[str]) -> Dict[str, float]:
    """
    获取特征重要性或权重
    
    参数:
        model (Any): 训练好的模型对象
        feature_names (List[str]): 特征名称列表
        
    返回:
        Dict[str, float]: 特征重要性字典，键为特征名，值为重要性得分
    """
    importance_dict = {}
    
    try:
        # 根据不同模型类型提取特征重要性
        # 示例1: 对于有components_属性的模型（如PCA）
        if hasattr(model, 'components_'):
            # 计算每个特征的重要性（绝对值的平均值）
            components = model.components_
            for i, feature_name in enumerate(feature_names):
                # 检查索引是否有效
                if i < components.shape[1]:
                    importance_dict[feature_name] = np.mean(np.abs(components[:, i]))
                else:
                    importance_dict[feature_name] = 0.0
        
        # 示例2: 对于有feature_importances_属性的模型（如决策树）
        elif hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            for i, feature_name in enumerate(feature_names):
                if i < len(importances):
                    importance_dict[feature_name] = float(importances[i])
                else:
                    importance_dict[feature_name] = 0.0
        
        # 示例3: 对于有coef_属性的模型（如线性回归）
        elif hasattr(model, 'coef_'):
            coefs = model.coef_
            # 处理不同形状的coef_ (一维或二维)
            if coefs.ndim == 1:
                for i, feature_name in enumerate(feature_names):
                    if i < len(coefs):
                        importance_dict[feature_name] = float(abs(coefs[i]))
                    else:
                        importance_dict[feature_name] = 0.0
            else:
                # 对于多输出模型，取平均值
                for i, feature_name in enumerate(feature_names):
                    if i < coefs.shape[1]:
                        importance_dict[feature_name] = float(np.mean(np.abs(coefs[:, i])))
                    else:
                        importance_dict[feature_name] = 0.0
        
        # 如果无法提取重要性，返回空字典或所有特征重要性为0
        if not importance_dict:
            for feature_name in feature_names:
                importance_dict[feature_name] = 0.0
                
    except Exception as e:
        logging.error(f"提取特征重要性失败: {e}")
        # 失败时返回空的重要性字典
        for feature_name in feature_names:
            importance_dict[feature_name] = 0.0
    
    return importance_dict
```

#### 2.7 predict 方法

**功能**：使用训练好的模型进行预测。

**实现步骤**：
1. 接收新数据和预测参数
2. 执行预测操作
3. 返回预测结果

**示例实现**：

```python
def predict(self, model: Any, X: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    模型预测方法
    
    参数:
        model (Any): 训练好的模型对象
        X (pd.DataFrame): 预测输入数据
        params (Dict[str, Any]): 预测参数
        
    返回:
        pd.DataFrame: 预测结果DataFrame
    """
    # 处理空值参数
    params = params or {}
    
    # 确保模型已训练
    if model is None:
        raise ValueError("模型未训练，请先训练模型")
    
    try:
        # 根据模型类型执行预测
        # 示例1: 对于转换类模型（如降维）
        if hasattr(model, 'transform'):
            # 使用transform方法进行预测
            predictions = model.transform(X)
            
            # 为降维结果创建有意义的列名
            # 例如: 对于PCA，列名可以是'PC1', 'PC2', ...
            n_components = predictions.shape[1]
            columns = [f'component_{i+1}' for i in range(n_components)]
            
            # 转换为DataFrame返回
            return pd.DataFrame(predictions, columns=columns, index=X.index)
        
        # 示例2: 对于预测类模型
        elif hasattr(model, 'predict'):
            # 检查是否需要概率预测
            if params.get('return_proba', False) and hasattr(model, 'predict_proba'):
                predictions = model.predict_proba(X)
                # 处理概率预测结果
                if len(predictions.shape) == 1:
                    # 二分类问题
                    return pd.DataFrame({
                        'probability_class_0': 1 - predictions,
                        'probability_class_1': predictions
                    }, index=X.index)
                else:
                    # 多分类问题
                    columns = [f'probability_class_{i}' for i in range(predictions.shape[1])]
                    return pd.DataFrame(predictions, columns=columns, index=X.index)
            else:
                # 普通预测
                predictions = model.predict(X)
                return pd.DataFrame({'prediction': predictions}, index=X.index)
        
        else:
            raise ValueError("模型不支持预测或转换操作")
            
    except Exception as e:
        logging.error(f"模型预测失败: {e}")
        raise RuntimeError(f"模型预测失败: {str(e)}") from e
```

#### 2.8 save_model_artifacts 方法

**功能**：保存模型及其相关产物，支持后续加载和部署。

**实现步骤**：
1. 接收模型和保存路径
2. 序列化模型及其相关组件
3. 返回保存状态

**示例实现**：

```python
def save_model_artifacts(self, model: Any, save_path: str, params: Optional[Dict[str, Any]] = None) -> bool:
    """
    保存模型产物
    
    参数:
        model (Any): 训练好的模型对象
        save_path (str): 保存路径
        params (Dict[str, Any]): 保存参数
        
    返回:
        bool: 保存成功返回True，失败返回False
    """
    # 处理空值参数
    params = params or {}
    
    try:
        # 确保保存目录存在
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 保存模型
        import joblib
        joblib.dump(model, save_path)
        
        # 可选：保存额外信息
        # 例如，保存特征名称、编码信息等
        if params.get('save_metadata', False):
            metadata_path = save_path.replace('.pkl', '_metadata.json')
            metadata = {
                'model_type': str(type(model).__name__),
                'save_time': pd.Timestamp.now().isoformat(),
                'params': params
            }
            
            import json
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logging.info(f"模型已成功保存到: {save_path}")
        return True
        
    except Exception as e:
        logging.error(f"保存模型失败: {e}")
        return False
```

#### 2.9 get_default_metrics 方法

**功能**：获取当前任务类型的默认评估指标列表。

**实现步骤**：
1. 根据模型类型从配置或硬编码获取默认指标
2. 返回指标列表

**示例实现**：

```python
def get_default_metrics(self, model_type: str) -> List[str]:
    """
    获取默认评估指标列表
    
    参数:
        model_type (str): 模型类型，如 'classification', 'regression', 'clustering', 'dimensionality_reduction'
        
    返回:
        List[str]: 默认评估指标列表
    """
    # 定义不同任务类型的默认指标
    default_metrics_map = {
        'classification': ['accuracy', 'f1_score'],
        'regression': ['rmse', 'r2_score'],
        'clustering': ['silhouette_score'],
        'dimensionality_reduction': ['reconstruction_error', 'trustworthiness'],
        'anomaly_detection': ['precision', 'recall'],
        'transformer': []  # 转换任务可能不需要评估指标
    }
    
    # 返回对应的默认指标列表，如果没有定义则返回空列表
    metrics = default_metrics_map.get(model_type.lower(), [])
    
    # 可以选择从配置文件加载而不是硬编码
    try:
        from Utils.config_loader import load_config
        config = load_config()
        if 'ML_model_evaluation_methods' in config and model_type in config['ML_model_evaluation_methods']:
            # 从配置中提取默认指标
            config_metrics = list(config['ML_model_evaluation_methods'][model_type].keys())
            if config_metrics:
                metrics = config_metrics
    except Exception as e:
        logging.warning(f"从配置文件加载默认指标失败，使用硬编码指标: {e}")
    
    return metrics
```

#### 2.10 analyzer 方法

**功能**：分析器的核心方法，协调整个分析流程。

**实现步骤**：
1. 验证和预处理输入数据
2. 调用preprocess方法处理数据
3. 调用train方法训练模型
4. 调用postprocess方法进行后处理
5. 评估模型（如果需要）
6. 构建并返回标准格式的结果

**示例实现**：

```python
def analyzer(
    self, 
    df: pd.DataFrame, 
    learn_type: str, 
    model_type: str, 
    model: str,
    random_state: int = 42, 
    is_split: bool = True, 
    split_ratio: float = 0.2,
    feature_cols: Optional[List[str]] = None, 
    target_col: Optional[str] = None,
    metrics_list: Optional[List[str]] = None, 
    is_return_model_score: bool = True,
    feature_cols_encoding: str = "auto", 
    target_col_encoding: str = "auto",
    test_set: Optional[pd.DataFrame] = None, 
    model_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    执行完整分析流程
    
    参数:
        df (pd.DataFrame): 输入数据集
        learn_type (str): 学习类型，如 "ML"（机器学习）或 "DL"（深度学习）
        model_type (str): 模型类别，如 "classification"、"regression"、"clustering"
        model (str): 模型名称，如 "random_forest"、"xgboost"
        random_state (int): 随机种子，用于复现实验结果
        is_split (bool): 是否自动划分训练/测试集
        split_ratio (float): 测试集占比
        feature_cols (List[str]): 特征列名列表
        target_col (str): 目标列名
        metrics_list (List[str]): 评价指标列表
        is_return_model_score (bool): 是否返回模型评估得分
        feature_cols_encoding (str): 特征列编码方式
        target_col_encoding (str): 目标列编码方式
        test_set (pd.DataFrame): 外部传入的测试集
        model_params (Dict[str, Any]): 模型特定超参数
        
    返回:
        Dict[str, Any]: 包含模型、评分、数据等的结果字典
    """
    # 1. 加载和验证参数
    processed_params = self.load_params(model_params)
    self.validate_params(processed_params)
    
    # 2. 验证列是否存在
    self.validate_cols_exist(df, feature_cols, target_col)
    
    # 3. 数据编码（如果需要）
    # 对于降维任务，可能不需要对目标列进行编码
    X = df[feature_cols].copy()
    y = df[target_col].copy() if target_col and target_col in df.columns else None
    
    # 特征编码
    X_encoded, encoders = self.feature_set_encoding(X, feature_cols_encoding)
    
    # 目标编码（如果有目标列）
    y_encoded = None
    target_encoder = None
    if y is not None:
        y_encoded, target_encoder = self.target_col_encoding(y, target_col_encoding, model_type)
    
    # 4. 数据划分
    if is_split:
        X_train, X_test, y_train, y_test = self.split_data_set(
            X_encoded, y_encoded, split_ratio, random_state, model_type
        )
    else:
        X_train = X_encoded
        y_train = y_encoded
        # 使用外部测试集或全部作为训练集
        if test_set is not None:
            X_test = test_set[feature_cols].copy()
            # 对测试集应用相同的编码
            X_test = self.apply_encoding(X_test, encoders)
            y_test = test_set[target_col].copy() if target_col and target_col in test_set.columns else None
            if y_test is not None and target_encoder is not None:
                y_test = self.apply_target_encoding(y_test, target_encoder)
        else:
            X_test = X_encoded.copy()
            y_test = y_encoded
    
    # 5. 数据预处理
    X_train_processed = self.preprocess(X_train, processed_params)
    X_test_processed = self.preprocess(X_test, processed_params)
    
    # 6. 模型训练
    trained_model = self.train(X_train_processed, processed_params)
    
    # 7. 后处理
    postprocess_results = self.postprocess(trained_model, X_train_processed, processed_params)
    
    # 8. 评估模型
    model_score = {}
    if is_return_model_score:
        # 使用指定的指标或默认指标
        if not metrics_list:
            metrics_list = self.get_default_metrics(model_type)
        
        # 调用基类的evaluate_model方法或自定义评估
        if hasattr(self, 'evaluate_model'):
            model_score = self.evaluate_model(trained_model, X_test_processed, y_test, metrics_list)
    
    # 9. 构建返回结果
    result = {
        "model": trained_model,
        "model_score": model_score,
        "train_set": pd.concat([X_train, pd.DataFrame(y_train, columns=[target_col])], axis=1) if y_train is not None else X_train,
        "test_set": pd.concat([X_test, pd.DataFrame(y_test, columns=[target_col])], axis=1) if y_test is not None else X_test,
        "feature_cols": feature_cols,
        "encoding_methods": {
            "features": feature_cols_encoding,
            "target": target_col_encoding
        }
    }
    
    # 添加后处理结果
    result.update(postprocess_results)
    
    return result
```

### 3. 实现注意事项

1. **异常处理**：每个方法都应该包含适当的异常处理，记录详细的错误日志。
2. **参数校验**：始终验证输入参数的类型和值域，确保鲁棒性。
3. **数据复制**：处理数据时，始终创建副本以避免修改原始数据。
4. **日志记录**：使用logging模块记录关键操作和错误信息。
5. **返回格式**：严格按照规范的返回格式返回结果。
6. **模块导入**：对于可选依赖，使用try-except块进行导入，并提供友好的错误提示。
7. **文档字符串**：为每个方法提供完整的文档字符串，包括参数、返回值和异常说明。

### 4. 不同类型任务的特殊考虑

#### 4.1 分类任务
- 确保支持概率预测（predict_proba）
- 处理多类别情况的评估指标
- 考虑类别不平衡问题

#### 4.2 回归任务
- 使用适当的评估指标（RMSE、MAE、R²等）
- 考虑异常值对模型的影响

#### 4.3 聚类任务
- 处理无监督特性，可能没有目标列
- 使用内部评估指标（如轮廓系数）

#### 4.4 降维任务
- 关注维度转换的质量和可解释性
- 实现重构误差等特定评估指标
- 注意处理转换后的数据格式

#### 4.5 异常检测任务
- 处理不平衡数据
- 实现特定的异常评分机制

### 5. 示例完整实现

以下是一个PCA分析器的完整实现示例，展示了所有方法的集成：

```python
"""
PCA降维分析器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Cores.base_analyzer import BaseAnalyzer
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA as SklearnPCA
import joblib
import logging

logger = logging.getLogger(__name__)

class PCAAnalyzer(BaseAnalyzer):
    """
    主成分分析(PCA)降维分析器
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
    
    def load_params(self, model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """加载和处理模型参数"""
        if model_params is None:
            return {}
        
        if not isinstance(model_params, dict):
            try:
                return dict(model_params)
            except:
                return {}
        
        processed_params = model_params.copy()
        
        # 参数类型转换
        if 'n_components' in processed_params:
            try:
                processed_params['n_components'] = int(processed_params['n_components'])
            except (ValueError, TypeError):
                processed_params.pop('n_components', None)
        
        if 'random_state' in processed_params:
            try:
                processed_params['random_state'] = int(processed_params['random_state'])
            except (ValueError, TypeError):
                processed_params.pop('random_state', None)
        
        return processed_params
    
    def validate_params(self, model_params: Dict[str, Any]) -> bool:
        """验证模型参数的合法性"""
        supported_params = {
            'n_components', 'random_state', 'copy', 'whiten', 'svd_solver', 
            'tol', 'iterated_power', 'n_oversamples', 'power_iteration_normalizer'
        }
        
        # 检查不支持的参数
        for param_name in model_params:
            if param_name not in supported_params:
                logger.warning(f"参数 '{param_name}' 可能不被PCA模型支持")
        
        # 参数范围检查
        if 'n_components' in model_params:
            n_components = model_params['n_components']
            if not isinstance(n_components, int) or n_components <= 0:
                logger.error(f"参数 'n_components' 必须是正整数，当前值: {n_components}")
                raise ValueError("参数 'n_components' 必须是正整数")
        
        return True
    
    def preprocess(self, X: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """数据预处理"""
        processed_X = X.copy()
        params = params or {}
        
        # 处理缺失值
        if processed_X.isnull().any().any():
            numeric_cols = processed_X.select_dtypes(include=[np.number]).columns
            processed_X[numeric_cols] = processed_X[numeric_cols].fillna(processed_X[numeric_cols].mean())
        
        # 默认标准化数据（PCA对数据尺度敏感）
        if params.get('normalize', True):
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            numeric_cols = processed_X.select_dtypes(include=[np.number]).columns
            processed_X[numeric_cols] = scaler.fit_transform(processed_X[numeric_cols])
        
        return processed_X
    
    def train(self, X_train: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> Any:
        """训练PCA模型"""
        params = params or {}
        
        # 创建模型实例
        model = SklearnPCA(**params)
        
        try:
            model.fit(X_train)
            self.model = model
            return model
        except Exception as e:
            logger.error(f"PCA模型训练失败: {e}")
            raise RuntimeError(f"PCA模型训练失败: {str(e)}") from e
    
    def postprocess(self, model: Any, X_train: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """训练后处理"""
        result = {}
        
        # 提取方差解释率
        if hasattr(model, 'explained_variance_ratio_'):
            result['explained_variance_ratio'] = model.explained_variance_ratio_.tolist()
            result['cumulative_explained_variance'] = np.cumsum(model.explained_variance_ratio_).tolist()
        
        # 提取特征重要性
        if hasattr(model, 'components_') and X_train.shape[1] > 0:
            result['feature_importance'] = self.get_feature_importance(model, X_train.columns)
        
        return result
    
    def get_feature_importance(self, model: Any, feature_names: List[str]) -> Dict[str, float]:
        """获取特征重要性（PCA组件权重）"""
        importance_dict = {}
        
        try:
            if hasattr(model, 'components_'):
                components = model.components_
                for i, feature_name in enumerate(feature_names):
                    if i < components.shape[1]:
                        # 使用绝对值的平均值作为重要性
                        importance_dict[feature_name] = float(np.mean(np.abs(components[:, i])))
                    else:
                        importance_dict[feature_name] = 0.0
            else:
                for feature_name in feature_names:
                    importance_dict[feature_name] = 0.0
        except Exception as e:
            logger.error(f"提取PCA特征重要性失败: {e}")
            for feature_name in feature_names:
                importance_dict[feature_name] = 0.0
        
        return importance_dict
    
    def predict(self, model: Any, X: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """使用PCA模型进行降维转换"""
        if model is None:
            raise ValueError("模型未训练，请先训练模型")
        
        try:
            # 执行转换
            transformed_data = model.transform(X)
            
            # 创建有意义的列名
            n_components = transformed_data.shape[1]
            columns = [f'PC{i+1}' for i in range(n_components)]
            
            return pd.DataFrame(transformed_data, columns=columns, index=X.index)
        except Exception as e:
            logger.error(f"PCA转换失败: {e}")
            raise RuntimeError(f"PCA转换失败: {str(e)}") from e
    
    def save_model_artifacts(self, model: Any, save_path: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """保存模型产物"""
        try:
            # 确保保存目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 保存模型
            joblib.dump(model, save_path)
            
            logger.info(f"PCA模型已成功保存到: {save_path}")
            return True
        except Exception as e:
            logger.error(f"保存PCA模型失败: {e}")
            return False
    
    def get_default_metrics(self, model_type: str) -> List[str]:
        """获取降维任务的默认评估指标"""
        return ['reconstruction_error', 'explained_variance_ratio']
    
    def analyzer(
        self, 
        df: pd.DataFrame, 
        learn_type: str, 
        model_type: str, 
        model: str,
        random_state: int = 42, 
        is_split: bool = True, 
        split_ratio: float = 0.2,
        feature_cols: Optional[List[str]] = None, 
        target_col: Optional[str] = None,
        metrics_list: Optional[List[str]] = None, 
        is_return_model_score: bool = True,
        feature_cols_encoding: str = "auto", 
        target_col_encoding: str = "auto",
        test_set: Optional[pd.DataFrame] = None, 
        model_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行PCA降维分析"""
        # 加载和验证参数
        processed_params = self.load_params(model_params)
        self.validate_params(processed_params)
        
        # 设置随机种子
        if 'random_state' not in processed_params:
            processed_params['random_state'] = random_state
        
        # 验证列存在性
        self.validate_cols_exist(df, feature_cols, target_col)
        
        # 准备数据
        X = df[feature_cols].copy()
        
        # 数据编码
        X_encoded, encoders = self.feature_set_encoding(X, feature_cols_encoding)
        
        # 数据划分
        if is_split:
            X_train, X_test = self.split_data_set(X_encoded, None, split_ratio, random_state, model_type)
        else:
            X_train = X_encoded
            X_test = test_set[feature_cols].copy() if test_set is not None else X_encoded
        
        # 数据预处理
        X_train_processed = self.preprocess(X_train, processed_params)
        X_test_processed = self.preprocess(X_test, processed_params)
        
        # 模型训练
        trained_model = self.train(X_train_processed, processed_params)
        
        # 后处理
        postprocess_results = self.postprocess(trained_model, X_train_processed, processed_params)
        
        # 评估模型
        model_score = {}
        if is_return_model_score:
            if not metrics_list:
                metrics_list = self.get_default_metrics(model_type)
            
            # 计算评估指标
            for metric in metrics_list:
                if metric == 'reconstruction_error':
                    # 计算重构误差
                    X_reduced = trained_model.transform(X_test_processed)
                    X_reconstructed = trained_model.inverse_transform(X_reduced)
                    reconstruction_error = np.mean(np.square(X_test_processed - X_reconstructed))
                    model_score['reconstruction_error'] = reconstruction_error
                elif metric == 'explained_variance_ratio':
                    # 记录方差解释率
                    if hasattr(trained_model, 'explained_variance_ratio_'):
                        model_score['explained_variance_ratio'] = float(np.sum(trained_model.explained_variance_ratio_))
        
        # 构建返回结果
        result = {
            "model": trained_model,
            "model_score": model_score,
            "train_set": X_train,
            "test_set": X_test,
            "feature_cols": feature_cols,
            "encoding_methods": {
                "features": feature_cols_encoding,
                "target": target_col_encoding
            }
        }
        
        # 添加后处理结果
        result.update(postprocess_results)
        
        return result
```

通过遵循以上实现指南，您可以创建功能完整、鲁棒性强的底层处理器类，确保与系统的其他部分正确集成，并提供一致的接口和行为。

## 异常处理

若必填参数为空，记录 ERROR 日志并抛出 ValueError。
推荐捕获异常并做统一错误响应处理。

```
if df is None or df.empty:
    logger.error("Required parameter 'df' is None or empty.")
    raise ValueError("Parameter 'df' cannot be None or empty.")
```


> ✅ 架构图示意：调用方 → `DataAnalysisUpgrade` → 主工厂 → 子工厂 → 策略器 → 具体分析器 → 执行并返回结果

---

## 🔁 传参与执行流程详解

### 1. 调用初始化与参数校验

调用方通过实例化 `DataAnalysisUpgrade` 创建分析器对象，并传入以下关键参数：

- `learn_type`: 学习类型（如 `"ML"`）
- `model_type`: 任务类型（如 `"classification"`）
- `model`: 模型名称（如 `"logistic_regression"`）
- `data`: 输入数据集
- 其他可选参数（超参、配置路径等）

## 执行流程：

1. 实例化时调用 `__init__()` 方法。
2. 使用 `Utils/data_validator.py` 进行空值与格式校验。
   - 若校验失败 → 记录日志（`Utils/logger.py`）→ 抛出异常终止流程。

---

### 2. 主工厂路由（`main_factory.py`）

调用 `analyze()` 方法后，进入主工厂 `MainFactory.processing_selector()`，根据 `learn_type` 决定分支：

| `learn_type` | 工厂类             | 状态       |
|-------------|--------------------|------------|
| `ML`        | `MachineLearningFactory` | ✅ 已实现 |
| `DL`        | `DeepLearningFactory`    | ⚠️ 预留，当前未启用 |

> 🧭 路由逻辑由 `Factory/main_factory.py` 实现，确保学习路径的正确分发。

---

### 3. 任务工厂创建（`ml_factory.py`）

`MachineLearningFactory` 接收 `model_type` 参数，进一步选择对应的任务工厂和策略类：

| `model_type`              | 工厂模块         | 对应策略类（Strategy）                     |
|--------------------------|------------------|-------------------------------------------|
| `classification`         | 分类任务工厂     | `classification_strategy.ClassificationStrategy` |
| `regression`             | 回归任务工厂     | `regression_strategy.RegressionStrategy`         |
| `clustering`             | 聚类任务工厂     | `clustering_strategy.ClusteringStrategy`         |
| `dimensionality_reduction` | 降维任务工厂   | `dimensionality_reduction_strategy.DimensionalityReductionStrategy` |
| `anomaly_detection`      | 异常检测任务工厂 | `pre_detection_strategy.PreDetectionStrategy`|
|`transformer`| 变换任务工厂|  `transformer_strategy.TransformerStrategy`|

> 💡 每个任务工厂不仅负责创建分析器，还绑定对应的策略类，实现“行为+对象”的统一管理。

---

### 4. 模型分析器实例化（`Tasks/` 目录）

任务工厂根据 `model` 名称查找 `model_analysis.json` 配置文件（由 `Utils/config_loader.py` 加载），校验并匹配具体模型实现类。

#### 示例：分类任务
当 `model_type="classification"` 且 `model="logistic_regression"` 时：
- 加载 `Tasks/classification/analyzers/logistic_regression.py` 中的 `LogisticRegressionAnalyzer`
- 该类继承自 `Cores/base_analyzer.py` 的 `BaseAnalyzer`

> ✅ 所有分析器均实现统一接口（如 `.train()`, `.evaluate()`），保证流程一致性。

#### 支持的模型类型

| 任务类型                  | 支持模型（`model` 名）                                                                 |
|--------------------------|----------------------------------------------------------------------------------------|
| 分类 (`classification`)   | logistic_regression, decision_tree, random_forest, svc, knn, xgboost                   |
| 回归 (`regression`)       | linear_regression, decision_tree, random_forest, xgboost                                |
| 聚类 (`clustering`)       | kmeans, mean_shift, agglomerative                                                      |
| 降维 (`dimensionality_reduction`) | pca, tsne, umap                                                              |
| 异常检测 (`anomaly_detection`) | isolation_forest, one_class_svm, autoencoder                                       |
| 数据转换 (`transformer`)  | scaler (StandardScaler, MinMaxScaler), encoder (OneHotEncoder)                          |

> 📁 所有具体分析器位于 `Tasks/{task_type}/analyzers/` 下，结构清晰，易于维护。

---

### 5. 策略控制执行（`Strategy/` 目录）

每个任务类型绑定一个策略类（继承自 `Cores/base_strategy.py`），通过 `analysis_context.py` 上下文执行流程控制。

#### 执行流程由 `Strategy` 控制：
1. **数据预处理**：调用 `transformer` 分析器进行标准化或编码
2. **模型训练**：调用 `.train()` 方法
3. **模型评估**：调用 `.evaluate()` 并获取指标

> 🔄 策略类确保不同任务类型的执行顺序一致，提升系统稳定性。

---

### 6. 评估指标获取（`Evaluation/` 模块）

评估指标从 `model_analysis.json` 配置中读取，并由对应模块计算：

| `model_type`                  | 评估模块                         |
|------------------------------|----------------------------------|
| `classification`             | `Evaluation/classification_metrics.py` |
| `regression`                 | `Evaluation/regression_metrics.py`     |
| `clustering`                 | `Evaluation/clustering_metrics.py`     | 
| `dimensionality_reduction`   | `Evaluation/dimensionality_reduction_metrics.py`| 
| `anomaly_detection`          | `Evaluation/anomaly_detection_metrics.py`  |
注意：具体指标内容查看配置文件
---

### 7. 结果封装与返回（`Cores/analysis_result.py`）

最终结果由 `AnalysisResult` 类统一封装，返回标准字典结构：
```python

{
   "model": object,
   "model_score":{"{metric_name}":{metric_value}
   ,...
   },
   train_set:pd.DataFrame,
   test_set:pd.DataFrame,
   feature_cols:list[str],
   encoding_methods:dict[str,str] 
}


```


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
| 异常检测 | 添加异常检测任务类型支持（占位符，尚未实现）|

## 使用示例

```
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