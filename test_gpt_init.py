#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证 initialize_disk_to_gpt 函数功能

使用方法：
1. 修改下面的测试参数
2. 运行脚本：python test_gpt_init.py

注意：此脚本会执行磁盘操作，请确保：
- 以管理员权限运行
- 选择正确的磁盘编号
- 已备份重要数据
"""

import sys
import os
import traceback

# 添加当前目录到Python路径，以便导入我们的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from partition_disk import initialize_disk_to_gpt

def test_gpt_initialization():
    """
    测试GPT初始化函数
    
    在这里修改您的测试参数：
    """
    
    # ========== 测试参数配置区域 ==========
    # 请根据您的实际情况修改以下参数：
    
    # 磁盘编号 (必填) - 要操作的磁盘编号，通常是 0, 1, 2, 3 等
    DISK_NUMBER = 3
    
    # EFI分区大小 (可选) - EFI分区大小(MB)，例如：100, 200, 512 等
    EFI_SIZE = 200
    
    # EFI分区盘符 (可选) - EFI分区的盘符，例如：'S', 'T', 'Z' 等
    # 注意：不能使用 C, D 这两个保留盘符
    EFI_LETTER = 'P'
    
    # ========================================
    
    print("="*60)
    print("GPT磁盘初始化测试")
    print("="*60)
    print(f"测试参数:")
    print(f"  - 磁盘编号: {DISK_NUMBER}")
    print(f"  - EFI分区大小: {EFI_SIZE} MB")
    print(f"  - EFI分区盘符: {EFI_LETTER}")
    print("-"*60)
    
    # 警告信息
    print("⚠️  重要警告:")
    print("  此操作将清除选定磁盘上的所有数据！")
    print("  请确保以管理员权限运行此脚本")
    print("  请确保磁盘编号正确")
    print("-"*60)
    
    print("开始执行GPT初始化...")
    
    try:
        # 调用GPT初始化函数
        result = initialize_disk_to_gpt(
            disk_number=DISK_NUMBER,
            efi_size=EFI_SIZE,
            efi_letter=EFI_LETTER
        )
        
        print("-"*60)
        if result:
            print("✅ GPT初始化成功完成！")
            print(f"  磁盘 {DISK_NUMBER} 已成功转换为GPT格式")
            if EFI_SIZE and EFI_LETTER:
                print(f"  EFI分区 ({EFI_SIZE}MB, 盘符: {EFI_LETTER}) 创建完成")
        else:
            print("❌ GPT初始化失败")
            
        return result
        
    except Exception as e:
        print(f"❌ 执行过程中发生异常: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False

def main():
    """
    主函数
    """
    print("GPT磁盘初始化测试脚本")
    print("版本: 1.1")
    print("")
    
    # 直接执行测试，无需用户输入
    test_gpt_initialization()
    
    print("\n测试完成")

if __name__ == "__main__":
    main()