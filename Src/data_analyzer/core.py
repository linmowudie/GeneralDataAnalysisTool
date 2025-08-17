"""
Src/data_analyzer/core.py
数据处理核心引擎模块

该模块定义了 DataProcessingEngine 类，作为整个数据处理流程的统一入口与协调中心。
通过封装数据导入、清洗、分析、可视化及报告生成等阶段，提供简洁、流畅的接口供外部调用。
引擎采用状态管理方式维护各阶段中间结果，确保流程有序执行，并集成日志系统以支持过程追踪与问题排查。

主要特性：
- 流程化设计：支持从原始数据到分析结果的端到端处理
- 阶段解耦：各处理阶段由独立模块实现，核心引擎负责调度
- 状态管理：自动维护导入、清洗、分析等中间数据状态
- 异常处理：每阶段均包含完善的错误捕获与日志记录
- 易用性：对外暴露简洁方法，隐藏底层复杂性

使用示例：
    engine = DataProcessingEngine()
    engine.import_data("data.csv", "csv")
    engine.clean_data("auto", [])
    engine.analyze_data(model=RandomForestClassifier())
"""
from . import data_import
from . import data_analysis
from . import data_cleaning
from . import data_visualization
from . import reporting
from . import log_setting

import logging
import random
import pandas as pd
from pathlib import Path
from typing import Optional, Any, Union, List
from matplotlib.figure import Figure  # 用于类型提示
from typing import Dict


class DataProcessingEngine:
    """
    数据处理引擎类
    提供统一接口供外部调用，封装完整的数据处理流程
    重构后：所有配置参数由各阶段方法本地传入，构造函数仅做基础初始化
    """

    def __init__(self):
        # 初始化中间数据状态
        self.imported_data: Optional[pd.DataFrame] = None
        self.cleaned_data: Optional[pd.DataFrame] = None
        self.analyzed_data: Optional[dict] = None
        self.visualized_plot: Optional[Dict[str, Figure]] = None
        self.report_data: Optional[Dict] = None

        # 初始化日志
        self.logger = log_setting.setup_logging()
        self.logger.debug("DataProcessingEngine 初始化完成，等待执行数据处理任务。")

    def import_data(
        self,
        resource_path: Union[Path, str],
        resource_type: str,
        db_connection_string: Optional[str] = None,
        query: Optional[str] = None,
        is_database: bool = False
    ) -> None:
        """
        导入数据，支持文件或数据库表

        Args:
            resource_path: 文件路径或资源标识
            resource_type: 资源类型，如 'csv', 'excel', 'json', 'db'
            db_connection_string: 数据库连接字符串（仅用于数据库）
            query: SQL 查询语句（仅用于数据库）
            is_database: 是否为数据库源
        """
        self.logger.info("core: 开始导入数据")
        try:
            # 只有在是数据库源时才需要数据库连接字符串
            if is_database and db_connection_string is None:
                self.logger.error("数据库连接字符串不能为空")
                raise ValueError("数据库连接字符串不能为空")

            importer = data_import.DataImport(
                file_resource=resource_path,
                resource_type=resource_type,
                db_connection_string=db_connection_string,
                is_database=is_database
            )
            self.imported_data = importer.import_data(query=query)

            if self.imported_data is not None:
                self.logger.info("数据导入成功，共 %d 行，%d 列", self.imported_data.shape[0], self.imported_data.shape[1])

        except Exception as e:
            error_msg = f"数据导入失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

        self.logger.info("core: 数据导入完成")

    def clean_data(
        self,
        select_mode: str,
        params_list: List[str],
        is_freedom_params: bool = False
    ) -> None:
        """
        数据清洗阶段

        Args:
            select_mode: 清洗模式（如 'auto', 'manual'）
            params_list: 参数列表，如要处理的列名或规则
            is_freedom_params: 是否为自由格式参数
        """
        self.logger.info("core: 开始数据清洗")

        if self.imported_data is None:
            error_msg = "请先导入数据"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            cleaner = data_cleaning.CleanDataMode(
                self.imported_data,
                select_mode,
                params_list,
                is_freedom_params
            )
            self.cleaned_data = cleaner.clean_data()
            self.logger.info("数据清洗完成，清洗后数据形状: %s", str(self.cleaned_data.shape))

        except Exception as e:
            error_msg = f"数据清洗失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

        self.logger.info("core: 数据清洗完成")

    def analyze_data(
        self,
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
    ) -> None:
        """
        数据分析阶段

        Args:
            model: 机器学习模型实例（如 sklearn 模型）
            random_state: 随机种子
            is_split: 是否划分训练/测试集
            split_ratio: 训练集比例
            feature_cols: 特征列名列表
            target_col: 目标列名
            is_return_model_param: 是否返回模型超参
            metrics_list: 评估指标列表，如 ['accuracy', 'f1']
            is_return_model_score: 是否返回模型评分
            is_return_training_set: 是否返回训练集
            is_return_model_predicting_set: 是否返回预测结果
            feature_cols_encoding: 特征列编码映射
            target_col_encoding: 标签列编码映射
            test_set: 外部测试集（可选）
            model_params: 模型参数字典，用于覆盖默认参数
        """
        self.logger.info("core: 开始数据分析")

        if self.cleaned_data is None:
            error_msg = "请先进行数据清洗"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            analyzer = data_analysis.DataAnalyzer(
                df = self.cleaned_data,
                model=model,
                random_state=random_state,
                is_split=is_split,
                split_ratio=split_ratio,
                feature_cols=feature_cols,
                target_col=target_col,
                is_return_model_param=is_return_model_param,
                metrics_list=metrics_list,
                is_return_model_score=is_return_model_score,
                is_return_training_set=is_return_training_set,
                is_return_model_predicting_set=is_return_model_predicting_set,
                feature_cols_encoding=feature_cols_encoding,
                target_col_encoding=target_col_encoding,
                test_set=test_set,
                model_params=model_params
            )
            result = analyzer.analyze()
            self.analyzed_data = result  # 可根据 analyze 返回内容调整
            self.logger.info("数据分析完成")


        except Exception as e:
            error_msg = f"数据分析失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

        self.logger.info("core: 数据分析完成")

    def visualize_data(self, param_dict: Optional[Dict[str, Any]] = None) -> None:
        """
        数据可视化阶段

        Args:
            param_dict: 可视化参数字典，如果为None则使用分析结果中的默认参数
        """
        self.logger.info("core: 开始数据可视化")

        if self.analyzed_data is None:
            error_msg = "请先进行数据分析"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # 如果没有提供参数字典，则根据分析结果构建默认参数
            if param_dict is None:
                param_dict = self._build_default_visualization_params()
            
            # 检查是否至少有特征数据
            if 'feature' not in param_dict or param_dict['feature'] is None:
                self.logger.warning("没有足够的数据进行可视化，跳过可视化步骤")
                self.visualized_plot = {}
                return
            
            visualizer = data_visualization.DataVisualization(param_dict)
            self.visualized_plot = visualizer.plot_chart()
            self.logger.info("数据可视化完成")

        except Exception as e:
            error_msg = f"数据可视化失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.visualized_plot = {}  # 确保即使失败也有默认值
            raise ValueError(error_msg) from e
        
        self.logger.info("core: 数据可视化完成")

    def _build_default_visualization_params(self) -> Dict[str, Any]:
        """
        根据分析结果构建默认的可视化参数
        """
        # 检查是否有分析数据
        if not self.analyzed_data:
            raise ValueError("没有可用的分析数据用于可视化")
        
        # 从分析结果中提取必要信息
        trained_model = self.analyzed_data.get('trained_model')
        task_type = self.analyzed_data.get('task_type', 'unknown')
        
        # 构建默认参数字典
        param_dict = {
            "task_type": task_type,
            "model_name": trained_model.__class__.__name__.lower() if trained_model else "unknown",
        }
        
        # 添加可用的数据
        if 'X_train' in self.analyzed_data and self.analyzed_data['X_train'] is not None:
            param_dict['feature'] = self.analyzed_data['X_train']
        elif 'X_test' in self.analyzed_data and self.analyzed_data['X_test'] is not None:
            param_dict['feature'] = self.analyzed_data['X_test']
            
        if 'y_train' in self.analyzed_data and self.analyzed_data['y_train'] is not None:
            param_dict['target'] = self.analyzed_data['y_train']
        elif 'y_test' in self.analyzed_data and self.analyzed_data['y_test'] is not None:
            param_dict['target'] = self.analyzed_data['y_test']
            
        if 'predictions' in self.analyzed_data and self.analyzed_data['predictions'] is not None:
            param_dict['predict'] = self.analyzed_data['predictions']
            
        return param_dict

    def generate_report(self) -> None:
        """
        生成分析报告
        """
        self.logger.info("core: 开始生成报告")

        try:
            # 准备报告数据
            model_params = self.analyzed_data.get('model_params') if self.analyzed_data else None
            model_scores = self.analyzed_data.get('scores') if self.analyzed_data else None
            model_predictions = self.analyzed_data.get('predictions') if self.analyzed_data else None
            
            report_generator = reporting.Report(
                model_params=model_params,
                model_scores=model_scores,
                visualizations=self.visualized_plot,
                model_predictions=model_predictions
            )
            
            self.report_data = report_generator.return_report()
            self.logger.info("分析报告生成完成")

        except Exception as e:
            error_msg = f"报告生成失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
        
        self.logger.info("core: 报告生成完成")

    def get_report(self) -> Optional[Dict]:
        """
        获取生成的报告数据

        Returns:
            报告数据字典或None（如果尚未生成报告）
        """
        return self.report_data

    def run_complete_process(
        self,
        import_params: Dict[str, Any],
        clean_params: Dict[str, Any],
        analyze_params: Dict[str, Any],
        visualize_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        运行完整的数据处理流程

        Args:
            import_params: 数据导入参数
            clean_params: 数据清洗参数
            analyze_params: 数据分析参数
            visualize_params: 数据可视化参数（可选）

        Returns:
            包含所有处理结果的字典
        """

        self.logger.info("core: 开始完整数据处理流程")
        try:
            # 数据导入
            self.import_data(**import_params)
            
            # 数据清洗
            self.clean_data(**clean_params)
            
            # 数据分析
            self.analyze_data(**analyze_params)
            
            # 数据可视化（可选）
            if visualize_params is not None:
                self.visualize_data(visualize_params)
            else:
                self.visualize_data()
                
            # 生成报告
            self.generate_report()
            
            # 返回完整结果
            result = {
                "imported_data": self.imported_data,
                "cleaned_data": self.cleaned_data,
                "analyzed_data": self.analyzed_data,
                "visualized_plot": self.visualized_plot,
                "report": self.report_data
            }
            
            self.logger.info("完整数据处理流程执行完成")
            return result
            
        except Exception as e:
            error_msg = f"完整数据处理流程执行失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
