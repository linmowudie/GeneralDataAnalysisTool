from pathlib import Path
from typing import Union, Optional
import logging
from .importer.db_import import DatabaseImport
from .importer.file_import import FileImport
import pandas as pd

class DataImport(DatabaseImport, FileImport):
    def __init__(self, file_resource: Union[str, Path], resource_type: str, db_connection_string: str, is_database: bool = False) -> None:
        """
        初始化 DataImport 实例。
        
        :param file_resource: 文件来源或者路径
        :param resource_type: 文件类型或者数据库类型
        :param is_database: 标记是否从数据库导入数据
        :param db_connection_string: 数据库连接信息
        """
        self.is_database = is_database
        if self.is_database:
            DatabaseImport.__init__(self, db_connection_string, resource_type)
        else:
            FileImport.__init__(self, file_resource, resource_type)

    def import_data(self, **kwargs) -> Optional[Union[pd.DataFrame, None]]:
        """
        根据 is_database 属性选择合适的数据导入方法。
        
        :param kwargs: 传递给具体导入函数的额外参数
        :return: Pandas DataFrame 或者 None
        """
        try:
            if self.is_database:
                return self.select_db_import_type(**kwargs)
            else:
                return self.select_import_type(**kwargs)
            
        except Exception as e:
            logging.error(f"Error importing data: {e}")
            print(f"Error importing data: {e}")
            return None