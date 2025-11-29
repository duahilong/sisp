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
import re
from typing import Any, Dict, Optional, Union, List, Tuple
from disk_info import get_disk_info, print_disk_info
from get_user_disknumber import input_user

# 全局变量，用于存储用户输入的磁盘编号列表
USER_DISK_NUMBER = []

# 全局变量，用于存储读取的JSON配置数据
JSON_CONFIG_DATA = None

# JSON配置缓存
_JSON_CACHE = {}
_JSON_CACHE_TIME = {}

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
        type=str,
        required=False,
        help='要操作的磁盘编号。支持格式：单个数字(3)、范围(1-3)、多个数字(1,3,5)、字母a(全部)',
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
        
    Raises:
        FileNotFoundError: 当文件不存在时抛出
        json.JSONDecodeError: 当JSON格式错误时抛出
    """
    start_time = time.time()  # 记录开始时间，用于性能统计
    
    try:
        # 步骤1: 路径处理
        # 获取绝对路径（包含完整目录路径），这样可以避免相对路径的问题
        abs_path = os.path.abspath(json_file_path)
        
        # 步骤2: 检查缓存机制
        # 如果启用缓存且文件已缓存，检查文件是否发生变化
        if use_cache and abs_path in _JSON_CACHE:
            file_mtime = os.path.getmtime(abs_path)  # 获取文件修改时间
            # 如果缓存时间与文件修改时间一致，说明文件未变化
            if abs_path in _JSON_CACHE_TIME and _JSON_CACHE_TIME[abs_path] == file_mtime:
                print(f"从缓存读取JSON配置: {json_file_path}")
                return _JSON_CACHE[abs_path]  # 直接返回缓存数据，避免重复读取
        
        # 步骤3: 验证文件存在性
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"JSON文件不存在: {json_file_path}")
        
        # 步骤4: 验证文件大小和类型
        file_size = os.path.getsize(abs_path)
        if file_size == 0:
            raise ValueError("JSON文件为空")
        elif file_size > 50 * 1024 * 1024:  # 50MB限制
            raise ValueError(f"JSON文件过大: {file_size / (1024*1024):.2f}MB")
        
        # 检查文件扩展名（纯格式检查，不是硬性要求）
        if not abs_path.lower().endswith(('.json', '.jsonc', '.json5')):
            print(f"警告: 文件扩展名不是标准的JSON格式: {json_file_path}")
        
        # 步骤5: 读取并解析JSON文件
        # 添加重试机制，处理可能的临时读取错误
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 读取文件内容（使用utf-8编码）
                with open(abs_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # 检查JSON是否为空或只有空白字符
                if not content.strip():
                    raise ValueError("JSON文件内容为空或只包含空白字符")
                
                # 解析JSON字符串为Python对象（字典或列表）
                config_data = json.loads(content)
                break  # 解析成功，退出重试循环
                
            except json.JSONDecodeError as e:
                # 如果是最后一次尝试，抛出异常
                if attempt == max_retries - 1:
                    raise
                # 否则打印重试信息并等待一下
                print(f"JSON解析重试 {attempt + 1}/{max_retries}: {e}")
                time.sleep(0.1)  # 等待100毫秒后重试
        
        # # 步骤6: Schema验证（可选）
        # # 注意：validate_json_schema函数已被移除，此处不再进行结构验证
        # if validate_schema:
        #     print(f"ℹ️  注意: JSON结构验证功能已被禁用。")
        
        # 步骤7: 更新缓存
        if use_cache:
            _JSON_CACHE[abs_path] = config_data  # 缓存文件内容
            _JSON_CACHE_TIME[abs_path] = os.path.getmtime(abs_path)  # 缓存文件修改时间
        
        # 步骤8: 成功反馈
        # 显示JSON文件中的description字段值，如果没有description则回退到文件名
        if config_data and 'description' in config_data:
            description = config_data.get('description', '未指定配置描述')
            print(f"成功读取JSON配置文件: {description}")
        else:
            print(f"成功读取JSON配置文件: {json_file_path}")
        
        
        return config_data  # 返回解析后的JSON数据
        
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


def main():
    """主函数：先显示磁盘信息，然后获取用户输入"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 检查是否需要读取JSON配置文件
        global JSON_CONFIG_DATA
        if args.json:
            JSON_CONFIG_DATA = read_json_config(args.json)
            if JSON_CONFIG_DATA is None:
                print(f"X JSON配置文件读取失败，程序退出。")
                return
        else:
            print("ℹ️  未指定JSON配置文件，使用默认配置，JSON_CONFIG_DATA 将为空字典。")
            JSON_CONFIG_DATA = {} # 确保在没有JSON文件时也是一个空字典
        
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
        
        # 显示用户选择的磁盘编号
        if len(USER_DISK_NUMBER) == 1:
            print(f"已选择磁盘编号: {USER_DISK_NUMBER[0]}")
        else:
            print(f"已选择磁盘编号: {', '.join(map(str, USER_DISK_NUMBER))}")
        print("=" * 60)
        # 安全地获取description，如果不存在则使用默认值
        description = JSON_CONFIG_DATA.get('description', '未指定配置描述')
        print(description)
        print(*USER_DISK_NUMBER)
            
    except ValueError as e:
        print(f"输入错误: {e}")
        print("请使用 --help 查看正确的使用方法。")
    except Exception as e:
        print(f"获取磁盘信息时发生错误: {e}")
        print("请确保您有管理员权限运行此程序。")

if __name__ == "__main__":
    main()