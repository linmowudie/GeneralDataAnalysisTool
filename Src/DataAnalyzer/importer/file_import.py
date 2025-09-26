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
            # 如果指定了chunksize且是CSV文件，则分块读取
            if chunksize is not None and self.file_type == 'csv':
                chunks = []
                for chunk in read_method(self.path, chunksize=chunksize):
                    chunks.append(chunk)
                df = pd.concat(chunks, ignore_index=True)
                logger.info(f"分块读取完成，共 {len(chunks)} 块，合并后 {len(df)} 行")
            else:
                df = read_method(self.path)
            return df
        except Exception as e:
            logger.error(f"文件读取错误：{e}")
            print(f"文件读取错误：{e}")
            return None