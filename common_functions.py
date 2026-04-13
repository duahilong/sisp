"""
公共函数模块，存放多个模块共同依赖的函数和数据
"""

import os
import json
import time
import logging
from typing import Any, Dict, Optional

# JSON配置缓存
_JSON_CACHE = {}
_JSON_CACHE_TIME = {}

# 日志配置
_logger = None


def setup_logging(log_file: str = None, level: int = logging.INFO):
    """配置日志系统"""
    global _logger
    if _logger is not None:
        return _logger
    
    _logger = logging.getLogger('sisp')
    _logger.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            _logger.addHandler(file_handler)
        except Exception:
            pass
    
    return _logger


def get_logger():
    """获取日志记录器"""
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


def _validate_json_file_path(file_path: str) -> str:
    """验证并处理JSON文件路径"""
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"JSON文件不存在: {file_path}")
    
    file_size = os.path.getsize(abs_path)
    if file_size == 0:
        raise ValueError("JSON文件为空")
    elif file_size > 50 * 1024 * 1024:
        raise ValueError(f"JSON文件过大: {file_size / (1024*1024):.2f}MB")
    
    return abs_path


def _check_json_cache(abs_path: str) -> Optional[Dict[str, Any]]:
    """检查JSON缓存"""
    if abs_path in _JSON_CACHE and abs_path in _JSON_CACHE_TIME:
        file_mtime = os.path.getmtime(abs_path)
        if _JSON_CACHE_TIME[abs_path] == file_mtime:
            return _JSON_CACHE[abs_path]
    return None


def _read_and_parse_json(abs_path: str, max_retries: int = 3) -> Dict[str, Any]:
    """读取并解析JSON文件"""
    for attempt in range(max_retries):
        try:
            with open(abs_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if not content.strip():
                raise ValueError("JSON文件内容为空或只包含空白字符")
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(0.1)


def _update_json_cache(abs_path: str, config_data: Dict[str, Any]) -> None:
    """更新JSON缓存"""
    _JSON_CACHE[abs_path] = config_data
    _JSON_CACHE_TIME[abs_path] = os.path.getmtime(abs_path)


def read_json_config(json_file_path: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """读取并解析JSON配置文件"""
    try:
        abs_path = _validate_json_file_path(json_file_path)
        
        if use_cache:
            cached_data = _check_json_cache(abs_path)
            if cached_data is not None:
                return cached_data
        
        config_data = _read_and_parse_json(abs_path)
        
        if use_cache:
            _update_json_cache(abs_path, config_data)
        
        return config_data
        
    except FileNotFoundError as e:
        print(f"X 文件错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"X JSON格式错误: {e}")
        return None
    except ValueError as e:
        print(f"X 文件验证错误: {e}")
        return None
    except Exception as e:
        print(f"X 读取JSON文件时发生未知错误: {e}")
        return None


def clear_json_cache():
    """清空JSON配置缓存"""
    global _JSON_CACHE, _JSON_CACHE_TIME
    _JSON_CACHE.clear()
    _JSON_CACHE_TIME.clear()


# 磁盘编号与盘符映射配置
number_list = [
    {
        "disk_number": 1,
        "efi_letter": "E",
        "c_letter": "F",
        "d_letter": "G",
        "e_letter": "H",
    },
    {
        "disk_number": 2,
        "efi_letter": "I",
        "c_letter": "J",
        "d_letter": "K",
        "e_letter": "L",
    },
    {
        "disk_number": 3,
        "efi_letter": "M",
        "c_letter": "N",
        "d_letter": "O",
        "e_letter": "P",
    },
    {
        "disk_number": 4,
        "efi_letter": "Q",
        "c_letter": "R",
        "d_letter": "S",
        "e_letter": "T",
    },
    {
        "disk_number": 5,
        "efi_letter": "U",
        "c_letter": "V",
        "d_letter": "W",
        "e_letter": "X",
    },
    {
        "disk_number": 6,
        "efi_letter": "Y",
        "c_letter": "Z",
        "d_letter": "A",
        "e_letter": "B",
    },
]


def get_disk_letter(disk_number, letter_type):
    """
    获取指定磁盘的特定分区字母
    
    Args:
        disk_number: 磁盘编号 (1-6)
        letter_type: 分区类型 ('efi', 'c', 'd', 'e')
    
    Returns:
        str: 对应的分区字母，如果未找到则返回None
        
    Example:
        >>> get_disk_letter(3, 'efi')
        'M'
    """
    for disk_config in number_list:
        if disk_config["disk_number"] == disk_number:
            if letter_type == 'efi':
                return disk_config["efi_letter"]
            elif letter_type == 'c':
                return disk_config["c_letter"]
            elif letter_type == 'd':
                return disk_config["d_letter"]
            elif letter_type == 'e':
                return disk_config["e_letter"]
            else:
                return None
    return None


# WMI连接单例
_disk_manager_instance = None


def get_disk_manager():
    """获取DiskManager单例实例"""
    global _disk_manager_instance
    if _disk_manager_instance is None:
        from disk_info import DiskManager
        _disk_manager_instance = DiskManager()
    return _disk_manager_instance