#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 validate_input_parameters 函数的保留盘符验证功能
"""

import sys
import os

# 将当前目录添加到Python路径中，以便能导入partition_disk模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from partition_disk import validate_input_parameters

def test_efi_letter_with_reserved_c():
    """测试EFI盘符使用保留字母'C'"""
    print("测试EFI盘符使用保留字母'C':")
    result = validate_input_parameters(
        disk_number=0,
        efi_letter='C'
    )
    print(f"结果: {'通过' if result else '失败'}")
    return not result  # 应该失败

def test_c_letter_with_reserved_c():
    """测试C盘符使用保留字母'C'"""
    print("\n测试C盘符使用保留字母'C':")
    result = validate_input_parameters(
        disk_number=0,
        c_letter='C'
    )
    print(f"结果: {'通过' if result else '失败'}")
    return not result  # 应该失败

def test_d_letter_with_reserved_d():
    """测试D盘符使用保留字母'D'"""
    print("\n测试D盘符使用保留字母'D':")
    result = validate_input_parameters(
        disk_number=0,
        d_letter='D'
    )
    print(f"结果: {'通过' if result else '失败'}")
    return not result  # 应该失败

def test_e_letter_with_reserved_c():
    """测试E盘符使用保留字母'C'"""
    print("\n测试E盘符使用保留字母'C':")
    result = validate_input_parameters(
        disk_number=0,
        e_letter='C'
    )
    print(f"结果: {'通过' if result else '失败'}")
    return not result  # 应该失败

def test_valid_letters():
    """测试使用有效的非保留字母"""
    print("\n测试使用有效的非保留字母'E'作为EFI盘符:")
    result = validate_input_parameters(
        disk_number=0,
        efi_letter='E'
    )
    print(f"结果: {'通过' if result else '失败'}")
    return result  # 应该通过

def test_multiple_reserved_letters():
    """测试多个参数使用保留字母"""
    print("\n测试多个参数使用保留字母'C'和'D':")
    result = validate_input_parameters(
        disk_number=0,
        efi_letter='C',
        c_letter='D'
    )
    print(f"结果: {'通过' if result else '失败'}")
    return not result  # 应该失败

def main():
    print("=" * 50)
    print("validate_input_parameters 保留盘符验证测试")
    print("=" * 50)
    
    tests = [
        test_efi_letter_with_reserved_c,
        test_c_letter_with_reserved_c,
        test_d_letter_with_reserved_d,
        test_e_letter_with_reserved_c,
        test_valid_letters,
        test_multiple_reserved_letters
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    if passed == total:
        print("所有测试都通过了!")
    else:
        print("部分测试失败!")
    print("=" * 50)

if __name__ == "__main__":
    main()