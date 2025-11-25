#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动测试 validate_input_parameters 函数的脚本
可以通过命令行参数传递参数进行测试

使用方法:
python manual_test_params.py --disk_number 0 --efi_size 200 --efi_letter E --c_size 100 --c_letter C --d_letter D
"""

import sys
import os
import argparse

# 将当前目录添加到Python路径中，以便能导入partition_disk模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from partition_disk import validate_input_parameters
from disk_info import DiskManager

def main():
    parser = argparse.ArgumentParser(description='手动测试 validate_input_parameters 函数')
    parser.add_argument('--disk_number', type=int, required=True, help='磁盘编号（必需，非负整数）')
    parser.add_argument('--efi_size', type=int, help='EFI分区大小(MB)（正整数）')
    parser.add_argument('--efi_letter', type=str, help='EFI分区盘符（单个大写字母）')
    parser.add_argument('--c_size', type=int, help='C分区大小(MB)（正整数）')
    parser.add_argument('--c_letter', type=str, help='C分区盘符（单个大写字母）')
    parser.add_argument('--d_letter', type=str, help='D分区盘符（单个大写字母）')
    parser.add_argument('--e_letter', type=str, help='E分区盘符（单个大写字母）')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("手动测试 validate_input_parameters 函数")
    print("=" * 50)
    
    # 显示磁盘信息
    try:
        disk_manager = DiskManager()
        disk_info = disk_manager.get_disk_by_index(args.disk_number)
        if disk_info:
            print(f"磁盘 {args.disk_number} 信息: {disk_info.capacity} - {disk_info.name}")
        else:
            print(f"未找到磁盘 {args.disk_number}")
    except Exception as e:
        print(f"获取磁盘信息时出错: {e}")
    
    print("\n输入参数:")
    for arg, value in vars(args).items():
        print(f"  {arg}: {value}")
    
    print("\n开始验证...")
    result = validate_input_parameters(
        disk_number=args.disk_number,
        efi_size=args.efi_size,
        efi_letter=args.efi_letter,
        c_size=args.c_size,
        c_letter=args.c_letter,
        d_letter=args.d_letter,
        e_letter=args.e_letter
    )
    
    print(f"\n验证结果: {'通过' if result else '失败'}")
    print("=" * 50)

if __name__ == "__main__":
    main()