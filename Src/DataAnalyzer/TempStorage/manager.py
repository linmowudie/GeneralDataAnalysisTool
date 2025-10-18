"""
中间数据管理模块
用于处理大数据集的临时存储，避免内存溢出
"""

import os
import pandas as pd
import pickle
import logging
import shutil
from pathlib import Path
from typing import Optional, Any, Dict, List
import gc
import time


logger = logging.getLogger(__name__)

class StoragePathManager:
    """
    存储路径管理器
    负责管理不同处理阶段的存储路径
    """
    
    def __init__(self, base_path: str = "temp_storage"):
        """
        初始化存储路径管理器
        
        Args:
            base_path: 基础存储路径
        """
        # 如果base_path是相对路径，则基于项目根目录
        if not Path(base_path).is_absolute():
            self.base_path = PROJECT_ROOT / base_path
        else:
            self.base_path = Path(base_path)
            
        self.stage_paths = {
            'imported': self.base_path / "imported",
            'cleaned': self.base_path / "cleaned",
            'analyzed': self.base_path / "analyzed",
            'visualized': self.base_path / "visualized"
        }
        
        # 确保所有阶段路径存在
        for path in self.stage_paths.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def get_stage_path(self, stage: str) -> Path:
        """
        获取指定阶段的存储路径
        
        Args:
            stage: 处理阶段
            
        Returns:
            Path: 对应阶段的存储路径
        """
        if stage not in self.stage_paths:
            raise ValueError(f"不支持的阶段: {stage}")
        return self.stage_paths[stage]


class DataSerializer:
    """
    数据序列化器
    负责数据的保存和加载操作
    """
    
    @staticmethod
    def save_data(data: Any, file_path: Path) -> Path:
        """
        保存数据到文件
        
        Args:
            data: 要保存的数据
            file_path: 文件保存路径
            
        Returns:
            Path: 保存文件的路径
        """
        # 根据数据类型选择保存方式
        if isinstance(data, pd.DataFrame):
            # 对于DataFrame，使用更节省内存的格式
            if len(data) > 10000:  # 大于10000行的DataFrame使用parquet格式
                parquet_path = file_path.with_suffix('.parquet')
                data.to_parquet(parquet_path, index=False)
                logger.info(f"保存大数据DataFrame到 {parquet_path}")
                return parquet_path
            else:
                # 小数据集使用pickle
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
        else:
            # 其他数据类型使用pickle
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
                
        logger.info(f"保存数据到 {file_path}")
        return file_path
    
    @staticmethod
    def load_data(file_path: Path) -> Any:
        """
        从文件加载数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的数据
        """
        # 检查文件是否存在
        if not file_path.exists():
            logger.warning(f"文件 {file_path} 不存在")
            return None
            
        # 根据文件扩展名选择加载方式
        if file_path.suffix == '.parquet':
            data = pd.read_parquet(file_path)
            logger.info(f"从 {file_path} 加载大数据DataFrame")
        else:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            logger.info(f"从 {file_path} 加载数据")
            
        return data


class FileCleaner:
    """
    文件清理器
    负责清理过期和不需要的文件
    """
    
    @staticmethod
    def cleanup_old_files(paths: List[Path], max_age_hours: int = 24) -> None:
        """
        清理超过指定时间的旧文件
        
        Args:
            paths: 要清理的路径列表
            max_age_hours: 文件最大保留时间（小时）
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for path in paths:
            if path.exists():
                for file_path in path.iterdir():
                    try:
                        # 检查文件修改时间
                        if file_path.is_file():
                            file_age = current_time - file_path.stat().st_mtime
                            if file_age > max_age_seconds:
                                file_path.unlink()
                                logger.info(f"删除过期文件: {file_path}")
                    except Exception as e:
                        logger.warning(f"检查文件 {file_path} 时出错: {e}")
        
        logger.info("清理过期临时文件完成")
    
    @staticmethod
    def clear_directory(directory: Path) -> Dict[str, int]:
        """
        清理指定目录中的所有文件
        
        Args:
            directory: 要清理的目录
            
        Returns:
            dict: 清理统计信息
        """
        stats = {"files_removed": 0, "space_freed": 0}
        
        if directory.exists():
            for item in directory.iterdir():
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink()
                        stats["files_removed"] += 1
                        stats["space_freed"] += size
                    elif item.is_dir():
                        size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                        shutil.rmtree(item)
                        stats["space_freed"] += size
                except Exception as e:
                    logger.warning(f"删除文件 {item} 失败: {e}")
        
        return stats


class TempStorageManager:
    """
    中间数据存储管理器
    用于在磁盘上临时存储处理过程中的大数据，避免内存溢出
    """
    
    def __init__(self, base_path: str = "temp_storage", auto_cleanup: bool = True):
        """
        初始化中间数据存储管理器
        
        Args:
            base_path: 基础存储路径
            auto_cleanup: 是否在初始化时自动清理旧文件
        """
        self.path_manager = StoragePathManager(base_path)
        self.serializer = DataSerializer()
        self.cleaner = FileCleaner()
        
        # 如果启用自动清理，在初始化时清理旧文件
        if auto_cleanup:
            self._cleanup_old_files()
            
        logger.info("TempStorageManager 初始化完成")
    
    def _cleanup_old_files(self, max_age_hours: int = 24) -> None:
        """
        清理超过指定时间的旧文件
        
        Args:
            max_age_hours: 文件最大保留时间（小时）
        """
        paths = list(self.path_manager.stage_paths.values())
        self.cleaner.cleanup_old_files(paths, max_age_hours)
        
    def save_data(self, data: Any, stage: str, filename: str = "data.pkl") -> Path:
        """
        保存数据到指定阶段的存储目录
        
        Args:
            data: 要保存的数据
            stage: 处理阶段 ('imported', 'cleaned', 'analyzed', 'visualized')
            filename: 保存的文件名
            
        Returns:
            Path: 保存文件的路径
        """
        stage_path = self.path_manager.get_stage_path(stage)
        file_path = stage_path / filename
        return self.serializer.save_data(data, file_path)
        
    def load_data(self, stage: str, filename: str = "data.pkl") -> Any:
        """
        从指定阶段加载数据
        
        Args:
            stage: 处理阶段 ('imported', 'cleaned', 'analyzed', 'visualized')
            filename: 要加载的文件名
            
        Returns:
            加载的数据
        """
        stage_path = self.path_manager.get_stage_path(stage)
        file_path = stage_path / filename
        return self.serializer.load_data(file_path)
        
    def clear_stage_data(self, stage: str) -> None:
        """
        清理指定阶段的数据
        
        Args:
            stage: 处理阶段 ('imported', 'cleaned', 'analyzed', 'visualized')
        """
        stage_path = self.path_manager.get_stage_path(stage)
        self.cleaner.clear_directory(stage_path)
        logger.info(f"清理 {stage} 阶段数据完成")
        
    def clear_all_data(self) -> None:
        """
        清理所有中间数据
        """
        for stage in ['imported', 'cleaned', 'analyzed', 'visualized']:
            self.clear_stage_data(stage)
            
        logger.info("清理所有中间数据完成")
        
    def clear_all_temp_directories(self) -> Dict[str, int]:
        """
        清理所有临时目录（包括API输出目录）
        
        Returns:
            dict: 清理统计信息
        """
        stats = {"files_removed": 0, "space_freed": 0}
        
        # 清理各个阶段的数据
        for stage in ['imported', 'cleaned', 'analyzed', 'visualized']:
            stage_path = self.path_manager.get_stage_path(stage)
            stage_stats = self.cleaner.clear_directory(stage_path)
            stats["files_removed"] += stage_stats["files_removed"]
            stats["space_freed"] += stage_stats["space_freed"]
        
        # 清理API输出目录
        api_output_path = PROJECT_ROOT / "APIOutput"
        if api_output_path.exists():
            api_stats = self.cleaner.clear_directory(api_output_path)
            stats["files_removed"] += api_stats["files_removed"]
            stats["space_freed"] += api_stats["space_freed"]
            logger.info("API输出目录清理完成")
            
        logger.info("所有临时目录清理完成")
        return stats
        
    def clear_api_output(self) -> None:
        """
        清理API输出目录中的文件
        """
        api_output_path = PROJECT_ROOT / "APIOutput"
        if api_output_path.exists():
            for file_path in api_output_path.iterdir():
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                except Exception as e:
                    logger.warning(f"删除API输出文件 {file_path} 失败: {e}")
                    
        logger.info("清理API输出目录完成")

    def optimize_memory(self) -> None:
        """
        优化内存使用
        """
        gc.collect()
        logger.info("执行内存优化完成")

# 步骤映射配置
STEP_MAP = {
    'import': 'imported',
    'preview': 'imported',  # preview使用imported的数据
    'cleaning': 'cleaned',
    'analysis': 'analyzed',
    'visualization': 'visualized',
    'report': 'visualized'  # report使用visualized的数据
}

# 项目根目录路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class StepDataManager:
    """
    步骤数据管理器
    根据处理步骤管理数据的保存和清理
    """
    
    def __init__(self, storage_manager: TempStorageManager):
        """
        初始化步骤数据管理器
        
        Args:
            storage_manager: 临时存储管理器实例
        """
        self.storage_manager = storage_manager
    
    def cleanup_step_temp_files(self, step: str) -> Dict[str, int]:
        """
        清理指定步骤的临时文件
        
        Args:
            step: 步骤名称 ('import', 'preview', 'cleaning', 'analysis', 'visualization', 'report')
            
        Returns:
            dict: 清理统计信息
        """
        if step not in STEP_MAP:
            raise ValueError(f"不支持的步骤: {step}")
            
        stage = STEP_MAP[step]
        stats = {"files_removed": 0, "space_freed": 0}
        
        # 清理对应的临时存储目录
        stage_path = self.storage_manager.path_manager.get_stage_path(stage)
        stage_stats = self.storage_manager.cleaner.clear_directory(stage_path)
        
        # 合并统计信息
        stats["files_removed"] += stage_stats["files_removed"]
        stats["space_freed"] += stage_stats["space_freed"]
        
        logger.info(f"步骤 {step} 的临时文件清理完成")
        
        # 如果是导入步骤，还需要清理API输出目录
        if step == 'import':
            api_output_path = PROJECT_ROOT / "APIOutput"
            if api_output_path.exists():
                api_stats = self.storage_manager.cleaner.clear_directory(api_output_path)
                stats["files_removed"] += api_stats["files_removed"]
                stats["space_freed"] += api_stats["space_freed"]
                logger.info("API输出目录清理完成")
        
        return stats



