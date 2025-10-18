"""
Src/DataAnalyzer/importer/file_import.py
文件导入模块

该模块提供从各种文件格式导入数据的功能，支持CSV、Excel、JSON等
常见数据文件格式，并针对大文件提供分块读取功能以避免内存溢出。
"""

import pandas as pd
from pathlib import Path
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)

class FileImport:
    # 文件类型映射
    default_file_type = {
        'xlsx': 'read_excel', 
        'csv': 'read_csv', 
        'html': 'read_html', 
        'json': 'read_json'
    }
    
    def __init__(self, path: Union[str, Path], file_type: str):
        """
        初始化 FileImport 实例。
        
        :param path: 文件路径
        :param file_type: 文件类型
        """
        self.path = Path(path)
        self.file_type = file_type.lower()  # 确保文件类型统一为小写
    
    def select_import_type(self, chunksize: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        根据文件类型选择相应的读取方法，并读取文件。
        对于大文件，支持分块读取以避免内存溢出。
        对于CSV文件，支持流式处理模式。
        
        :param chunksize: 分块大小，None表示一次性读取整个文件
        :return: Pandas DataFrame 或 None
        """
        if self.file_type not in self.default_file_type:
            logger.error(f"不支持文件类型: {self.file_type}")
            raise ValueError(f"不支持文件类型: {self.file_type}")
        
        if not self.path.exists():
            logger.error(f"文件 {self.path} 不存在。")
            raise FileNotFoundError(f"文件 {self.path} 不存在.")
        
        if not self.path.is_file():
            logger.error(f"{self.path}是一个文件夹 , 不是文件。")
            raise IsADirectoryError(f"{self.path}是一个文件夹 , 不是文件。")
        
        read_method_name = self.default_file_type[self.file_type]
        read_method = getattr(pd, read_method_name)
        
        try:
            # 如果是CSV文件且指定了chunksize，则使用流式处理
            if self.file_type == 'csv' and chunksize is not None:
                logger.info(f"开始以流式方式读取CSV文件，块大小: {chunksize}")
                
                # 先获取CSV的列名
                header_chunk = pd.read_csv(self.path, nrows=0)
                columns = header_chunk.columns
                
                # 使用生成器模式逐块读取和处理
                chunks = []
                total_rows = 0
                
                for i, chunk in enumerate(read_method(self.path, chunksize=chunksize)):
                    chunks.append(chunk)
                    total_rows += len(chunk)
                    logger.info(f"已读取CSV块 {i+1}，包含 {len(chunk)} 行，累计 {total_rows} 行")
                    
                    # 每处理完10个块合并一次，减少内存占用
                    if len(chunks) >= 10:
                        temp_df = pd.concat(chunks, ignore_index=True)
                        chunks = [temp_df]
                
                # 合并剩余的块
                if chunks:
                    df = pd.concat(chunks, ignore_index=True)
                else:
                    df = pd.DataFrame(columns=columns)
                
                logger.info(f"CSV文件流式读取完成，共读取 {total_rows} 行数据")
                return df
            # 对于其他情况，使用普通读取方式
            else:
                df = read_method(self.path)
                logger.info(f"文件读取完成，共 {len(df)} 行数据")
                return df
        except Exception as e:
            logger.error(f"文件读取错误：{e}", exc_info=True)
            print(f"文件读取错误：{e}")
            return None