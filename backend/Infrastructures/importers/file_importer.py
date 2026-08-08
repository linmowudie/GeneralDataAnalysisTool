"""
backend/Infrastructures/importers/file_importer.py
FileImporter：按扩展名分发 csv/excel/json/html 读取，支持 chunksize 流式读取

统一签名 read(source, **kwargs) -> DataFrame，异常统一抛 ImportError_。
（读取实现原位于 Engine/ImporterModule/file_import.FileImport，已内联）
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from backend.shared.types import ImportError_  # noqa: E402

logger = logging.getLogger(__name__)


class FileImporter:
    """文件读取器"""

    SUPPORTED = {"csv", "xlsx", "xls", "json", "html"}

    # 文件类型 -> pandas 读取方法
    _READ_METHODS = {
        "xlsx": "read_excel",
        "csv": "read_csv",
        "html": "read_html",
        "json": "read_json",
    }

    def read(self, source: Union[str, Path], file_type: Optional[str] = None,
             chunksize: Optional[int] = None, **kwargs) -> pd.DataFrame:
        """
        读取文件为 DataFrame

        :param source: 文件路径
        :param file_type: 文件类型（缺省按扩展名推断）
        :param chunksize: 分块大小（大文件流式读取）
        :return: DataFrame
        :raises ImportError_: 读取失败
        """
        source_path = Path(source)
        if not source_path.exists():
            raise ImportError_(f"文件不存在: {source}")

        if file_type is None:
            file_type = source_path.suffix.lstrip(".").lower()
            # xls 归一到 xlsx 处理
            if file_type == "xls":
                file_type = "xlsx"

        if file_type not in self.SUPPORTED:
            raise ImportError_(f"不支持的文件类型: {file_type}")

        try:
            # 大文件自动启用分块读取
            if chunksize is None:
                try:
                    file_size_mb = os.path.getsize(source_path) / (1024 * 1024)
                    if file_size_mb > 100:
                        chunksize = 10000
                        logger.info("检测到大文件 (%.2f MB)，启用分块读取", file_size_mb)
                except OSError:
                    pass

            df = self._read_file(source_path, file_type, chunksize)
            if df is None:
                raise ImportError_(f"文件读取返回空结果: {source}")
            return df
        except ImportError_:
            raise
        except Exception as e:
            logger.error("文件读取失败: %s", e, exc_info=True)
            raise ImportError_(f"文件读取失败: {str(e)}") from e

    # ------------------------------------------------------------------ 内部
    def _read_file(self, path: Path, file_type: str,
                   chunksize: Optional[int]) -> Optional[pd.DataFrame]:
        """按文件类型读取；csv 支持分块流式读取"""
        read_method = getattr(pd, self._READ_METHODS[file_type])

        # csv 大文件流式读取
        if file_type == "csv" and chunksize is not None:
            logger.info("开始以流式方式读取CSV文件，块大小: %s", chunksize)
            header_chunk = pd.read_csv(path, nrows=0)
            columns = header_chunk.columns

            chunks = []
            total_rows = 0
            for i, chunk in enumerate(read_method(path, chunksize=chunksize)):
                chunks.append(chunk)
                total_rows += len(chunk)
                logger.info("已读取CSV块 %d，包含 %d 行，累计 %d 行", i + 1, len(chunk), total_rows)
                # 每处理完10个块合并一次，减少内存占用
                if len(chunks) >= 10:
                    chunks = [pd.concat(chunks, ignore_index=True)]

            df = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=columns)
            logger.info("CSV文件流式读取完成，共读取 %d 行数据", total_rows)
            return df

        df = read_method(path)
        logger.info("文件读取完成，共 %d 行数据", len(df))
        return df
