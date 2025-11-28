#!/usr/bin/env python3
"""
main.py - 磁盘信息主程序

直接运行disk_info来获取和显示硬盘信息，保持原有的输出格式和结构。
支持命令行参数输入磁盘编号和优化的JSON配置文件读取功能。
"""

import argparse
import json
import os
import time
from typing import Any, Dict, Optional, Union
from disk_info import get_disk_info, print_disk_info

# 全局变量，用于存储用户输入的磁盘编号
USER_DISK_NUMBER = None

# 全局变量，用于存储读取的JSON配置数据
JSON_CONFIG_DATA = None

# JSON配置缓存
_JSON_CACHE = {}
_JSON_CACHE_TIME = {}
_JSON_SCHEMA_VALIDATION = True


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="磁盘信息查询工具",
        epilog="示例: python main.py --disk 3 或 python main.py -d 5 --json config.json"
    )
    
    parser.add_argument(
        '--disk', '-d',
        type=int,
        required=False,
        help='要操作的磁盘编号 (1-10)',
        metavar='NUMBER'
    )
    
    parser.add_argument(
        '--json', '-j',
        type=str,
        required=False,
        help='JSON配置文件路径',
        metavar='FILE_PATH'
    )
    
    return parser.parse_args()


def validate_json_schema(data: Any) -> bool:
    """
    验证JSON数据结构是否符合预期
    
    Args:
        data: JSON解析后的数据
        
    Returns:
        bool: 是否符合预期结构
    """
    # 基本的schema验证
    if isinstance(data, dict):
        # 检查是否包含常见的配置项
        common_keys = ['disk_number', 'partition_style', 'volume_label', 'settings']
        return any(key in data for key in common_keys)
    elif isinstance(data, list):
        return len(data) > 0  # 非空列表
    else:
        return True  # 其他类型默认通过


def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    安全获取配置值的函数
    
    Args:
        key_path: 支持点分隔的路径，如 'disk.number'
        default: 默认值
        
    Returns:
        配置值或默认值
    """
    if not JSON_CONFIG_DATA:
        return default
    
    # 处理简单的键访问
    if '.' not in key_path:
        return JSON_CONFIG_DATA.get(key_path, default)
    
    # 处理嵌套路径访问
    keys = key_path.split('.')
    current = JSON_CONFIG_DATA
    
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
    print("🗑️ JSON缓存已清空")


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
        "validation_enabled": _JSON_SCHEMA_VALIDATION,
        "cache_keys": list(_JSON_CACHE.keys())
    }


def read_json_config(json_file_path: str, use_cache: bool = True, 
                    validate_schema: bool = True) -> Optional[Dict[str, Any]]:
    """
    高性能读取并解析JSON配置文件
    
    Args:
        json_file_path: JSON文件路径
        use_cache: 是否使用缓存机制
        validate_schema: 是否进行schema验证
        
    Returns:
        解析后的JSON数据，失败时返回None
        
    Raises:
        FileNotFoundError: 当文件不存在时抛出
        json.JSONDecodeError: 当JSON格式错误时抛出
    """
    start_time = time.time()
    
    try:
        # 获取绝对路径
        abs_path = os.path.abspath(json_file_path)
        
        # 检查缓存
        if use_cache and abs_path in _JSON_CACHE:
            file_mtime = os.path.getmtime(abs_path)
            if abs_path in _JSON_CACHE_TIME and _JSON_CACHE_TIME[abs_path] == file_mtime:
                print(f"⚡ 从缓存读取JSON配置: {json_file_path}")
                return _JSON_CACHE[abs_path]
        
        # 验证文件存在性
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"JSON文件不存在: {json_file_path}")
        
        # 文件大小和类型验证
        file_size = os.path.getsize(abs_path)
        if file_size == 0:
            raise ValueError("JSON文件为空")
        elif file_size > 50 * 1024 * 1024:  # 50MB限制，提高限制
            raise ValueError(f"JSON文件过大: {file_size / (1024*1024):.2f}MB")
        
        # 检查文件扩展名
        if not abs_path.lower().endswith(('.json', '.jsonc', '.json5')):
            print(f"⚠️  警告: 文件扩展名不是标准的JSON格式: {json_file_path}")
        
        # 读取并解析JSON文件（添加重试机制）
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(abs_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # 检查JSON是否为空或只有空白字符
                if not content.strip():
                    raise ValueError("JSON文件内容为空或只包含空白字符")
                
                # 解析JSON（支持注释的JSON）
                config_data = json.loads(content)
                break
                
            except json.JSONDecodeError as e:
                if attempt == max_retries - 1:
                    raise
                print(f"JSON解析重试 {attempt + 1}/{max_retries}: {e}")
                time.sleep(0.1)
        
        # Schema验证
        if validate_schema and not validate_json_schema(config_data):
            print("⚠️  警告: JSON数据结构不符合常见配置格式")
        
        # 更新缓存
        if use_cache:
            _JSON_CACHE[abs_path] = config_data
            _JSON_CACHE_TIME[abs_path] = os.path.getmtime(abs_path)
        
        # 成功反馈
        elapsed_time = time.time() - start_time
        print(f"✅ 成功读取JSON配置文件: {json_file_path}")
        print(f"📄 文件大小: {file_size / 1024:.2f} KB | 解析时间: {elapsed_time:.3f}s")
        
        # 详细的数据结构分析
        analyze_json_structure(config_data)
        
        return config_data
        
    except FileNotFoundError as e:
        print(f"❌ 文件错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        print("   建议检查:")
        print("   - 字符串是否用双引号包围")
        print("   - 末尾逗号和不必要的逗号")
        print("   - 转义字符是否正确")
        return None
    except ValueError as e:
        print(f"❌ 文件验证错误: {e}")
        return None
    except PermissionError as e:
        print(f"❌ 权限错误: 无法读取文件 {json_file_path}")
        return None
    except Exception as e:
        print(f"❌ 读取JSON文件时发生未知错误: {e}")
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
                print(f"{indent}  📝 {key}: {value_type}")
        
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
        print(f"{indent}📝 {type(data).__name__}: {data}")


def input_user(disk_number=None):
    """
    获取用户输入的硬盘编号（支持命令行参数或交互式输入）
    
    Args:
        disk_number (int, optional): 通过命令行传入的磁盘编号
        
    Returns:
        int: 用户选择的有效磁盘编号
        
    Raises:
        ValueError: 当磁盘编号超出有效范围时抛出
    """
    if disk_number is not None:
        # 命令行参数模式
        return validate_disk_input(disk_number)
    else:
        # 交互式输入模式
        return interactive_input()


def validate_disk_input(disk_number):
    """
    验证磁盘编号输入（只允许1-10）
    
    Args:
        disk_number (int): 要验证的磁盘编号
        
    Returns:
        int: 验证通过的磁盘编号
        
    Raises:
        ValueError: 当磁盘编号不在1-10范围内时抛出
    """
    if not isinstance(disk_number, int):
        raise ValueError("磁盘编号必须是整数")
    
    if disk_number < 1 or disk_number > 10:
        raise ValueError(f"磁盘编号必须在 1-10 范围内，您输入的是: {disk_number}")
    
    return disk_number


def interactive_input():
    """
    交互式输入模式（向后兼容）
    
    Returns:
        int: 用户选择的有效磁盘编号
    """
    try:
        # 获取用户输入（简化提示）
        while True:
            try:
                disk_number = int(input("请输入磁盘编号（1-10，0退出）："))
                
                # 允许用户退出
                if disk_number == 0:
                    return None
                
                # 验证磁盘编号范围（1-10）
                if disk_number < 1 or disk_number > 10:
                    print("磁盘编号必须在 1-10 范围内，请重新输入。")
                    continue
                
                # 直接返回，不进行额外的确认和检查
                return disk_number
                    
            except ValueError:
                print("请输入一个有效的整数（1-10）。")
            except KeyboardInterrupt:
                return None
                
    except Exception as e:
        print(f"获取磁盘信息时发生错误: {e}")
        return None


def main():
    """主函数：先显示磁盘信息，然后获取用户输入"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 检查是否需要读取JSON配置文件
        global JSON_CONFIG_DATA
        if args.json:
            print("🔍 正在读取JSON配置文件...")
            JSON_CONFIG_DATA = read_json_config(args.json)
            if JSON_CONFIG_DATA is None:
                print("❌ JSON配置文件读取失败，程序退出。")
                return
            
            print("✨ JSON配置数据已加载到全局变量 JSON_CONFIG_DATA")
            print("-" * 60)
        else:
            print("ℹ️  未指定JSON配置文件，使用默认配置")
            JSON_CONFIG_DATA = {}
            print("-" * 60)
        
        # 首先获取并显示磁盘信息
        disk_data = get_disk_info()
        
        if disk_data:
            # 显示所有磁盘（保持原有表格格式）
            print_disk_info(disk_data)
            print()  # 添加空行分隔
        else:
            print("未找到任何磁盘信息。")
            return
        
        # 处理磁盘编号输入
        global USER_DISK_NUMBER
        USER_DISK_NUMBER = input_user(args.disk)
        
        if USER_DISK_NUMBER is None:
            print("未选择有效的磁盘编号，程序退出。")
            return
        
        print(f"已选择磁盘编号: {USER_DISK_NUMBER}")
        
        # 如果有JSON配置数据，显示可用的配置信息
        if JSON_CONFIG_DATA and isinstance(JSON_CONFIG_DATA, dict):
            print("📋 当前可用的配置项:")
            for key, value in JSON_CONFIG_DATA.items():
                if isinstance(value, (str, int, float)):
                    print(f"   {key}: {value}")
                elif isinstance(value, list):
                    print(f"   {key}: [列表，包含{len(value)}项]")
                elif isinstance(value, dict):
                    print(f"   {key}: {{字典，包含{len(value)}项}}")
                else:
                    print(f"   {key}: {type(value).__name__}")
            
            print("\n💡 您可以在其他函数中通过访问 JSON_CONFIG_DATA 变量来使用这些配置数据")
            
    except ValueError as e:
        print(f"输入错误: {e}")
        print("请使用 --help 查看正确的使用方法。")
    except Exception as e:
        print(f"获取磁盘信息时发生错误: {e}")
        print("请确保您有管理员权限运行此程序。")

if __name__ == "__main__":
    main()