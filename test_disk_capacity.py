#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 validate_input_parameters 函数的磁盘容量验证功能
"""

import sys
import os

# 将当前目录添加到Python路径中，以便能导入partition_disk模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from partition_disk import validate_input_parameters
from disk_info import DiskManager

def main():
    print("=" * 50)
    print("validate_input_parameters 磁盘容量验证测试")
    print("=" * 50)
    
    # 获取磁盘信息
    disk_manager = DiskManager()
    disks = disk_manager.get_disk_info()
    
    if not disks:
        print("未找到任何磁盘。")
        return
    
    # 显示所有磁盘信息
    print("\n可用磁盘:")
    for disk in disks:
        print(f"  磁盘 {disk.index}: {disk.capacity} - {disk.name}")
    
    # 选择第一个磁盘进行测试
    first_disk = disks[0]
    disk_number = first_disk.index
    
    # 解析磁盘容量
    try:
        disk_capacity_str = first_disk.capacity.replace("GB", "").strip()
        disk_capacity_gb = float(disk_capacity_str)
    except ValueError:
        print(f"无法解析磁盘 {disk_number} 的容量信息。")
        return
    
    print(f"\n选择磁盘 {disk_number} 进行测试，容量: {disk_capacity_gb} GB")
    
    # 测试用例1: C分区大小小于磁盘容量（应该通过）
    # 将GB转换为MB进行测试
    c_size_mb = int((disk_capacity_gb - 10) * 1024)
    print(f"\n测试: C分区大小 ({c_size_mb} MB / {c_size_mb/1024:.2f} GB) 小于磁盘容量 ({disk_capacity_gb} GB)")
    try:
        result = validate_input_parameters(
            disk_number=disk_number,
            c_size=c_size_mb
        )
        print(f"结果: {'通过' if result else '失败'}")
    except Exception as e:
        print(f"结果: 失败 - {e}")
    
    # 测试用例2: C分区大小等于磁盘容量（应该通过）
    c_size_mb = int(disk_capacity_gb * 1024)
    print(f"\n测试: C分区大小 ({c_size_mb} MB / {c_size_mb/1024:.2f} GB) 等于磁盘容量 ({disk_capacity_gb} GB)")
    try:
        result = validate_input_parameters(
            disk_number=disk_number,
            c_size=c_size_mb
        )
        print(f"结果: {'通过' if result else '失败'}")
    except Exception as e:
        print(f"结果: 失败 - {e}")
    
    # 测试用例3: C分区大小大于磁盘容量（应该失败）
    c_size_mb = int((disk_capacity_gb + 10) * 1024)
    print(f"\n测试: C分区大小 ({c_size_mb} MB / {c_size_mb/1024:.2f} GB) 大于磁盘容量 ({disk_capacity_gb} GB)")
    try:
        result = validate_input_parameters(
            disk_number=disk_number,
            c_size=c_size_mb
        )
        print(f"结果: {'通过' if result else '失败'}")
    except ValueError as e:
        print(f"结果: 失败 - {e}")
    except Exception as e:
        print(f"结果: 失败 - 意外异常 {type(e).__name__}: {e}")
    
    print("\n" + "=" * 50)
    print("磁盘容量验证测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()