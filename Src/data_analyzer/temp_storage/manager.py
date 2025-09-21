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

logger = logging.getLogger(__name__)

class TempStorageManager:
    """
    中间数据存储管理器
    用于在磁盘上临时存储处理过程中的大数据，避免内存溢出
    """
    
    def __init__(self, base_path: str = "Src/data_analyzer/temp_storage"):
        """
        初始化中间数据存储管理器
        
        Args:
            base_path: 基础存储路径
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
            
        logger.info("TempStorageManager 初始化完成")
        
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