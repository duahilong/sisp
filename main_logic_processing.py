from ast import parse
import json
import os
import time
import argparse
from typing import Dict, Any, Optional
from webbrowser import get
from disk_info import DiskManager

import disk_info
from partition_disk import initialize_disk_to_gpt
from partition_disk import initialize_disk_to_partitioning_C
from partition_disk import initialize_disk_to_partitioning_D
from partition_disk import initialize_disk_to_partitioning_E
from call_ghost import call_ghost
from call_bcdboot import repair_boot_loader

# JSON配置缓存 - 这个保留，因为它是真正的缓存机制
_JSON_CACHE = {}
_JSON_CACHE_TIME = {}
def parse_arguments():
    parser = argparse.ArgumentParser(
    description="磁盘信息查询工具",
    epilog="示例: python main.py --disk 3 或 python main.py -d 5 --json config.json"
    )
    
    # 添加磁盘编号参数
    parser.add_argument(
    '--disk', '-d',
    type=int,
    required=True,
    choices=[1, 2, 3, 4, 5, 6],
    help='磁盘编号 (1-6)，用于指定要操作的磁盘',
    metavar='DISK_NUMBER'
    )
    
    parser.add_argument(
    '--json', '-j',
    type=str,
    required=True,
    help='JSON配置文件路径',
    metavar='FILE_PATH'
    )
    
    return parser.parse_args()



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

def get_config_value(config_data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    安全获取配置值的函数
    
    Args:
        config_data: JSON配置数据字典
        key_path: 支持点分隔的路径，如 'disk.number'
        default: 默认值
        
    Returns:
        配置值或默认值
    """
    if not config_data:
        return default
    
    # 处理简单的键访问
    if '.' not in key_path:
        return config_data.get(key_path, default)
    
    # 处理嵌套路径访问
    keys = key_path.split('.')
    current = config_data
    
    try:
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current if current is not None else default
    except (TypeError, KeyError, AttributeError):
        return default


def clear_json_cache():
    """清空JSON配置缓存"""
    global _JSON_CACHE, _JSON_CACHE_TIME
    _JSON_CACHE.clear()
    _JSON_CACHE_TIME.clear()
    print("JSON缓存已清空")


def get_cache_info() -> Dict[str, Any]:
    """
    获取缓存信息
    
    Returns:
        缓存统计信息
    """
    total_size = 0
    for filepath in _JSON_CACHE.keys():
        if os.path.exists(filepath):
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, IOError):
                pass  # 忽略无法访问的文件
    
    return {
        "cached_files": len(_JSON_CACHE),
        "cache_size_mb": total_size / (1024 * 1024),
        "validation_enabled": False,  # JSON结构验证功能已被禁用
        "cache_keys": list(_JSON_CACHE.keys())
    }


def _validate_json_file_path(file_path: str) -> str:
    """验证并处理JSON文件路径
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        处理后的绝对路径
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件为空或过大
    """
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"JSON文件不存在: {file_path}")
    
    file_size = os.path.getsize(abs_path)
    if file_size == 0:
        raise ValueError("JSON文件为空")
    elif file_size > 50 * 1024 * 1024:  # 50MB限制
        raise ValueError(f"JSON文件过大: {file_size / (1024*1024):.2f}MB")
    
    return abs_path


def _check_cache(abs_path: str) -> Optional[Dict[str, Any]]:
    """检查缓存
    
    Args:
        abs_path: 文件绝对路径
        
    Returns:
        缓存的数据，如果缓存未命中则返回None
    """
    if abs_path in _JSON_CACHE and abs_path in _JSON_CACHE_TIME:
        file_mtime = os.path.getmtime(abs_path)
        if _JSON_CACHE_TIME[abs_path] == file_mtime:
            print(f"从缓存读取JSON配置: {abs_path}")
            return _JSON_CACHE[abs_path]
    return None


def _read_and_parse_json(abs_path: str, max_retries: int = 3) -> Dict[str, Any]:
    """读取并解析JSON文件
    
    Args:
        abs_path: 文件绝对路径
        max_retries: 最大重试次数
        
    Returns:
        解析后的JSON数据
        
    Raises:
        json.JSONDecodeError: JSON解析错误
        ValueError: 文件内容为空或无效
    """
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
            print(f"JSON解析重试 {attempt + 1}/{max_retries}: {e}")
            time.sleep(0.1)


def _update_cache(abs_path: str, config_data: Dict[str, Any]) -> None:
    """更新缓存
    
    Args:
        abs_path: 文件绝对路径
        config_data: 配置数据
    """
    _JSON_CACHE[abs_path] = config_data
    _JSON_CACHE_TIME[abs_path] = os.path.getmtime(abs_path)


def read_json_config(json_file_path: str, use_cache: bool = True, 
                    validate_schema: bool = True) -> Optional[Dict[str, Any]]:
    """
    高性能读取并解析JSON配置文件
    
    主要功能：
    1. 读取JSON配置文件
    2. 验证文件格式和结构
    3. 支持缓存机制提高性能
    4. 提供详细的错误信息和处理
    
    Args:
        json_file_path: JSON文件路径
        use_cache: 是否使用缓存机制（避免重复读取同一文件）
        validate_schema: 是否进行schema验证（检查JSON结构是否符合预期）
        
    Returns:
        解析后的JSON数据，失败时返回None
    """
    try:
        # 验证文件路径
        abs_path = _validate_json_file_path(json_file_path)
        
        # 检查文件扩展名
        if not abs_path.lower().endswith(('.json', '.jsonc', '.json5')):
            print(f"警告: 文件扩展名不是标准的JSON格式: {json_file_path}")
        
        # 检查缓存
        if use_cache:
            cached_data = _check_cache(abs_path)
            if cached_data is not None:
                return cached_data
        
        # 读取并解析JSON
        config_data = _read_and_parse_json(abs_path)
        
        # 更新缓存
        if use_cache:
            _update_cache(abs_path, config_data)
        
        # 显示成功信息
        if config_data and 'description' in config_data:
            print(f"成功读取JSON配置文件: {config_data['description']}")
        else:
            print(f"成功读取JSON配置文件: {json_file_path}")
        
        return config_data
        
    except FileNotFoundError as e:
        print(f"X 文件错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"X JSON格式错误: {e}")
        print("   建议检查:")
        print("   - 字符串是否用双引号包围")
        print("   - 末尾逗号和不必要的逗号")
        print("   - 转义字符是否正确")
        return None
    except ValueError as e:
        print(f"X 文件验证错误: {e}")
        return None
    except PermissionError as e:
        print(f"X 权限错误: 无法读取文件 {json_file_path}")
        return None
    except Exception as e:
        print(f"X 读取JSON文件时发生未知错误: {e}")
        return None


def analyze_json_structure(data: Any, max_depth: int = 3, current_depth: int = 0):
    """
    分析并显示JSON数据结构
    
    Args:
        data: JSON数据
        max_depth: 最大分析深度
        current_depth: 当前分析深度
    """
    if current_depth >= max_depth:
        return
    
    indent = "  " * current_depth
    
    if isinstance(data, dict):
        print(f"{indent}📊 字典结构 - {len(data)} 个键值对:")
        
        # 显示主要键值
        keys = list(data.keys())
        main_keys = keys[:5] if len(keys) > 5 else keys
        
        for key in main_keys:
            value = data[key]
            value_type = type(value).__name__
            if isinstance(value, str):
                preview = value[:20] + "..." if len(value) > 20 else value
                print(f"{indent}  🔑 {key}: {value_type} = {repr(preview)}")
            elif isinstance(value, (int, float)):
                print(f"{indent}  🔢 {key}: {value_type} = {value}")
            elif isinstance(value, list):
                print(f"{indent}  📋 {key}: {value_type}[{len(value)}]")
            elif isinstance(value, dict):
                print(f"{indent}  📁 {key}: {value_type}[{len(value)}]")
            else:
                print(f"{indent}  注释 {key}: {value_type}")
        
        if len(keys) > 5:
            print(f"{indent}  ... 还有 {len(keys) - 5} 个其他键值")
            
        # 递归分析嵌套结构（限制深度）
        if current_depth < max_depth - 1:
            nested_dicts = [v for v in data.values() if isinstance(v, dict) and len(v) > 0]
            for i, nested_data in enumerate(nested_dicts[:2]):  # 只显示前2个嵌套结构
                print(f"{indent}  📂 嵌套字典 {i+1}:")
                analyze_json_structure(nested_data, max_depth, current_depth + 2)
                
    elif isinstance(data, list):
        print(f"{indent}📋 列表结构 - {len(data)} 个元素:")
        if data:
            sample_item = data[0]
            sample_type = type(sample_item).__name__
            print(f"{indent}  元素类型: {sample_type}")
            
            # 如果是字典列表，显示键值
            if isinstance(sample_item, dict) and sample_item:
                sample_keys = list(sample_item.keys())[:3]
                print(f"{indent}  主要键值: {', '.join(sample_keys)}")
    else:
        print(f"{indent}注释 {type(data).__name__}: {data}")


def setup_json_config(args: argparse.Namespace) -> Dict[str, Any]:
    """设置并读取JSON配置文件
    
    Args:
        args: 命令行参数对象，包含json字段
        
    Returns:
        读取的JSON配置数据字典，如果失败则返回空字典
    """
    if args.json:
        config_data = read_json_config(args.json)
        if config_data is None:
            print("X JSON配置文件读取失败，程序退出。")
            return {}
        else:
            return config_data
    else:
        print("ℹ️  未指定JSON配置文件，使用默认配置。")
        return {}


def validate_protected_disk(disk_number: int, config_data: Optional[dict] = None) -> bool:
    """
    验证用户输入的disk_number是否为保护硬盘
    
    Args:
        disk_number: 磁盘编号 (1-6)
        config_data: JSON配置数据字典，包含excluded_disk_names字段
        
    Returns:
        bool: 如果不是保护硬盘返回True，如果是保护硬盘返回False
        
    Raises:
        ValueError: 当disk_number超出范围或配置数据无效时抛出
        RuntimeError: 当无法获取磁盘信息时抛出
    """
    if not isinstance(disk_number, int) or disk_number < 1 or disk_number > 6:
        raise ValueError(f"磁盘编号必须在1-6范围内，错误编号: {disk_number}")
    
    # 如果没有提供配置数据，返回True（默认可操作）
    if config_data is None:
        return True
    
    # 获取保护硬盘名称列表
    excluded_disk_names = config_data.get('excluded_disk_names', [])
    if not isinstance(excluded_disk_names, list):
        raise ValueError("excluded_disk_names必须是列表格式")
    
    try:
        # 使用disk_info模块查询指定磁盘编号的硬盘名称
        disk_manager = DiskManager()
        disk_info = disk_manager.get_disk_by_index(disk_number)
        
        if disk_info is None:
            raise RuntimeError(f"未找到磁盘编号 {disk_number} 的信息")
        
        disk_name = disk_info.name
        
        # 检查是否为保护硬盘
        if disk_name in excluded_disk_names:
            print(f"⚠️  磁盘 {disk_number} ({disk_name}) 是保护硬盘，无法操作")
            return False
        else:
            # 验证成功，静默返回（不输出任何信息）
            return True
            
    except Exception as e:
        raise RuntimeError(f"获取磁盘 {disk_number} 信息失败: {e}")



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




def all_disk_partitions(disk_number, efi_size, c_size):
    """
    初始化磁盘分区
    
    Args:
        disk_number: 磁盘编号 (1-6)
        efi_size: EFI分区大小 (MB)
        c_size: C盘分区大小 (MB)
    """
    efi_letter = get_disk_letter(disk_number, 'efi')
    c_letter = get_disk_letter(disk_number, 'c')
    d_letter = get_disk_letter(disk_number, 'd')
    e_letter = get_disk_letter(disk_number, 'e')

    # 顺序执行：第一步
    if not initialize_disk_to_gpt(disk_number, efi_size, efi_letter):
        return False
    
    # 顺序执行：第二步
    if not initialize_disk_to_partitioning_C(disk_number, c_size, c_letter):
        return False
    
    # 顺序执行：第三步
    if not initialize_disk_to_partitioning_D(disk_number, d_letter, efi_size, c_size):
        return False
    
    # 顺序执行：第四步
    if not initialize_disk_to_partitioning_E(disk_number, e_letter):
        return False
    
    return True



if __name__ == "__main__":
    
    args = parse_arguments()
    disk_number = args.disk
    json_data = setup_json_config(args)
    efi_size = json_data.get("efi_size")
    c_size = json_data.get("c_size")
    gho_exe = json_data.get("gho_exe")
    win_gho = json_data.get("win_gho")
    bcd_exe = json_data.get("bcd_exe")
    efi_letter = get_disk_letter(disk_number, 'efi')
    c_letter = get_disk_letter(disk_number, 'c')
    print(c_letter)
    print(c_size)
    print(efi_size)
    print(disk_number)
    
    validate_protected_disk(disk_number, json_data)

        # if all_disk_partitions(disk_number, efi_size, c_size):
        #     time.sleep(5)
        #     if call_ghost(disk_number, gho_exe, win_gho, c_letter):
        #         time.sleep(5)
        #         if repair_boot_loader(disk_number, bcd_exe, efi_letter, c_letter):
        #             pass
        #         else:
        #             pass
        #     else:
        #         pass
        # else:
        #     pass


