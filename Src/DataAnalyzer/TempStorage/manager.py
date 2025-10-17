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
from typing import Optional, Any
import gc
import time

logger = logging.getLogger(__name__)

class TempStorageManager:
    """
    中间数据存储管理器
    用于在磁盘上临时存储处理过程中的大数据，避免内存溢出
    """
    
    def __init__(self, base_path: str = "Src/DataAnalyzer/TempStorage", auto_cleanup: bool = True):
        """
        初始化中间数据存储管理器
        
        Args:
            base_path: 基础存储路径
            auto_cleanup: 是否在初始化时自动清理旧文件
        """
        self.base_path = Path(base_path)
        self.imported_path = self.base_path / "imported"
        self.cleaned_path = self.base_path / "cleaned"
        self.analyzed_path = self.base_path / "analyzed"
        self.visualized_path = self.base_path / "visualized"
        
        # 确保存储目录存在
        for path in [self.imported_path, self.cleaned_path, 
                     self.analyzed_path, self.visualized_path]:
            path.mkdir(parents=True, exist_ok=True)
            
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
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for stage_path in [self.imported_path, self.cleaned_path, 
                          self.analyzed_path, self.visualized_path]:
            if stage_path.exists():
                for file_path in stage_path.iterdir():
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
        stage_path = getattr(self, f"{stage}_path", None)
        if stage_path is None:
            raise ValueError(f"不支持的阶段: {stage}")
            
        file_path = stage_path / filename
        
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
        
    def load_data(self, stage: str, filename: str = "data.pkl") -> Any:
        """
        从指定阶段加载数据
        
        Args:
            stage: 处理阶段 ('imported', 'cleaned', 'analyzed', 'visualized')
            filename: 要加载的文件名
            
        Returns:
            加载的数据
        """
        stage_path = getattr(self, f"{stage}_path", None)
        if stage_path is None:
            raise ValueError(f"不支持的阶段: {stage}")
            
        file_path = stage_path / filename
        
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
        
    def clear_api_output(self) -> None:
        """
        清理API输出目录中的文件
        """
        api_output_path = Path("APIOutput")
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
        
    def clear_stage_data(self, stage: str) -> None:
        """
        清理指定阶段的数据
        
        Args:
            stage: 处理阶段 ('imported', 'cleaned', 'analyzed', 'visualized')
        """
        stage_path = getattr(self, f"{stage}_path", None)
        if stage_path is None:
            raise ValueError(f"不支持的阶段: {stage}")
            
        # 删除该目录下的所有文件
        for file_path in stage_path.iterdir():
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.warning(f"删除文件 {file_path} 失败: {e}")
                
        logger.info(f"清理 {stage} 阶段数据完成")
        
    def clear_all_data(self) -> None:
        """
        清理所有中间数据
        """
        for stage in ['imported', 'cleaned', 'analyzed', 'visualized']:
            self.clear_stage_data(stage)
            
        logger.info("清理所有中间数据完成")
        
    def optimize_memory(self) -> None:
        """
        优化内存使用
        """
        gc.collect()
        logger.info("执行内存优化完成")