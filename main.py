#!/usr/bin/env python3
"""
main.py - 磁盘信息主程序

直接运行disk_info来获取和显示硬盘信息，保持原有的输出格式和结构。
支持命令行参数输入磁盘编号和优化的JSON配置文件读取功能。
"""

import argparse
import sys
import time
from typing import Any, Dict, List, Optional
from disk_info import get_disk_info, print_disk_info
from get_user_disknumber import input_user
from common_functions import read_json_config


def pause_if_interactive(prompt: str = "请按 Enter 键退出...") -> None:
    """仅在交互终端中暂停，避免自动化场景阻塞。"""
    try:
        if sys.stdin and sys.stdin.isatty():
            input(prompt)
    except EOFError:
        pass


def parse_arguments():
    """解析命令行参数"""
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


def setup_json_config(args: argparse.Namespace) -> Dict[str, Any]:
    """设置并读取JSON配置文件"""
    if args.json:
        config_data = read_json_config(args.json)
        if config_data is None:
            print("X JSON配置文件读取失败，程序退出。")
            return {}
        else:
            if config_data and 'description' in config_data:
                print(f"成功读取JSON配置文件: {config_data['description']}")
            return config_data
    else:
        print("未指定JSON配置文件，使用默认配置。")
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
                if process.returncode != 0:
                    print(f"磁盘 {disk_number} 执行失败，退出码: {process.returncode}")
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
        except Exception as e:
            print(f"磁盘 {disk_number} 执行时发生异常: {e}")
    
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
        if not config_data:
            print("配置为空，程序退出。")
            return

        main_logic = config_data.get('main_logic')
        if not main_logic:
            print("配置缺少 main_logic 字段，程序退出。")
            return
        
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
        execute_main_logic(disk_numbers, json_path, main_logic)

        pause_if_interactive()

    except ValueError as e:
        print(f"输入错误: {e}")
        print("请使用 --help 查看正确的使用方法。")
    except Exception as e:
        print(f"获取磁盘信息时发生错误: {e}")
        print("请确保您有管理员权限运行此程序。")

if __name__ == "__main__":
    main()
