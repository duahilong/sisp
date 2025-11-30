number_list = [
    {
        "disk_number": 1,
        "efi_letter": "E",
        "c_letter": "F",
        "d_letter": "G",
        "e_letter": "H",
    },
    {
        "disk_number": 2,
        "efi_letter": "I",
        "c_letter": "J",
        "d_letter": "K",
        "e_letter": "L",
    },
    {
        "disk_number": 3,
        "efi_letter": "M",
        "c_letter": "N",
        "d_letter": "O",
        "e_letter": "P",
    },
    {
        "disk_number": 4,
        "efi_letter": "Q",
        "c_letter": "R",
        "d_letter": "S",
        "e_letter": "T",
    },
    {
        "disk_number": 5,
        "efi_letter": "U",
        "c_letter": "V",
        "d_letter": "W",
        "e_letter": "X",
    },
    {
        "disk_number": 6,
        "efi_letter": "Y",
        "c_letter": "Z",
        "d_letter": "A",
        "e_letter": "B",
    },
]

def get_disk_labels(data_list, target_disk_number):
    """
    根据传入的 disk_number 查找对应的记录，并返回其 efi_letter, c_letter, d_letter, e_letter 的值。

    Args:
        data_list (list): 包含磁盘记录字典的列表。
        target_disk_number (int): 目标磁盘的编号。

    Returns:
        tuple or None: 
            如果找到记录，返回一个包含 (efi_label, c_label, d_label, e_label) 的元组。
            如果未找到记录，返回 None。
    """
    
    # 1. 遍历列表，查找匹配的记录
    for record in data_list:
        if record.get("disk_number") == target_disk_number:
            
            # 2. 如果找到匹配项，提取所需的四个标签值
            efi = record.get("efi_letter")
            c = record.get("c_letter")
            d = record.get("d_letter")
            e = record.get("e_letter")
            
            # 3. 将这四个值打包成一个元组 (tuple) 返回
            return (efi, c, d, e)
            
    # 4. 如果循环结束仍未找到，则返回 None
    return None

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁盘处理工作流程模块
整合单个和多个磁盘处理功能

作者: SISP团队
版本: 2.0
"""

import os
import subprocess
import sys
import threading
import time
from typing import Union, List


def unified_disk_processing(
    disk_numbers: Union[int, List[int]], 
    win_gho: str, 
    efi_size: int, 
    c_size: int,
    gho_exe: str = "sw\\ghost64.exe"
) -> Union[bool, dict]:
    """
    统一的磁盘处理工作流程函数 - 整合版
    
    该函数是整个磁盘处理的统一入口，既可以处理单个磁盘，也可以批量处理多个磁盘。
    智能检测传入的disk_numbers参数类型，自动选择处理模式。
    
    Args:
        disk_numbers (Union[int, List[int]]): 
            - 单个磁盘编号 (int): 例如 3
            - 多个磁盘编号列表 (List[int]): 例如 [2, 3, 4]
        win_gho (str): Windows镜像文件路径
        efi_size (int): EFI分区大小（MB）
        c_size (int): C分区大小（MB）
        gho_exe (str, optional): Ghost可执行文件路径，默认使用 "sw\\ghost64.exe"
    
    Returns:
        Union[bool, dict]: 
            - 单个磁盘处理时返回 bool: True成功/False失败
            - 多个磁盘处理时返回 dict: {磁盘编号: 成功状态}
        
    Note:
        - 所有硬盘盘符信息都通过 get_disk_labels() 函数统一查询
        - 盘符配置基于 number_list 中的预设值
        - 当前置步骤失败时，后续步骤不会执行
        - 批量处理时，每个磁盘独立处理，失败不影响其他磁盘
    """
    
    # 检测输入参数类型，自动选择处理模式
    if isinstance(disk_numbers, int):
        # 单个磁盘处理模式
        return _process_single_disk_workflow(
            disk_number=disk_numbers,
            win_gho=win_gho,
            efi_size=efi_size,
            c_size=c_size,
            gho_exe=gho_exe
        )
    elif isinstance(disk_numbers, list):
        # 多个磁盘处理模式
        return _process_multiple_disks_workflow(
            disk_numbers=disk_numbers,
            win_gho=win_gho,
            efi_size=efi_size,
            c_size=c_size,
            gho_exe=gho_exe
        )
    else:
        raise ValueError(f"disk_numbers 必须是 int 或 List[int] 类型，实际是 {type(disk_numbers).__name__}")


def _process_single_disk_workflow(
    disk_number: int, 
    win_gho: str, 
    efi_size: int, 
    c_size: int,
    gho_exe: str = "sw\\ghost64.exe"
) -> bool:
    """
    内部函数：单个磁盘的完整处理流程
    
    Args:
        disk_number (int): 磁盘编号
        win_gho (str): Windows镜像文件路径
        efi_size (int): EFI分区大小（MB）
        c_size (int): C分区大小（MB）
        gho_exe (str): Ghost可执行文件路径
    
    Returns:
        bool: 整个流程执行成功返回True，失败返回False
    """
    
    print(f"=== 开始磁盘 {disk_number} 的完整处理流程 ===")
    
    try:
        # 1. 通过统一函数获取所有盘符信息
        result = get_disk_labels(number_list, disk_number)
        if not result:
            print(f"❌ 错误: 未找到磁盘编号 {disk_number} 的预设标签配置")
            return False
        
        # 解包获取到的盘符信息
        efi_letter, c_letter, d_letter, e_letter = result
        
        # 显示即将使用的配置信息
        print(f"📋 磁盘 {disk_number} 配置信息:")
        print(f"  实际传入磁盘编号: {disk_number - 1} (disk_number - 1)")
        print(f"  EFI分区: {efi_size}MB, 盘符: {efi_letter}")
        print(f"  C分区: {c_size}MB, 盘符: {c_letter}")
        print(f"  D分区: 盘符: {d_letter}")
        print(f"  E分区: 盘符: {e_letter}")
        print(f"  镜像文件: {win_gho}")
        print(f"  Ghost程序: {gho_exe}")
        print("-" * 50)
        
        # 2. 导入必要的模块
        try:
            from partition_disk import (
                initialize_disk_to_gpt,
                initialize_disk_to_partitioning_C,
                initialize_disk_to_partitioning_D,
                initialize_disk_to_partitioning_E
            )
            from call_ghost import call_ghost
        except ImportError as e:
            print(f"❌ 错误: 无法导入必要的模块: {e}")
            return False
        
        # 3. 按顺序执行磁盘处理步骤
        
        # 步骤1: 初始化磁盘为GPT格式
        print("步骤 1/5: 初始化磁盘为GPT格式...")
        result_gpt = initialize_disk_to_gpt(disk_number - 1, efi_size, efi_letter)
        if not result_gpt:
            print("❌ 步骤 1 失败: 磁盘GPT初始化失败，流程终止")
            return False
        print("✅ 步骤 1 成功: 磁盘GPT初始化完成")
        print()
        
        # 步骤2: 创建C分区
        print("步骤 2/5: 创建C分区...")
        result_c = initialize_disk_to_partitioning_C(disk_number - 1, c_size, c_letter)
        if not result_c:
            print("❌ 步骤 2 失败: C分区创建失败，流程终止")
            return False
        print("✅ 步骤 2 成功: C分区创建完成")
        print()
        
        # 步骤3: 创建D分区
        print("步骤 3/5: 创建D分区...")
        result_d = initialize_disk_to_partitioning_D(disk_number - 1, d_letter, efi_size, c_size)
        if not result_d:
            print("❌ 步骤 3 失败: D分区创建失败，流程终止")
            return False
        print("✅ 步骤 3 成功: D分区创建完成")
        print()
        
        # 步骤4: 创建E分区
        print("步骤 4/5: 创建E分区...")
        result_e = initialize_disk_to_partitioning_E(disk_number - 1, e_letter)
        if not result_e:
            print("❌ 步骤 4 失败: E分区创建失败，流程终止")
            return False
        print("✅ 步骤 4 成功: E分区创建完成")
        print()
        
        # 步骤5: 调用Ghost镜像烧录
        print("步骤 5/5: 开始Ghost镜像烧录...")
        result_ghost = call_ghost(disk_number, gho_exe, win_gho, c_letter)
        if not result_ghost:
            print("❌ 步骤 5 失败: Ghost镜像烧录失败")
            return False
        print("✅ 步骤 5 成功: Ghost镜像烧录完成")
        print()
        
        # 6. 整个流程成功完成
        print("🎉 恭喜！所有步骤都成功完成")
        print(f"磁盘 {disk_number} 的完整处理流程执行成功！")
        return True
        
    except Exception as e:
        print(f"❌ 执行过程中发生未知错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return False


def test_process_parameters(
    disk_number: int, 
    win_gho: str, 
    efi_size: int, 
    c_size: int,
    gho_exe: str = "sw\\ghost64.exe"
) -> dict:
    """
    测试函数：接收并打印所有传入的参数
    
    该函数用于调试和验证参数传递，确保所有参数都能正确接收和显示。
    参数与 process_disk_workflow 函数保持一致。
    
    Args:
        disk_number (int): 磁盘编号
        win_gho (str): Windows镜像文件路径
        efi_size (int): EFI分区大小（MB）
        c_size (int): C分区大小（MB）
        gho_exe (str, optional): Ghost可执行文件路径，默认使用 "sw\\ghost64.exe"
    
    Returns:
        dict: 包含所有接收参数的字典
        
    Note:
        - 该函数不会执行实际的磁盘操作
        - 仅用于测试参数传递和验证参数格式
    """
    
    print("🧪 测试函数：参数接收验证")
    print("=" * 50)
    
    # 创建一个参数字典来存储和返回
    parameters = {
        "disk_number": disk_number,
        "win_gho": win_gho,
        "efi_size": efi_size,
        "c_size": c_size,
        "gho_exe": gho_exe
    }
    
    # 打印所有参数
    print("📋 接收到的参数详情:")
    print(f"  磁盘编号 (disk_number): {disk_number} (类型: {type(disk_number).__name__})")
    print(f"  镜像文件路径 (win_gho): '{win_gho}' (类型: {type(win_gho).__name__})")
    print(f"  EFI分区大小 (efi_size): {efi_size}MB (类型: {type(efi_size).__name__})")
    print(f"  C分区大小 (c_size): {c_size}MB (类型: {type(c_size).__name__})")
    print(f"  Ghost程序路径 (gho_exe): '{gho_exe}' (类型: {type(gho_exe).__name__})")
    
    print("\n🔍 参数验证:")
    
    # 参数类型验证
    type_checks = []
    if not isinstance(disk_number, int):
        type_checks.append(f"❌ disk_number 应该是 int 类型，实际是 {type(disk_number).__name__}")
    else:
        type_checks.append("✅ disk_number 类型正确")
        
    if not isinstance(win_gho, str):
        type_checks.append(f"❌ win_gho 应该是 str 类型，实际是 {type(win_gho).__name__}")
    else:
        type_checks.append("✅ win_gho 类型正确")
        
    if not isinstance(efi_size, int):
        type_checks.append(f"❌ efi_size 应该是 int 类型，实际是 {type(efi_size).__name__}")
    else:
        type_checks.append("✅ efi_size 类型正确")
        
    if not isinstance(c_size, int):
        type_checks.append(f"❌ c_size 应该是 int 类型，实际是 {type(c_size).__name__}")
    else:
        type_checks.append("✅ c_size 类型正确")
        
    if not isinstance(gho_exe, str):
        type_checks.append(f"❌ gho_exe 应该是 str 类型，实际是 {type(gho_exe).__name__}")
    else:
        type_checks.append("✅ gho_exe 类型正确")
    
    for check in type_checks:
        print(f"  {check}")
    
    # 参数合理性检查
    print("\n📏 参数合理性检查:")
    logic_checks = []
    
    if disk_number <= 0:
        logic_checks.append("⚠️  disk_number 应该大于0")
    else:
        logic_checks.append("✅ disk_number 数值合理")
        
    if efi_size <= 0:
        logic_checks.append("⚠️  efi_size 应该大于0")
    elif efi_size < 100:
        logic_checks.append("⚠️  efi_size 可能过小（建议至少100MB）")
    else:
        logic_checks.append("✅ efi_size 数值合理")
        
    if c_size <= 0:
        logic_checks.append("⚠️  c_size 应该大于0")
    elif c_size < 1000:
        logic_checks.append("⚠️  c_size 可能过小（建议至少1000MB）")
    else:
        logic_checks.append("✅ c_size 数值合理")
        
    if not win_gho:
        logic_checks.append("⚠️  win_gho 不应该为空")
    else:
        logic_checks.append("✅ win_gho 路径有效")
        
    if not gho_exe:
        logic_checks.append("⚠️  gho_exe 不应该为空")
    else:
        logic_checks.append("✅ gho_exe 路径有效")
    
    for check in logic_checks:
        print(f"  {check}")
    
    print("\n" + "=" * 50)
    print("✅ 参数接收测试完成")
    print(f"返回值: {parameters}")
    
    return parameters


def process_disk_workflow(
    disk_number: int, 
    win_gho: str, 
    efi_size: int, 
    c_size: int,
    gho_exe: str = "sw\\ghost64.exe"
) -> bool:
    """
    统一的磁盘处理工作流程函数
    
    该函数是整个磁盘处理的核心入口，自动从预设配置中获取所有盘符信息，
    并按顺序执行完整的磁盘分区和镜像烧录流程。
    
    Args:
        disk_number (int): 磁盘编号
        win_gho (str): Windows镜像文件路径
        efi_size (int): EFI分区大小（MB）
        c_size (int): C分区大小（MB）
        gho_exe (str, optional): Ghost可执行文件路径，默认使用 "sw\\ghost64.exe"
    
    Returns:
        bool: 整个流程执行成功返回True，失败返回False
        
    Note:
        - 所有硬盘盘符信息都通过 get_disk_labels() 函数统一查询
        - 盘符配置基于 number_list 中的预设值
        - 当前置步骤失败时，后续步骤不会执行
    """
    
    print(f"=== 开始磁盘 {disk_number} 的完整处理流程 ===")
    
    try:
        # 1. 通过统一函数获取所有盘符信息
        result = get_disk_labels(number_list, disk_number)
        if not result:
            print(f"❌ 错误: 未找到磁盘编号 {disk_number} 的预设标签配置")
            return False
        
        # 解包获取到的盘符信息
        efi_letter, c_letter, d_letter, e_letter = result
        
        # 显示即将使用的配置信息
        print(f"📋 磁盘 {disk_number} 配置信息:")
        print(f"  实际传入磁盘编号: {disk_number - 1} (disk_number - 1)")
        print(f"  EFI分区: {efi_size}MB, 盘符: {efi_letter}")
        print(f"  C分区: {c_size}MB, 盘符: {c_letter}")
        print(f"  D分区: 盘符: {d_letter}")
        print(f"  E分区: 盘符: {e_letter}")
        print(f"  镜像文件: {win_gho}")
        print(f"  Ghost程序: {gho_exe}")
        print("-" * 50)
        
        # 2. 导入必要的模块
        try:
            from partition_disk import (
                initialize_disk_to_gpt,
                initialize_disk_to_partitioning_C,
                initialize_disk_to_partitioning_D,
                initialize_disk_to_partitioning_E
            )
            from call_ghost import call_ghost
        except ImportError as e:
            print(f"❌ 错误: 无法导入必要的模块: {e}")
            return False
        
        # 3. 按顺序执行磁盘处理步骤
        
        # 步骤1: 初始化磁盘为GPT格式
        print("步骤 1/5: 初始化磁盘为GPT格式...")
        result_gpt = initialize_disk_to_gpt(disk_number - 1, efi_size, efi_letter)
        if not result_gpt:
            print("❌ 步骤 1 失败: 磁盘GPT初始化失败，流程终止")
            return False
        print("✅ 步骤 1 成功: 磁盘GPT初始化完成")
        print()
        
        # 步骤2: 创建C分区
        print("步骤 2/5: 创建C分区...")
        result_c = initialize_disk_to_partitioning_C(disk_number - 1, c_size, c_letter)
        if not result_c:
            print("❌ 步骤 2 失败: C分区创建失败，流程终止")
            return False
        print("✅ 步骤 2 成功: C分区创建完成")
        print()
        
        # 步骤3: 创建D分区
        print("步骤 3/5: 创建D分区...")
        result_d = initialize_disk_to_partitioning_D(disk_number - 1, d_letter, efi_size, c_size)
        if not result_d:
            print("❌ 步骤 3 失败: D分区创建失败，流程终止")
            return False
        print("✅ 步骤 3 成功: D分区创建完成")
        print()
        
        # 步骤4: 创建E分区
        print("步骤 4/5: 创建E分区...")
        result_e = initialize_disk_to_partitioning_E(disk_number - 1, e_letter)
        if not result_e:
            print("❌ 步骤 4 失败: E分区创建失败，流程终止")
            return False
        print("✅ 步骤 4 成功: E分区创建完成")
        print()
        
        # 步骤5: 调用Ghost镜像烧录
        print("步骤 5/5: 开始Ghost镜像烧录...")
        result_ghost = call_ghost(disk_number, gho_exe, win_gho, c_letter)
        if not result_ghost:
            print("❌ 步骤 5 失败: Ghost镜像烧录失败")
            return False
        print("✅ 步骤 5 成功: Ghost镜像烧录完成")
        print()
        
        # 6. 整个流程成功完成
        print("🎉 恭喜！所有步骤都成功完成")
        print(f"磁盘 {disk_number} 的完整处理流程执行成功！")
        return True
        
    except Exception as e:
        print(f"❌ 执行过程中发生未知错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return False


def process_multiple_disks(
    disk_numbers: list[int], 
    win_gho: str, 
    efi_size: int, 
    c_size: int,
    gho_exe: str = "sw\\ghost64.exe"
) -> dict:
    """
    批量处理多个磁盘的工作流程函数
    
    该函数可以同时处理多个磁盘，为每个磁盘执行完整的分区和镜像烧录流程。
    
    Args:
        disk_numbers (list[int]): 磁盘编号列表，例如 [2, 3, 4]
        win_gho (str): Windows镜像文件路径
        efi_size (int): EFI分区大小（MB）
        c_size (int): C分区大小（MB）
        gho_exe (str, optional): Ghost可执行文件路径，默认使用 "sw\\ghost64.exe"
    
    Returns:
        dict: 包含每个磁盘处理结果的字典，格式为 {磁盘编号: 成功状态}
              例如: {2: True, 3: False, 4: True}
        
    Note:
        - 每个磁盘独立处理，一个磁盘失败不会影响其他磁盘
        - 盘符配置基于 number_list 中的预设值
        - 函数会尝试处理所有指定的磁盘编号
    """
    
    print(f"=== 开始批量处理 {len(disk_numbers)} 个磁盘 ===")
    print(f"目标磁盘: {disk_numbers}")
    print("=" * 60)
    
    # 存储每个磁盘的处理结果
    results = {}
    
    for i, disk_number in enumerate(disk_numbers, 1):
        print(f"\n🔄 [{i}/{len(disk_numbers)}] 开始处理磁盘 {disk_number}")
        print("-" * 60)
        
        try:
            # 调用单个磁盘处理函数
            success = process_disk_workflow(
                disk_number=disk_number,
                win_gho=win_gho,
                efi_size=efi_size,
                c_size=c_size,
                gho_exe=gho_exe
            )
            
            # 记录结果
            results[disk_number] = success
            
            if success:
                print(f"✅ 磁盘 {disk_number} 处理成功")
            else:
                print(f"❌ 磁盘 {disk_number} 处理失败")
                
        except Exception as e:
            print(f"❌ 磁盘 {disk_number} 处理时发生错误: {e}")
            results[disk_number] = False
    
    # 打印批量处理总结
    print("\n" + "=" * 60)
    print("📊 批量处理总结:")
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"总磁盘数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    print("\n详细结果:")
    for disk_num, result in results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"  磁盘 {disk_num}: {status}")
    
    return results


def _process_multiple_disks_workflow(
    disk_numbers: List[int], 
    win_gho: str, 
    efi_size: int, 
    c_size: int,
    gho_exe: str = "sw\\ghost64.exe"
) -> dict:
    """
    内部函数：批量处理多个磁盘的工作流程
    
    Args:
        disk_numbers (List[int]): 磁盘编号列表
        win_gho (str): Windows镜像文件路径
        efi_size (int): EFI分区大小（MB）
        c_size (int): C分区大小（MB）
        gho_exe (str): Ghost可执行文件路径
    
    Returns:
        dict: 包含每个磁盘处理结果的字典，格式为 {磁盘编号: 成功状态}
    """
    
    print(f"=== 开始批量处理 {len(disk_numbers)} 个磁盘 ===")
    print(f"目标磁盘: {disk_numbers}")
    print("=" * 60)
    
    # 存储每个磁盘的处理结果
    results = {}
    
    for i, disk_number in enumerate(disk_numbers, 1):
        print(f"\n🔄 [{i}/{len(disk_numbers)}] 开始处理磁盘 {disk_number}")
        print("-" * 60)
        
        try:
            # 调用单个磁盘处理函数
            success = _process_single_disk_workflow(
                disk_number=disk_number,
                win_gho=win_gho,
                efi_size=efi_size,
                c_size=c_size,
                gho_exe=gho_exe
            )
            
            # 记录结果
            results[disk_number] = success
            
            if success:
                print(f"✅ 磁盘 {disk_number} 处理成功")
            else:
                print(f"❌ 磁盘 {disk_number} 处理失败")
                
        except Exception as e:
            print(f"❌ 磁盘 {disk_number} 处理时发生错误: {e}")
            results[disk_number] = False
    
    # 打印批量处理总结
    print("\n" + "=" * 60)
    print("📊 批量处理总结:")
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"总磁盘数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    print("\n详细结果:")
    for disk_num, result in results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"  磁盘 {disk_num}: {status}")
    
    return results


def get_disk_config(disk_number: int) -> dict:
    """
    获取指定磁盘的完整配置信息
    
    Args:
        disk_number (int): 磁盘编号
    
    Returns:
        dict: 包含磁盘配置信息的字典，如果磁盘编号不存在则返回空字典
    """
    result = get_disk_labels(number_list, disk_number)
    if result:
        efi_letter, c_letter, d_letter, e_letter = result
        return {
            "disk_number": disk_number,
            "efi_letter": efi_letter,
            "c_letter": c_letter,
            "d_letter": d_letter,
            "e_letter": e_letter
        }
    return {}


# 示例代码和使用指南
if __name__ == "__main__":
    print("🚀 磁盘处理工作流程 - 使用示例")
    print("=" * 60)
    
    # 示例1: 测试函数 - 参数接收验证
    print("🧪 示例1: 测试函数 - 参数接收验证")
    print("验证 test_process_parameters 函数能否正确接收和处理参数...")
    
    # 调用测试函数
    test_result = test_process_parameters(
        disk_number=3,               # 磁盘编号
        win_gho="img\\test.GHO",  # Windows镜像文件路径
        efi_size=512,               # EFI分区大小（MB）
        c_size=50000,               # C分区大小（MB）
        gho_exe="sw\\ghost64.exe"   # Ghost可执行文件路径（可选，默认值）
    )
    
    print(f"\n测试函数返回值: {test_result}")
    
    print("\n" + "=" * 60)
    
    # 示例2: 统一处理函数使用示例（单磁盘）
    print("🚀 示例2: 统一处理函数使用示例（单磁盘）")
    print("处理磁盘3的完整流程...")
    
    # 调用统一的处理函数
    success = process_disk_workflow(
        disk_number=3,               # 磁盘编号
        win_gho="img\\test.GHO",  # Windows镜像文件路径
        efi_size=512,               # EFI分区大小（MB）
        c_size=50000,               # C分区大小（MB）
        gho_exe="sw\\ghost64.exe"   # Ghost可执行文件路径（可选，默认值）
    )
    
    print(f"\n处理结果: {'🎉 成功' if success else '❌ 失败'}")
    
    print("\n" + "=" * 60)
    
    # 示例3: 批量处理多个磁盘
    print("🚀 示例3: 批量处理多个磁盘")
    print("同时处理磁盘2和磁盘3...")
    
    # 调用批量处理函数
    results = process_multiple_disks(
        disk_numbers=[2, 3],          # 磁盘编号列表（2个或以上）
        win_gho="img\\test.GHO",   # Windows镜像文件路径
        efi_size=512,                # EFI分区大小（MB）
        c_size=50000,                # C分区大小（MB）
        gho_exe="sw\\ghost64.exe"    # Ghost可执行文件路径（可选，默认值）
    )
    
    print(f"\n批量处理结果: {results}")
    
    print("\n" + "=" * 60)
    print("📖 使用说明:")
    print("1. 参数测试: 使用 test_process_parameters() 函数验证参数")
    print("2. 单个磁盘处理: 使用 process_disk_workflow() 函数")
    print("3. 多个磁盘处理: 使用 process_multiple_disks() 函数")
    print("4. 统一处理函数: 使用 unified_disk_processing() 函数")
    print("5. 并行处理函数: 使用 parallel_disk_processing() 函数")
    print("6. 所有硬盘盘符信息都通过 get_disk_labels() 函数统一查询")
    print("7. 只需指定 disk_number/disk_numbers, win_gho, efi_size, c_size 四个必要参数")
    print("8. gho_exe 参数可选，默认使用 'sw\\ghost64.exe'")
    print("9. 当前置步骤失败时，后续步骤不会执行")
    print("10. 调用分区函数时，disk_number 会自动减1 (disk_number - 1)")
    print("11. 批量处理时，每个磁盘独立处理，失败不影响其他磁盘")
    print("12. 并行处理时，每个磁盘在新窗口中独立运行，最大并发数可控制")


def parallel_disk_processing(
    disk_numbers: Union[int, List[int]], 
    win_gho: str, 
    efi_size: int, 
    c_size: int,
    max_concurrent: int = None,
    gho_exe: str = "sw\\ghost64.exe"
) -> dict:
    """
    并行磁盘处理工作流程函数
    
    该函数支持单个和多个磁盘的并行处理，为每个磁盘创建独立的命令行窗口。
    特别适用于使用diskpart进行磁盘操作时的并行处理场景。
    
    Args:
        disk_numbers (Union[int, List[int]]): 
            - 单个磁盘编号 (int): 例如 3
            - 多个磁盘编号列表 (List[int]): 例如 [2, 3, 4]
        win_gho (str): Windows镜像文件路径
        efi_size (int): EFI分区大小（MB）
        c_size (int): C分区大小（MB）
        max_concurrent (int, optional): 最大并发数，默认为磁盘数量和系统CPU核心数的较小值
        gho_exe (str, optional): Ghost可执行文件路径，默认使用 "sw\\ghost64.exe"
    
    Returns:
        dict: 包含每个磁盘处理结果的字典，格式为 {磁盘编号: 成功状态}
              例如: {2: True, 3: False, 4: True}
    
    Warning:
        - 并行处理可能会对系统资源造成压力
        - 建议根据磁盘类型和系统性能调整并发数
        - SSD磁盘可以支持更高并发数，机械硬盘建议降低并发数
        - 确保目标磁盘是独立的，避免数据冲突
    """
    
    # 统一处理单个磁盘的情况
    if isinstance(disk_numbers, int):
        disk_numbers = [disk_numbers]
    
    # 确定最大并发数
    if max_concurrent is None:
        # 默认为磁盘数量和CPU核心数的较小值，但不超过4
        import multiprocessing
        max_concurrent = min(len(disk_numbers), multiprocessing.cpu_count(), 4)
    
    print(f"=== 开始并行处理 {len(disk_numbers)} 个磁盘 ===")
    print(f"目标磁盘: {disk_numbers}")
    print(f"最大并发数: {max_concurrent}")
    print("=" * 60)
    
    # 创建进程锁用于线程安全的结果记录
    results_lock = threading.Lock()
    results = {}
    
    def worker_process(disk_number):
        """工作进程：处理单个磁盘"""
        try:
            print(f"🚀 [线程 {threading.current_thread().name}] 开始处理磁盘 {disk_number}")
            
            # 在新窗口中启动处理过程
            cmd = [
                "powershell", "-Command",
                f"""
                Write-Host "=== 正在处理磁盘 {disk_number} ===" -ForegroundColor Green;
                try {{
                    cd d:\\sisp;
                    python logic_processing.py --disk {disk_number} --gho {win_gho} --efi {efi_size} --csize {c_size} --ghost {gho_exe};
                    $exit_code = $? ? 0 : 1;
                    Write-Host "磁盘 {disk_number} 处理完成，退出码: $exit_code" -ForegroundColor Yellow;
                    exit $exit_code;
                }} catch {{
                    Write-Host "磁盘 {disk_number} 处理失败: $($_.Exception.Message)" -ForegroundColor Red;
                    exit 1;
                }}
                """
            ]
            
            # 启动新进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd="d:\\sisp"
            )
            
            # 等待进程完成
            stdout, stderr = process.communicate(timeout=1800)  # 30分钟超时
            
            # 判断处理结果
            success = process.returncode == 0
            
            # 记录结果（线程安全）
            with results_lock:
                results[disk_number] = success
            
            # 输出结果信息
            status = "✅ 成功" if success else "❌ 失败"
            print(f"📊 [线程 {threading.current_thread().name}] 磁盘 {disk_number}: {status}")
            
            if stderr:
                print(f"⚠️  [线程 {threading.current_thread().name}] 磁盘 {disk_number} 警告/错误:")
                print(stderr)
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ [线程 {threading.current_thread().name}] 磁盘 {disk_number} 处理超时")
            with results_lock:
                results[disk_number] = False
            return False
            
        except Exception as e:
            print(f"❌ [线程 {threading.current_thread().name}] 磁盘 {disk_number} 处理异常: {e}")
            with results_lock:
                results[disk_number] = False
            return False
    
    # 限制并发数的处理
    semaphore = threading.Semaphore(max_concurrent)
    
    def limited_worker(disk_number):
        """限制并发数的工作进程"""
        with semaphore:
            return worker_process(disk_number)
    
    # 创建并启动线程池
    threads = []
    for disk_number in disk_numbers:
        thread = threading.Thread(
            target=limited_worker, 
            args=(disk_number,),
            name=f"Disk-{disk_number}"
        )
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 打印并行处理总结
    print("\n" + "=" * 60)
    print("📊 并行处理总结:")
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"总磁盘数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    print("\n详细结果:")
    for disk_num, result in results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"  磁盘 {disk_num}: {status}")
    
    return results


def process_disk_in_subprocess(
    disk_number: int, 
    win_gho: str, 
    efi_size: int, 
    c_size: int,
    gho_exe: str = "sw\\ghost64.exe"
) -> bool:
    """
    在子进程中处理单个磁盘的辅助函数
    
    该函数被 parallel_disk_processing 函数调用，用于在独立进程中处理单个磁盘。
    
    Args:
        disk_number (int): 磁盘编号
        win_gho (str): Windows镜像文件路径
        efi_size (int): EFI分区大小（MB）
        c_size (int): C分区大小（MB）
        gho_exe (str): Ghost可执行文件路径
    
    Returns:
        bool: 整个流程执行成功返回True，失败返回False
    """
    
    try:
        # 调用单个磁盘处理函数
        return _process_single_disk_workflow(
            disk_number=disk_number,
            win_gho=win_gho,
            efi_size=efi_size,
            c_size=c_size,
            gho_exe=gho_exe
        )
    except Exception as e:
        print(f"❌ 磁盘 {disk_number} 在子进程处理时发生错误: {e}")
        return False


# 命令行接口支持
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='磁盘处理工作流程')
    parser.add_argument('--disk', type=int, help='磁盘编号')
    parser.add_argument('--gho', type=str, help='Windows镜像文件路径')
    parser.add_argument('--efi', type=int, help='EFI分区大小（MB）')
    parser.add_argument('--csize', type=int, help='C分区大小（MB）')
    parser.add_argument('--ghost', type=str, default='sw\\ghost64.exe', help='Ghost程序路径')
    parser.add_argument('--mode', type=str, choices=['single', 'parallel'], default='single', help='处理模式')
    parser.add_argument('--max-concurrent', type=int, help='最大并发数')
    
    args = parser.parse_args()
    
    if args.disk and args.gho and args.efi and args.csize:
        if args.mode == 'parallel':
            # 并行处理模式
            result = parallel_disk_processing(
                disk_numbers=[args.disk],
                win_gho=args.gho,
                efi_size=args.efi,
                c_size=args.csize,
                max_concurrent=args.max_concurrent,
                gho_exe=args.ghost
            )
        else:
            # 单个处理模式
            result = process_disk_workflow(
                disk_number=args.disk,
                win_gho=args.gho,
                efi_size=args.efi,
                c_size=args.csize,
                gho_exe=args.ghost
            )
    else:
        # 如果没有命令行参数，运行默认示例
        print("🚀 磁盘处理工作流程 - 使用示例")
        print("=" * 60)
        
        # 示例1: 测试函数
        print("🧪 示例1: 测试函数 - 参数接收验证")
        test_result = test_process_parameters(
            disk_number=3,
            win_gho="img\\test.GHO",
            efi_size=512,
            c_size=50000,
            gho_exe="sw\\ghost64.exe"
        )
        print(f"\n测试函数返回值: {test_result}")
        
        print("\n" + "=" * 60)
        
        # 示例2: 统一处理函数使用示例（单磁盘）
        print("🚀 示例2: 统一处理函数使用示例（单磁盘）")
        success = process_disk_workflow(
            disk_number=3,
            win_gho="img\\test.GHO",
            efi_size=512,
            c_size=50000,
            gho_exe="sw\\ghost64.exe"
        )
        print(f"\n处理结果: {'🎉 成功' if success else '❌ 失败'}")
        
        print("\n" + "=" * 60)
        
        # 示例3: 批量处理多个磁盘
        print("🚀 示例3: 批量处理多个磁盘")
        results = process_multiple_disks(
            disk_numbers=[2, 3],
            win_gho="img\\test.GHO",
            efi_size=512,
            c_size=50000,
            gho_exe="sw\\ghost64.exe"
        )
        print(f"\n批量处理结果: {results}")