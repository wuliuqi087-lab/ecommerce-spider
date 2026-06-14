"""
数据存储模块 - 支持多种存储方式
"""
import json
import csv
import os
import logging
from typing import List, Dict
from config import STORAGE_CONFIG

logger = logging.getLogger(__name__)


class DataStorage:
    """数据存储基类"""
    
    def __init__(self):
        self.output_dir = STORAGE_CONFIG['output_dir']
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f'Created output directory: {self.output_dir}')
    
    def save(self, data: List[Dict], filename: str):
        """保存数据（由子类实现）"""
        raise NotImplementedError


class JsonStorage(DataStorage):
    """JSON 格式存储"""
    
    def save(self, data: List[Dict], filename: str = None):
        """
        保存为 JSON 文件
        
        Args:
            data: 数据列表
            filename: 文件名
        """
        if filename is None:
            filename = STORAGE_CONFIG['filename']
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f'✓ 数据已保存到: {filepath}')
        except Exception as e:
            logger.error(f'✗ 保存 JSON 失败: {e}')


class CsvStorage(DataStorage):
    """CSV 格式存储"""
    
    def save(self, data: List[Dict], filename: str = None):
        """
        保存为 CSV 文件
        
        Args:
            data: 数据列表
            filename: 文件名
        """
        if filename is None:
            filename = STORAGE_CONFIG['filename'].replace('.json', '.csv')
        
        if not data:
            logger.warning('没有数据可保存')
            return
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            keys = data[0].keys()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f'✓ 数据已保存到: {filepath}')
        except Exception as e:
            logger.error(f'✗ 保存 CSV 失败: {e}')


class ExcelStorage(DataStorage):
    """Excel 格式存储"""
    
    def save(self, data: List[Dict], filename: str = None):
        """
        保存为 Excel 文件
        
        Args:
            data: 数据列表
            filename: 文件名
        """
        if filename is None:
            filename = STORAGE_CONFIG['filename'].replace('.json', '.xlsx')
        
        if not data:
            logger.warning('没有数据可保存')
            return
        
        try:
            import pandas as pd
            filepath = os.path.join(self.output_dir, filename)
            
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
            logger.info(f'✓ 数据已保存到: {filepath}')
        except ImportError:
            logger.error('pandas 或 openpyxl 未安装')
        except Exception as e:
            logger.error(f'✗ 保存 Excel 失败: {e}')


def get_storage(storage_type: str = None) -> DataStorage:
    """
    获取存储对象
    
    Args:
        storage_type: 存储类型 ('json', 'csv', 'excel')
        
    Returns:
        存储对象
    """
    if storage_type is None:
        storage_type = STORAGE_CONFIG['type']
    
    storage_map = {
        'json': JsonStorage,
        'csv': CsvStorage,
        'excel': ExcelStorage,
    }
    
    storage_class = storage_map.get(storage_type, JsonStorage)
    return storage_class()
