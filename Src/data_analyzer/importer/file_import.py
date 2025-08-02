import pandas as pd
from pathlib import Path
from typing import Union, Optional
import logging


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
    
    def select_import_type(self) -> Optional[pd.DataFrame]:
        """
        根据文件类型选择相应的读取方法，并读取文件。
        
        :param kwargs: 传递给 pandas 读取函数的额外参数
        :return: Pandas DataFrame 或 None
        """
        if self.file_type not in self.default_file_type:
            logging.error(f"Unsupported file type: {self.file_type}")
            raise ValueError(f"Unsupported file type: {self.file_type}")
        
        if not self.path.exists():
            logging.error(f"The file {self.path} does not exist.")
            raise FileNotFoundError(f"The file {self.path} does not exist.")
        
        if not self.path.is_file():
            logging.error(f"The path {self.path} is a directory, not a file.")
            raise IsADirectoryError(f"The path {self.path} is a directory, not a file.")
        
        read_method_name = self.default_file_type[self.file_type]
        read_method = getattr(pd, read_method_name)
        
        try:
            df = read_method(self.path)
            return df
        except Exception as e:
            logging.error(f"Error reading file: {e}")
            print(f"Error reading file: {e}")
            return None