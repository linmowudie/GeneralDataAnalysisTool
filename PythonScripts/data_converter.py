#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据格式转换脚本
用于将测试数据转换成各种当前支持的格式
支持 CSV、Excel、JSON、HTML、SQLite、MongoDB、Redis 等格式
"""

import pandas as pd
import json
import sqlite3
import os
from pathlib import Path
import argparse
import sys

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("警告: pymongo 未安装，MongoDB 功能不可用")

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("警告: redis 未安装，Redis 功能不可用")


class DataConverter:
    """
    数据格式转换器类
    支持将数据转换为多种格式
    """
    
    def __init__(self, input_file):
        """
        初始化数据转换器
        
        :param input_file: 输入文件路径
        """
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"输入文件 {input_file} 不存在")
        
        # 读取数据
        self.data = self._read_data()
        print(f"成功读取数据，共 {len(self.data)} 行")
    
    def _read_data(self):
        """
        读取输入数据
        
        :return: DataFrame
        """
        file_extension = self.input_file.suffix.lower()
        
        if file_extension == '.csv':
            return pd.read_csv(self.input_file)
        elif file_extension in ['.xlsx', '.xls']:
            return pd.read_excel(self.input_file)
        elif file_extension == '.json':
            return pd.read_json(self.input_file)
        else:
            raise ValueError(f"不支持的输入文件格式: {file_extension}")
    
    def to_csv(self, output_file):
        """
        转换为 CSV 格式
        
        :param output_file: 输出文件路径
        """
        output_path = Path(output_file)
        self.data.to_csv(output_path, index=False)
        print(f"数据已保存为 CSV 格式: {output_file}")
    
    def to_excel(self, output_file):
        """
        转换为 Excel 格式
        
        :param output_file: 输出文件路径
        """
        output_path = Path(output_file)
        self.data.to_excel(output_path, index=False)
        print(f"数据已保存为 Excel 格式: {output_file}")
    
    def to_json(self, output_file):
        """
        转换为 JSON 格式
        
        :param output_file: 输出文件路径
        """
        output_path = Path(output_file)
        self.data.to_json(output_path, orient='records', indent=2)
        print(f"数据已保存为 JSON 格式: {output_file}")
    
    def to_html(self, output_file):
        """
        转换为 HTML 格式
        
        :param output_file: 输出文件路径
        """
        output_path = Path(output_file)
        html_string = self.data.to_html(index=False)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_string)
        print(f"数据已保存为 HTML 格式: {output_file}")
    
    def to_sqlite(self, output_file, table_name="data"):
        """
        转换为 SQLite 数据库格式
        
        :param output_file: 输出文件路径
        :param table_name: 表名
        """
        output_path = Path(output_file)
        conn = sqlite3.connect(output_path)
        self.data.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        print(f"数据已保存为 SQLite 数据库: {output_file}，表名: {table_name}")
    
    def to_mongodb(self, connection_string, database_name, collection_name):
        """
        转换为 MongoDB 格式
        
        :param connection_string: MongoDB 连接字符串
        :param database_name: 数据库名
        :param collection_name: 集合名
        """
        if not MONGO_AVAILABLE:
            raise ImportError("pymongo 未安装，无法使用 MongoDB 功能")
        
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]
        
        # 清空现有数据
        collection.delete_many({})
        
        # 插入新数据
        records = self.data.to_dict('records')
        if records:
            collection.insert_many(records)
            print(f"数据已保存到 MongoDB: {connection_string}/{database_name}.{collection_name}，共 {len(records)} 条记录")
        else:
            print("没有数据需要保存到 MongoDB")
        
        client.close()
    
    def to_redis(self, connection_string, key_name):
        """
        转换为 Redis 格式
        
        :param connection_string: Redis 连接字符串
        :param key_name: 键名
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis 未安装，无法使用 Redis 功能")
        
        r = redis.from_url(connection_string)
        
        # 将数据转换为 JSON 格式
        data_json = self.data.to_json(orient='records')
        
        # 保存到 Redis
        r.set(key_name, data_json)
        print(f"数据已保存到 Redis: {connection_string}，键名: {key_name}")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='数据格式转换工具')
    parser.add_argument('input_file', help='输入文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-f', '--format', choices=['csv', 'excel', 'json', 'html', 'sqlite'], 
                       help='输出格式')
    parser.add_argument('--mongodb-connection', help='MongoDB 连接字符串')
    parser.add_argument('--mongodb-database', help='MongoDB 数据库名')
    parser.add_argument('--mongodb-collection', help='MongoDB 集合名')
    parser.add_argument('--redis-connection', help='Redis 连接字符串')
    parser.add_argument('--redis-key', help='Redis 键名')
    
    args = parser.parse_args()
    
    try:
        # 创建转换器
        converter = DataConverter(args.input_file)
        
        # 根据指定格式进行转换
        if args.format and args.output:
            if args.format == 'csv':
                converter.to_csv(args.output)
            elif args.format == 'excel':
                converter.to_excel(args.output)
            elif args.format == 'json':
                converter.to_json(args.output)
            elif args.format == 'html':
                converter.to_html(args.output)
            elif args.format == 'sqlite':
                converter.to_sqlite(args.output)
        
        # MongoDB 转换
        if args.mongodb_connection and args.mongodb_database and args.mongodb_collection:
            converter.to_mongodb(
                args.mongodb_connection, 
                args.mongodb_database, 
                args.mongodb_collection
            )
        
        # Redis 转换
        if args.redis_connection and args.redis_key:
            converter.to_redis(
                args.redis_connection, 
                args.redis_key
            )
        
        print("数据转换完成！")
        
    except Exception as e:
        print(f"数据转换过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()