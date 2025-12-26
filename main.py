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
from typing import Any, Dict, List, Optional
from disk_info import get_disk_info, print_disk_info
from get_user_disknumber import input_user
# from logic_processing import all_disk_partitions, test_input,process_disk_numbers







# JSON配置缓存 - 这个保留，因为它是真正的缓存机制
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
        epilog="示例: python main.py --json config.json"
    )
    

    
    parser.add_argument(
        '--json', '-j',
        type=str,
        required=True,
        help='JSON配置文件路径',
        metavar='FILE_PATH'
    )
    
    return parser.parse_args()





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


def display_disk_information() -> Optional[List[Dict[str, Any]]]:
    """获取并显示磁盘信息
    
    Returns:
        磁盘数据列表，如果获取失败则返回None
    """
    disk_data = get_disk_info()
    
    if disk_data:
        print_disk_info(disk_data)
        print()
        return disk_data
    else:
        print("未找到任何磁盘信息。")
        return None


def handle_user_input(disk_arg: Optional[str], config_data: Dict[str, Any]) -> Optional[List[int]]:
    """处理用户磁盘编号输入
    
    Args:
        disk_arg: 命令行传递的磁盘编号参数
        config_data: JSON配置数据，用于保护硬盘验证
        
    Returns:
        解析后的磁盘编号列表，如果失败则返回None
    """
    disk_numbers = input_user(disk_arg, config_data)
    
    if disk_numbers is None:
        print("未选择有效的磁盘编号，程序退出。")
        return None
    
    if not disk_numbers:
        print("没有通过保护硬盘验证的磁盘，程序退出。")
        return None
    
    return disk_numbers


def display_selection_results(disk_numbers: List[int], config_data: Dict[str, Any]) -> None:
    """显示用户选择的结果
    
    Args:
        disk_numbers: 磁盘编号列表
        config_data: JSON配置数据
    """
    if len(disk_numbers) == 1:
        print(f"已选择磁盘编号: {disk_numbers[0]}")
    else:
        print(f"已选择磁盘编号: {', '.join(map(str, disk_numbers))}")
    
    print("=" * 60)
    description = config_data.get('description', '未指定配置描述')
    print(description)
    print(*disk_numbers)


def execute_main_logic(disk_numbers: List[int], json_path: str, main_logic: str) -> None:
    """根据磁盘编号列表多次执行main_logic程序
    
    Args:
        disk_numbers: 磁盘编号列表
        json_path: JSON配置文件路径
        main_logic: 可执行程序路径
    """
    import subprocess
    import sys
    import os
    import threading
    
    # 转换为绝对路径
    main_logic_abs = os.path.abspath(main_logic)
    json_path_abs = os.path.abspath(json_path)
    
    def run_single_disk(disk_number: int, delay_seconds: int) -> None:
        """执行单个磁盘的程序
        
        Args:
            disk_number: 磁盘编号
            delay_seconds: 启动前的延迟秒数
        """
        # 延迟启动
        if delay_seconds > 0:
            print(f"等待 {delay_seconds} 秒后启动磁盘 {disk_number}...")
            time.sleep(delay_seconds)
        
        print(f"执行 {main_logic_abs} -d {disk_number} -j {json_path_abs}")
        try:
            if sys.platform == "win32":
                # Windows环境下开启新窗口执行
                process = subprocess.Popen(
                    [main_logic_abs, "-d", str(disk_number), "-j", json_path_abs],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                # 等待8秒，给程序初始化时间
                time.sleep(8)
                # 等待程序执行完成
                process.wait()
            else:
                # 非Windows环境使用原有方式
                subprocess.run(
                    [main_logic_abs, "-d", str(disk_number), "-j", json_path_abs],
                    check=True
                )
        except subprocess.CalledProcessError as e:
            print(f"磁盘 {disk_number} 执行失败: {e}")
        except FileNotFoundError:
            print(f"错误: 找不到程序 {main_logic_abs}")
    
    # 使用线程池错开时间启动所有磁盘操作
    threads = []
    for index, disk_number in enumerate(disk_numbers):
        # 每个磁盘延迟启动的时间：索引 * 8秒
        delay = index * 8
        thread = threading.Thread(target=run_single_disk, args=(disk_number, delay))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()


def main():
    """主函数：协调各个子功能模块"""
    try:
        # 解析命令行参数
        args = parse_arguments()
    
        # 设置JSON配置
        config_data = setup_json_config(args)
        json_path = args.json
        print(f"JSON配置文件路径: {json_path}")
        main_logic = config_data.get('main_logic')
        print( main_logic )
        
        # 显示磁盘信息
        disk_data = display_disk_information()
        if disk_data is None:
            return
        
        # 处理用户输入（传递配置数据进行保护硬盘验证）
        disk_numbers = handle_user_input(None, config_data)
        if disk_numbers is None:
            return
        
        # 显示选择结果
        display_selection_results(disk_numbers, config_data)
        print(disk_numbers)
        execute_main_logic(disk_numbers, json_path, main_logic)

        input("请按 Enter 键退出...")

    except ValueError as e:
        print(f"输入错误: {e}")
        print("请使用 --help 查看正确的使用方法。")
    except Exception as e:
        print(f"获取磁盘信息时发生错误: {e}")
        print("请确保您有管理员权限运行此程序。")

if __name__ == "__main__":
    main()