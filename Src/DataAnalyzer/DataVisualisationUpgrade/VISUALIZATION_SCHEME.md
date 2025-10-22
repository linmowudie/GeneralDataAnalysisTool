# DataVisualisationUpgrade 可视化方案文档

## 1. 概述

DataVisualisationUpgrade 模块采用工厂模式和策略模式相结合的设计架构，为不同类型的机器学习模型提供定制化的可视化功能。该模块支持分类、回归、聚类和变换器等多种任务类型的图表生成。

## 2. 整体架构

模块采用分层设计，包含以下核心组件：

1. **包初始化** (`__init__.py`) - 统一暴露接口，简化导入
2. **可视化工厂** (`factory.py`) - 根据模型类型返回对应可视化模块
3. **策略调度器** (`strategy.py`) - 自动选择最佳图表类型（如分类任务默认用混淆矩阵）
4. **任务特定策略** - 按任务类型组织的策略实现：
   - 分类任务 (`classification/`) - 包含逻辑回归、决策树、KNN、随机森林、XGBoost、SVM等模型的专用可视化
   - 回归任务 (`regression/`) - 包含线性回归、决策树回归、随机森林回归等模型的专用可视化
   - 聚类任务 (`clustering/`) - 包含KMeans、MeanShift、层次聚类等模型的专用可视化
   - 变换器任务 (`transformer/`) - 包含标准化、PCA、t-SNE、UMAP等变换器的专用可视化
5. **通用图表** (`common/`) - 所有模型共享的基础图表类型
6. **工具函数库** (`utils/`) - 底层可复用的绘图逻辑
7. **异常处理** (`exceptions.py`) - 自定义异常类，便于上层系统捕获和处理
8. **配置文件** (`../Configs/model_visualization.json`) - 定义模型支持的图表类型映射

## 3. 绘图逻辑流程

### 3.1 初始化阶段

1. 用户通过 [DataVisualization](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/ModuleInterfaces/data_visualization_upgrade_interfaces.py#L17-L108) 接口类传入参数：
   - `model_name`: 模型名称
   - `model`: 模型对象
   - `task_list`: 任务列表
   - `data_dict`: 数据字典
   - `label_style`: 标签样式
   - `plot_style`: 绘图样式
   - `font_style`: 字体样式
   - `interactive`: 是否生成交互式图表

2. [DataVisualization](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/ModuleInterfaces/data_visualization_upgrade_interfaces.py#L17-L108) 接口类根据模型名称确定任务类型，并构建参数字典

### 3.2 策略调度阶段

3. [Strategy](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/DataVisualisationUpgrade/strategy.py) 调度器根据任务类型自动选择最佳图表类型（如分类任务默认用混淆矩阵）

4. [VisualizationFactory](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/DataVisualisationUpgrade/visualization_factory.py) 根据模型名称和任务类型创建相应的可视化策略实例

5. 工厂类根据以下逻辑选择策略：
   - 首先检查是否为通用图表类型，如果是则使用通用图表策略
   - 否则根据任务类型（classification/regression/clustering/transformer）和模型名称选择特定策略

### 3.3 参数验证阶段

6. 策略实例调用 [validate_params()](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/DataVisualisationUpgrade/base_visualization.py#L34-L37) 方法验证参数完整性
   - 检查必需参数是否存在
   - 验证数据格式是否正确
   - 确认模型对象是否包含必要的属性

### 3.4 图表生成阶段

7. 根据 [interactive](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/ModuleInterfaces/data_visualization_upgrade_interfaces.py#L42-L42) 参数决定调用 [generate_static_charts()](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/DataVisualisationUpgrade/base_visualization.py#L44-L51) 或 [generate_interactive_charts()](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/DataVisualisationUpgrade/base_visualization.py#L53-L60) 方法

8. 策略实现具体的图表绘制逻辑：
   - 从参数中提取所需数据
   - 使用 matplotlib 或 plotly 绘制图表
   - 应用样式设置（字体、样式等）
   - 返回图表对象字典

## 4. 参数传递机制

### 4.1 参数结构

参数以字典形式在各组件间传递，包含以下主要字段：

```python
params = {
    "model_name": str,           # 模型名称
    "model": object,             # 模型对象
    "task_list": List[str],      # 任务列表
    "label_style": str,          # 标签样式
    "plot_style": str,           # 绘图样式
    "font_style": str,           # 字体样式
    # 数据相关参数，来自 data_dict
    "X_train": array,            # 训练特征
    "y_train": array,            # 训练标签
    "X_test": array,             # 测试特征
    "y_test": array,             # 测试标签
    # 任务特定参数
    # ... 其他参数
}
```

### 4.2 参数验证

每种策略都必须实现 [validate_params()](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/DataVisualisationUpgrade/base_visualization.py#L34-L37) 方法，确保：
- 必需参数存在
- 数据格式正确
- 模型对象包含必要属性

### 4.3 参数使用

策略在生成图表时从参数字典中提取所需数据：
- 通用参数：样式设置等
- 数据参数：训练/测试数据
- 模型参数：从模型对象中提取参数（如系数、特征重要性等）

### 4.4 工具函数调用

在底层绘图实现中，策略可以调用 [utils/](file:///E:/ProjectCode/GeneralDataAnalysisTool/Src/DataAnalyzer/DataVisualisationUpgrade/utils) 目录下的工具函数来复用常见的绘图逻辑，如绘制混淆矩阵、ROC曲线等。

## 5. 任务类型支持

### 5.1 分类任务 (classification)

支持逻辑回归、决策树、随机森林、K近邻、XGBoost、SVM等模型的可视化：
- 混淆矩阵
- ROC曲线
- 精确率-召回率曲线
- 校准曲线
- 特征系数/重要性图
- SHAP解释图
- 部分依赖图
- 决策边界图
- 支持向量分布图
- 树结构图

### 5.2 回归任务 (regression)

支持线性回归、决策树回归、随机森林回归等模型的可视化：
- 实际值vs预测值图
- 残差图
- Q-Q图
- Cook距离图
- 杠杆图
- 回归线图
- 置信区间图
- 预测路径图

### 5.3 聚类任务 (clustering)

支持KMeans、MeanShift、层次聚类等模型的可视化：
- 聚类散点图
- 聚类柱状图
- 3D投影图
- 轮廓分析图
- 肘部法图
- t-SNE/UMAP投影图
- 密度分布图
- 簇中心图
- 树状图（dendrogram）
- 簇合并过程图

### 5.4 变换器任务 (transformer)

支持标准化、PCA、t-SNE、UMAP等变换器的可视化：
- 变换前后分布图
- 缩放特征箱线图
- 缺失值矩阵
- 主成分解释方差图
- 生物图
- 载荷图
- 3D投影图
- 词云图
- 网络图
- 仪表盘图
- 桑基图

### 5.5 通用图表 (common)

所有模型都支持的基础图表类型：
- 散点图
- 折线图
- 柱状图
- 直方图
- 箱线图
- 小提琴图
- 热力图
- 成对图
- 密度等高线图
- 气泡图
- 面积图
- 阶梯图
- 山脊图
- Joy Plot
- K线图