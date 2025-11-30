#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BCD Boot 修复工具
用于修复硬盘引导
"""

import os
import subprocess
import sys


def repair_boot_loader(disk_number, bcd_exe, efi_letter, c_letter):
    """
    修复硬盘引导
    
    Args:
        disk_number (int): 硬盘编号
        bcd_exe (str): bcdboot.exe文件路径
        efi_letter (str): EFI分区盘符
        c_letter (str): 系统盘符
        
    Returns:
        bool: 修复成功返回True，失败返回False
    """
    try:
        # 构建bcdboot命令
        bcdboot_command = f'"{bcd_exe}" {c_letter}:\\Windows /s {efi_letter}: /f UEFI /l zh-cn'
        
        print(f"正在执行bcdboot修复命令...")
        print(f"命令: {bcdboot_command}")
        
        # 执行bcdboot命令
        result = subprocess.run(
            bcdboot_command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='gbk'  # Windows命令行编码
        )
        
        # 检查命令执行结果
        if result.returncode != 0:
            print(f"bcdboot命令执行失败!")
            print(f"错误信息: {result.stderr}")
            return False
        
        print("bcdboot命令执行成功!")
        print(f"输出信息: {result.stdout}")
        
        # 检查EFI文件夹是否存在
        efi_path = f"{efi_letter}:\\EFI"
        if os.path.exists(efi_path):
            print(f"EFI文件夹存在: {efi_path}")
            
            # 进一步检查EFI文件夹内容
            try:
                efi_contents = os.listdir(efi_path)
                if efi_contents:
                    print(f"EFI文件夹内容: {efi_contents}")
                    return True
                else:
                    print("EFI文件夹为空，修复可能未成功")
                    return False
            except Exception as e:
                print(f"读取EFI文件夹内容时出错: {e}")
                return False
        else:
            print(f"EFI文件夹不存在: {efi_path}")
            return False
            
    except Exception as e:
        print(f"执行bcdboot修复时发生异常: {e}")
        return False


# def main():
#     """
#     主函数 - 用于测试
#     """
#     # 测试参数
#     test_disk_number = 3
#     test_bcd_exe = "d:\\sisp\\sw\\bcdboot.exe"
#     test_efi_letter = "S"
#     test_c_letter = "C"
    
#     print("开始测试bcdboot修复功能...")
#     print(f"测试参数:")
#     print(f"  硬盘编号: {test_disk_number}")
#     print(f"  bcdboot路径: {test_bcd_exe}")
#     print(f"  EFI盘符: {test_efi_letter}")
#     print(f"  系统盘符: {test_c_letter}")
#     print("-" * 50)
    
#     success = repair_boot_loader(
#         test_disk_number, 
#         test_bcd_exe, 
#         test_efi_letter, 
#         test_c_letter
#     )
    
#     if success:
#         print("\n✅ 修复成功!")
#     else:
#         print("\n❌ 修复失败!")
    
#     return success


# if __name__ == "__main__":
#     main()