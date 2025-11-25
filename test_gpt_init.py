#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证 initialize_disk_to_gpt 函数功能

功能说明：
    该脚本用于测试GPT磁盘初始化功能，通过命令行参数接收配置，
    调用partition_disk.py中的initialize_disk_to_gpt函数执行GPT初始化操作。

执行流程：
    1. 解析命令行参数
    2. 验证必要参数是否提供
    3. 显示操作警告和参数信息
    4. 调用GPT初始化函数执行操作
    5. 根据执行结果输出简洁信息（成功）或详细错误信息（失败）

使用方法：
    python test_gpt_init.py --disk_number 2 --efi_size 200 --efi_letter P

命令行参数说明：
    --disk_number   磁盘编号 (必填) - 要操作的磁盘编号，例如：0, 1, 2, 3 等
    --efi_size      EFI分区大小 (可选) - EFI分区大小(MB)，例如：100, 200, 512 等
    --efi_letter    EFI分区盘符 (可选) - EFI分区的盘符，例如：'S', 'T', 'Z' 等
                    注意：不能使用 C, D 这两个保留盘符

注意事项：
    - 此脚本会清除选定磁盘上的所有数据，请谨慎操作
    - 请确保以管理员权限运行此脚本
    - 请确保磁盘编号正确，避免误操作
"""

import sys
import os
import traceback
import argparse  # 用于解析命令行参数

# 添加当前目录到Python路径，以便导入我们的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from partition_disk import initialize_disk_to_gpt

def test_gpt_initialization(disk_number, efi_size=None, efi_letter=None):
    """
    测试GPT初始化函数
    
    参数:
        disk_number (int): 要操作的磁盘编号
        efi_size (int, optional): EFI分区大小(MB)
        efi_letter (str, optional): EFI分区盘符
    
    返回:
        bool: GPT初始化是否成功
    """
    
    print("=" * 60)
    print("GPT磁盘初始化测试")
    print("=" * 60)
    print(f"测试参数:")
    print(f"  - 磁盘编号: {disk_number}")
    print(f"  - EFI分区大小: {efi_size} MB")
    print(f"  - EFI分区盘符: {efi_letter}")
    print("-" * 60)
    
    # 显示重要警告信息
    print("⚠️  重要警告:")
    print("  此操作将清除选定磁盘上的所有数据！")
    print("  请确保以管理员权限运行此脚本")
    print("  请确保磁盘编号正确")
    print("-" * 60)
    
    print("开始执行GPT初始化...")
    
    try:
        # 调用GPT初始化函数执行操作
        result = initialize_disk_to_gpt(
            disk_number=disk_number,
            efi_size=efi_size,
            efi_letter=efi_letter
        )
        
        print("-" * 60)
        if result:
            # 成功时输出简洁信息
            print(f"✅ 磁盘 {disk_number} GPT初始化成功")
        else:
            # 失败时输出详细错误信息
            print(f"❌ 磁盘 {disk_number} GPT初始化失败")
            print("  可能原因:")
            print("  - 磁盘编号错误")
            print("  - 权限不足（未以管理员身份运行）")
            print("  - 磁盘正在被使用")
            print("  - 磁盘硬件问题")
            
        return result
        
    except Exception as e:
        # 发生异常时输出完整错误信息
        print(f"❌ 执行过程中发生异常: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()  # 输出完整的堆栈跟踪
        print("\n异常类型:", type(e).__name__)
        print("异常信息:", str(e))
        return False

def main():
    """
    主函数
    负责解析命令行参数并调用测试函数
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="GPT磁盘初始化测试脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例用法：python test_gpt_init.py --disk_number 2 --efi_size 200 --efi_letter P"
    )
    
    # 添加命令行参数
    parser.add_argument(
        "--disk_number",
        type=int,
        required=True,
        help="磁盘编号（必填）- 要操作的磁盘编号，例如：0, 1, 2, 3 等"
    )
    
    parser.add_argument(
        "--efi_size",
        type=int,
        help="EFI分区大小（可选）- EFI分区大小(MB)，例如：100, 200, 512 等"
    )
    
    parser.add_argument(
        "--efi_letter",
        type=str,
        help="EFI分区盘符（可选）- EFI分区的盘符，例如：'S', 'T', 'Z' 等\n注意：不能使用 C, D 这两个保留盘符"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 执行测试函数，传入解析后的参数
    test_gpt_initialization(
        disk_number=args.disk_number,
        efi_size=args.efi_size,
        efi_letter=args.efi_letter
    )

if __name__ == "__main__":
    main()