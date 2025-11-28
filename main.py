#!/usr/bin/env python3
"""
main.py - 磁盘信息主程序

直接运行disk_info来获取和显示硬盘信息，保持原有的输出格式和结构。
支持命令行参数输入磁盘编号。
"""

import argparse
from disk_info import get_disk_info, print_disk_info

# 全局变量，用于存储用户输入的磁盘编号
USER_DISK_NUMBER = None


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="磁盘信息查询工具",
        epilog="示例: python main.py --disk 3 或 python main.py -d 5"
    )
    
    parser.add_argument(
        '--disk', '-d',
        type=int,
        required=False,
        help='要操作的磁盘编号 (1-10)',
        metavar='NUMBER'
    )
    
    return parser.parse_args()


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
            
    except ValueError as e:
        print(f"输入错误: {e}")
        print("请使用 --help 查看正确的使用方法。")
    except Exception as e:
        print(f"获取磁盘信息时发生错误: {e}")
        print("请确保您有管理员权限运行此程序。")

if __name__ == "__main__":
    main()