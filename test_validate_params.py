#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 validate_input_parameters 函数的脚本
"""

import sys
import os

# 将当前目录添加到Python路径中，以便能导入partition_disk模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from partition_disk import validate_input_parameters

def test_case(description, expected, **kwargs):
    """测试用例辅助函数"""
    print(f"\n测试: {description}")
    print(f"参数: {kwargs}")
    result = validate_input_parameters(**kwargs)
    print(f"期望结果: {expected}, 实际结果: {result}")
    if result == expected:
        print("✓ 测试通过")
    else:
        print("✗ 测试失败")
    return result

def main():
    print("=" * 50)
    print("validate_input_parameters 函数测试")
    print("=" * 50)
    
    # 测试用例1: 正常参数
    test_case(
        "正常参数",
        True,
        disk_number=0,
        efi_size=200,
        efi_letter="E",
        c_size=100,
        c_letter="C",
        d_letter="D"
    )
    
    # 测试用例2: 磁盘编号无效（负数）
    test_case(
        "磁盘编号无效（负数）",
        False,
        disk_number=-1
    )
    
    # 测试用例3: 磁盘编号无效（非整数）
    test_case(
        "磁盘编号无效（非整数）",
        False,
        disk_number="0"
    )
    
    # 测试用例4: EFI分区大小无效（负数）
    test_case(
        "EFI分区大小无效（负数）",
        False,
        disk_number=0,
        efi_size=-100
    )
    
    # 测试用例5: EFI分区大小无效（非整数）
    test_case(
        "EFI分区大小无效（非整数）",
        False,
        disk_number=0,
        efi_size="200"
    )
    
    # 测试用例6: EFI盘符无效（小写字母）
    test_case(
        "EFI盘符无效（小写字母）",
        False,
        disk_number=0,
        efi_letter="e"
    )
    
    # 测试用例7: EFI盘符无效（多个字符）
    test_case(
        "EFI盘符无效（多个字符）",
        False,
        disk_number=0,
        efi_letter="EF"
    )
    
    # 测试用例8: C分区大小无效（负数）
    test_case(
        "C分区大小无效（负数）",
        False,
        disk_number=0,
        c_size=-50
    )
    
    # 测试用例9: C盘符无效（小写字母）
    test_case(
        "C盘符无效（小写字母）",
        False,
        disk_number=0,
        c_letter="c"
    )
    
    # 测试用例10: 盘符重复（C盘符重复）
    test_case(
        "盘符重复（C盘符重复）",
        False,
        disk_number=0,
        efi_letter="C",
        c_letter="C"
    )
    
    # 测试用例11: 只有必需参数
    test_case(
        "只有必需参数",
        True,
        disk_number=1
    )
    
    # 测试用例12: 多个可选参数
    test_case(
        "多个可选参数",
        True,
        disk_number=2,
        efi_size=500,
        efi_letter="S",
        c_size=200,
        c_letter="W",
        d_letter="X",
        e_letter="Y"
    )
    
    # 测试用例13: 盘符重复（其他盘符重复）
    test_case(
        "盘符重复（其他盘符重复）",
        False,
        disk_number=0,
        efi_letter="E",
        c_letter="E"
    )
    
    # 测试用例14: 使用保留盘符'C'作为EFI盘符
    test_case(
        "使用保留盘符'C'作为EFI盘符",
        False,
        disk_number=0,
        efi_letter="C"
    )
    
    # 测试用例15: 使用保留盘符'D'作为D盘符
    test_case(
        "使用保留盘符'D'作为D盘符",
        False,
        disk_number=0,
        d_letter="D"
    )
    
    # 测试用例16: 使用保留盘符'C'作为C盘符
    test_case(
        "使用保留盘符'C'作为C盘符",
        False,
        disk_number=0,
        c_letter="C"
    )
    
    # 测试用例17: 使用保留盘符'D'作为E盘符
    test_case(
        "使用保留盘符'D'作为E盘符",
        False,
        disk_number=0,
        e_letter="D"
    )
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()