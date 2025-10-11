"""
Src/DataAnalyzer/core.py
数据处理核心引擎模块

该模块提供数据处理的完整流程，包括数据导入、清洗、分析、可视化和报告生成。
通过统一的接口协调各个子模块的工作，实现端到端的数据处理能力。
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Any, Union
import sys
import os
from pathlib import Path
import pickle
from datetime import datetime


# 添加项目根目录到Python路径中
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入各个子模块的接口
from .ModuleInterfaces import (
    data_import,
    data_cleaning,
    data_analysis,
    data_visualization
)
from .reporter import Report
from .TempStorage.manager import TempStorageManager

# 配置后端日志
from .Configs.log_setting import get_component_logger
backend_logger = get_component_logger('backend', 'core')

class DataProcessingEngine:
    """
    数据处理核心引擎类
    
    该类封装了完整的数据处理流程，包括：
    1. 数据导入 (import_data)
    2. 数据清洗 (clean_data)
    3. 数据分析 (analyze_data)
    4. 数据可视化 (visualize_data)
    5. 报告生成 (generate_report)
    
    各阶段处理结果会自动保存到临时存储中，支持断点续处理。
    """
    
    def __init__(self, auto_cleanup: bool = True):
        """
        初始化数据处理引擎
        
        Args:
            auto_cleanup: 是否在初始化时自动清理临时存储中的旧文件
        """
        self.logger = backend_logger
        self.logger.info("core: 初始化数据处理引擎")
        
        # 初始化各阶段数据存储
        self.imported_data: Optional[pd.DataFrame] = None
        self.cleaned_data: Optional[pd.DataFrame] = None
        self.analyzed_data: Optional[Dict[str, Any]] = None
        self.visualized_plot: Optional[Dict[str, Any]] = None
        self.report_data: Optional[Dict[str, Any]] = None
        
        # 记录最后导入的文件名
        self._last_imported_file: Optional[str] = None
        
        # 步骤状态管理
        self.completed_steps: List[str] = []  # 已完成的步骤
        self.locked_steps: List[str] = []     # 已锁定的步骤
        
        # 初始化临时存储管理器
        self.temp_storage = TempStorageManager(auto_cleanup=auto_cleanup)
        
        # 初始化自动提取模型标志
        self.auto_extract_model = False
        
        self.logger.info("core: 数据处理引擎初始化完成")

    def mark_step_completed(self, step: str) -> None:
        """
        标记步骤为已完成
        
        Args:
            step: 步骤名称
        """
        if step not in self.completed_steps:
            self.completed_steps.append(step)
            self.logger.debug(f"步骤 {step} 标记为已完成")

    def lock_step(self, step: str) -> None:
        """
        锁定步骤
        
        Args:
            step: 步骤名称
        """
        if step not in self.locked_steps:
            self.locked_steps.append(step)
            self.logger.debug(f"步骤 {step} 已锁定")

    def reset_step_and_following(self, step: str) -> None:
        """
        重置步骤及其后续步骤
        
        Args:
            step: 步骤名称
        """
        step_order = ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report']
        step_index = step_order.index(step) if step in step_order else -1
        
        if step_index != -1:
            # 解锁当前步骤及后续所有步骤
            steps_to_unlock = step_order[step_index:]
            self.locked_steps = [s for s in self.locked_steps if s not in steps_to_unlock]
            
            # 移除当前步骤及后续步骤的完成状态
            steps_to_remove = step_order[step_index:]
            self.completed_steps = [s for s in self.completed_steps if s not in steps_to_remove]
            
            # 根据步骤类型清理数据
            for step_to_reset in steps_to_remove:
                self._clear_step_data(step_to_reset)
            
            self.logger.info(f"已重置步骤 {step} 及后续步骤")

    def _clear_step_data(self, step: str) -> None:
        """
        清除特定步骤的数据
        
        Args:
            step: 步骤名称
        """
        if step == 'import':
            self.imported_data = None
            # 清理导入的临时数据
            self.temp_storage.clear_stage_data('imported')
        elif step == 'cleaning':
            self.cleaned_data = None
            # 清理清洗的临时数据
            self.temp_storage.clear_stage_data('cleaned')
        elif step == 'analysis':
            self.analyzed_data = None
            # 清理分析的临时数据
            self.temp_storage.clear_stage_data('analyzed')
        elif step == 'visualization':
            self.visualized_plot = None
            # 清理可视化的临时数据
            self.temp_storage.clear_stage_data('visualized')
        elif step == 'report':
            self.report_data = None

    def get_step_status(self) -> Dict[str, Any]:
        """
        获取步骤状态
        
        Returns:
            Dict: 包含已完成步骤和已锁定步骤的字典
        """
        return {
            'completed_steps': self.completed_steps,
            'locked_steps': self.locked_steps
        }

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
                # 保存导入的数据到临时存储
                self.temp_storage.save_data(self.imported_data, 'imported', 'imported_data.pkl')
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
        is_freedom_params: bool = False,
        target_col: Optional[str] = None
    ) -> None:
        """
        数据清洗阶段

        Args:
            select_mode: 清洗模式（如 'auto', 'manual'）
            params_list: 参数列表，如要处理的列名或规则
            is_freedom_params: 是否为自由格式参数
            target_col: 目标列名，用于分类任务中的字符串目标编码
        """
        self.logger.info("core: 开始数据清洗")

        # 如果没有导入的数据，尝试从临时存储加载
        if self.imported_data is None:
            self.imported_data = self.temp_storage.load_data('imported', 'imported_data.pkl')
            if self.imported_data is None:
                error_msg = "请先导入数据"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        try:
            cleaner = data_cleaning.CleanDataMode(
                self.imported_data,
                select_mode,
                params_list,
                is_freedom_params,
                target_col
            )
            self.cleaned_data = cleaner.clean_data()
            
            # 保存清洗后的数据到临时存储
            self.temp_storage.save_data(self.cleaned_data, 'cleaned', 'cleaned_data.pkl')
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
    ) -> Dict[str, Any]:
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

        # 如果没有清洗的数据，尝试从临时存储加载
        if self.cleaned_data is None:
            self.cleaned_data = self.temp_storage.load_data('cleaned', 'cleaned_data.pkl')
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
            
            # 保存分析结果到临时存储
            self.temp_storage.save_data(self.analyzed_data, 'analyzed', 'analyzed_data.pkl')
            self.logger.info("数据分析完成")


        except Exception as e:
            error_msg = f"数据分析失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

        # 检查是否需要自动提取模型
        if self.auto_extract_model:
            try:
                self._extract_model(result)
            except Exception as e:
                self.logger.warning(f"自动提取模型失败: {e}")

        self.logger.info("core: 数据分析完成")
        return result

    def _extract_model(self, result: Dict[str, Any]) -> None:
        """
        自动提取并保存训练好的模型到自动保存目录
        
        :param result: 数据分析结果
        """
        try:
            
            
            # 确保ModelOutput/自动保存目录存在
            model_output_dir = Path(__file__).parent.parent.parent / "ModelOutput" / "自动保存"
            model_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 获取模型名称
            trained_model = result.get('trained_model')
            if trained_model is not None:
                model_name = trained_model.__class__.__name__
            else:
                model_name = 'unknown_model'
                
            output_path = model_output_dir / f"{model_name}_{timestamp}.pkl"
            
            # 保存模型
            with open(output_path, 'wb') as f:
                pickle.dump(trained_model, f)
            
            self.logger.info(f"模型已自动保存到: {output_path}")
        except Exception as e:
            self.logger.warning(f"自动保存模型失败: {e}")

    def set_auto_extract_model(self, auto_extract: bool) -> None:
        """
        设置是否在分析完成后自动提取模型
        
        :param auto_extract: 是否自动提取模型
        """
        self.auto_extract_model = auto_extract

    def visualize_data(self, param_dict: Optional[Dict[str, Any]] = None) -> None:
        """
        数据可视化阶段

        Args:
            param_dict: 可视化参数字典，如果为None则使用分析结果中的默认参数
        """
        self.logger.info("core: 开始数据可视化")

        # 如果没有分析的数据，尝试从临时存储加载
        if self.analyzed_data is None:
            self.analyzed_data = self.temp_storage.load_data('analyzed', 'analyzed_data.pkl')
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
            
            self.logger.debug(f"可视化参数: {param_dict}")
            visualizer = data_visualization.DataVisualization(param_dict)
            self.visualized_plot = visualizer.plot_chart()
            
            # 保存可视化结果到临时存储
            self.temp_storage.save_data(self.visualized_plot, 'visualized', 'visualized_data.pkl')
            self.logger.info("数据可视化完成，生成了 %d 个图表", len(self.visualized_plot))

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
            # 尝试从临时存储加载
            self.analyzed_data = self.temp_storage.load_data('analyzed', 'analyzed_data.pkl')
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
        
        # 优先使用测试集数据进行可视化
        if ('X_test' in self.analyzed_data and self.analyzed_data['X_test'] is not None and
            'y_test' in self.analyzed_data and self.analyzed_data['y_test'] is not None and
            'predictions' in self.analyzed_data and self.analyzed_data['predictions'] is not None):
            # 使用测试集数据
            param_dict['feature'] = self.analyzed_data['X_test']
            param_dict['target'] = self.analyzed_data['y_test']
            param_dict['predict'] = self.analyzed_data['predictions']
        elif ('X_train' in self.analyzed_data and self.analyzed_data['X_train'] is not None and
              'y_train' in self.analyzed_data and self.analyzed_data['y_train'] is not None):
            # 回退到训练集数据
            param_dict['feature'] = self.analyzed_data['X_train']
            param_dict['target'] = self.analyzed_data['y_train']
            # 训练集上没有预测值，需要模型重新预测
            trained_model = self.analyzed_data.get('trained_model')
            if trained_model is not None:
                try:
                    predictions = trained_model.predict(self.analyzed_data['X_train'])
                    param_dict['predict'] = pd.Series(predictions, index=self.analyzed_data['y_train'].index)
                except:
                    param_dict['predict'] = None

        return param_dict

    def generate_report(self) -> None:
        """
        生成分析报告
        """
        self.logger.info("core: 开始生成报告")

        try:
            # 准备报告数据
            # 如果没有分析的数据，尝试从临时存储加载
            if not self.analyzed_data:
                self.analyzed_data = self.temp_storage.load_data('analyzed', 'analyzed_data.pkl')
                
            model_params = self.analyzed_data.get('model_params') if self.analyzed_data else None
            model_scores = self.analyzed_data.get('model_score') if self.analyzed_data else None
            model_predictions = self.analyzed_data.get('predictions') if self.analyzed_data else None
            
            # 如果没有可视化数据，尝试从临时存储加载
            if not self.visualized_plot:
                self.visualized_plot = self.temp_storage.load_data('visualized', 'visualized_data.pkl')
            
            report_generator = Report(
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
        finally:
            # 清理中间数据
            self.cleanup()
            
    def cleanup(self) -> None:
        """
        清理中间数据和优化内存
        """
        self.logger.info("开始清理中间数据")
        
        # 清空内存中的数据引用
        self.imported_data = None
        self.cleaned_data = None
        self.analyzed_data = None
        self.visualized_plot = None
        self.report_data = None
        
        # 清理磁盘上的临时数据
        self.temp_storage.clear_all_data()
        
        # 优化内存
        self.temp_storage.optimize_memory()
        
        self.logger.info("中间数据清理完成")

    def __str__(self)   -> str:
        return "欢迎使用数据分析引擎！！！"