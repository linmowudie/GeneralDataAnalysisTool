"""
中间数据存储包
用于处理大数据集的临时存储，避免内存溢出
"""

from .manager import TempStorageManager

__all__ = ['TempStorageManager']