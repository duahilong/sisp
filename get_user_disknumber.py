#!/usr/bin/env python3
"""
get_user_disknumber.py - 用户磁盘编号输入处理模块

专门处理用户磁盘编号输入的相关功能，包括：
- 解析多种格式的磁盘编号输入
- 验证磁盘编号的有效性
- 支持命令行参数和交互式输入
"""

import re
from typing import List, Union

# 预编译正则表达式模式 - 提升性能
# 用于分割逗号和空格分隔的磁盘编号输入
SPLIT_PATTERN = re.compile(r'[,\s]+')


def parse_disk_input(input_str: str) -> List[int]:
    """
    解析磁盘编号输入字符串，支持多种格式
    
    Args:
        input_str: 输入字符串，支持以下格式：
                  - 单个数字: "3"
                  - 范围: "1-3", "3-6"
                  - 多个数字: "1,3,5" 或 "1 3 5"
                  - 混合格式: "1,3-5,6" 或 "1 3-5 6" (数字+范围)
                  - 字母a: "a" (表示全部1-6)
    
    Returns:
        List[int]: 解析后的磁盘编号列表
        
    Raises:
        ValueError: 当输入格式不正确或超出范围时抛出
    """
    if not input_str or not input_str.strip():
        raise ValueError("输入不能为空")
    
    input_str = input_str.strip().lower()
    
    # 处理字母'a'表示全部
    if input_str == 'a' or input_str == 'all':
        return list(range(1, 7))  # 1-6
    
    result = set()  # 使用set避免重复
    
    # 检查是否包含逗号或空格分隔的多个项目 (如: 1,3,5 或 1 3 5 或 1,3-5,6 或 1 3-5 6)
    if ',' in input_str or ' ' in input_str:
        # 使用预编译的正则表达式分割，提高性能
        items = SPLIT_PATTERN.split(input_str)
        for item in items:
            item = item.strip()
            if not item:
                continue
            
            # 检查是否是范围格式 (如: 3-5)
            if '-' in item:
                try:
                    start_str, end_str = item.split('-', 1)
                    start = int(start_str.strip())
                    end = int(end_str.strip())
                    
                    if start > end:
                        raise ValueError(f"范围起始值不能大于结束值: {start}-{end}")
                    
                    if start < 1 or end > 6:
                        raise ValueError(f"磁盘编号必须在 1-6 范围内，您输入的是: {start}-{end}")
                    
                    # 添加范围内的所有数字
                    result.update(range(start, end + 1))
                    
                except ValueError as e:
                    if "invalid literal" in str(e):
                        raise ValueError(f"范围格式错误 '{item}'，请使用 '开始-结束' 格式，如: 1-3")
                    raise
            else:
                # 单个数字
                try:
                    num = int(item)
                    if num < 1 or num > 6:
                        raise ValueError(f"磁盘编号必须在 1-6 范围内，您输入的是: {num}")
                    result.add(num)
                except ValueError as e:
                    if "invalid literal" in str(e):
                        raise ValueError(f"无效的数字: '{item}'")
                    raise
    
    # 检查是否是范围格式 (如: 1-3，没有逗号)
    elif '-' in input_str:
        try:
            start_str, end_str = input_str.split('-', 1)
            start = int(start_str.strip())
            end = int(end_str.strip())
            
            if start > end:
                raise ValueError(f"范围起始值不能大于结束值: {start}-{end}")
            
            if start < 1 or end > 6:
                raise ValueError(f"磁盘编号必须在 1-6 范围内，您输入的是: {start}-{end}")
            
            # 添加范围内的所有数字
            result.update(range(start, end + 1))
            
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"范围格式错误，请使用 '开始-结束' 格式，如: 1-3")
            raise
    
    # 尝试单个数字
    else:
        try:
            num = int(input_str)
            if num < 1 or num > 6:
                raise ValueError(f"磁盘编号必须在 1-6 范围内，您输入的是: {num}")
            result.add(num)
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"请输入有效的数字、范围(1-3)、多个数字(1,3,5)或字母a")
            raise
    
    return sorted(list(result))


def validate_disk_numbers(disk_numbers: List[int]) -> List[int]:
    """
    验证磁盘编号列表
    
    Args:
        disk_numbers: 磁盘编号列表
        
    Returns:
        List[int]: 验证通过的磁盘编号列表
        
    Raises:
        ValueError: 当磁盘编号超出有效范围时抛出
    """
    if not disk_numbers:
        raise ValueError("没有有效的磁盘编号")
    
    # 验证每个编号都在有效范围内
    for num in disk_numbers:
        if not isinstance(num, int) or num < 1 or num > 6:
            raise ValueError(f"磁盘编号必须在 1-6 范围内，错误编号: {num}")
    
    return disk_numbers


def validate_disk_input(disk_input: Union[int, str]) -> List[int]:
    """
    验证磁盘编号输入（支持单个数字或字符串格式）
    
    Args:
        disk_input: 磁盘编号输入（可以是整数或字符串）
        
    Returns:
        List[int]: 验证通过的磁盘编号列表
        
    Raises:
        ValueError: 当磁盘编号超出有效范围时抛出
    """
    if isinstance(disk_input, int):
        # 兼容原来的整数输入
        disk_numbers = [disk_input]
    elif isinstance(disk_input, str):
        # 解析新的字符串格式
        disk_numbers = parse_disk_input(disk_input)
    else:
        raise ValueError("磁盘编号必须是整数或字符串")
    
    return validate_disk_numbers(disk_numbers)


def interactive_input():
    """
    交互式输入模式（支持多种输入格式）
    
    支持的输入格式：
    - 单个数字：3
    - 数字范围：1-3, 3-6
    - 多个数字：1,3,5
    - 字母 a：表示全部(1-6)
    - 0：退出
    
    Returns:
        List[int]: 用户选择的有效磁盘编号列表
    """
    try:
        # 获取用户输入（更新提示信息）
        while True:
            try:
                user_input = input("请输入磁盘编号（单个数字3、范围1-3、多个数字1,3,5或1 3 5、字母a表示全部，0退出）：").strip()
                
                # 允许用户退出
                if user_input == '0':
                    return None
                
                # 解析用户输入
                disk_numbers = parse_disk_input(user_input)
                
                if not disk_numbers:
                    print("没有解析到有效的磁盘编号，请重新输入。")
                    continue
                
                return disk_numbers
                    
            except ValueError as e:
                print(f"输入错误: {e}")
                print("支持的格式：单个数字(3)、范围(1-3)、多个数字(1,3,5或1 3 5)、字母a(全部)，0退出")
            except KeyboardInterrupt:
                return None
            except Exception as e:
                print(f"解析输入时发生错误: {e}")
                
    except Exception as e:
        print(f"获取磁盘信息时发生错误: {e}")
        return None


def input_user(disk_number=None):
    """
    获取用户输入的硬盘编号（支持命令行参数或交互式输入）
    
    Args:
        disk_number (int/str, optional): 通过命令行传入的磁盘编号
        
    Returns:
        List[int]: 用户选择的有效磁盘编号列表
        
    Raises:
        ValueError: 当磁盘编号超出有效范围时抛出
    """
    if disk_number is not None:
        # 命令行参数模式
        return validate_disk_input(disk_number)
    else:
        # 交互式输入模式
        return interactive_input()


# # 模块级测试函数（可选）
# def test_parse_disk_input():
#     """测试parse_disk_input函数的测试函数"""
#     test_cases = [
#         ("3", [3]),
#         ("1-3", [1, 2, 3]),
#         ("1,3,5", [1, 3, 5]),
#         ("1 3 5", [1, 3, 5]),
#         ("1 2-4 6", [1, 2, 3, 4, 6]),
#         ("a", [1, 2, 3, 4, 5, 6]),
#     ]
    
#     print("测试 parse_disk_input 函数:")
#     for input_str, expected in test_cases:
#         try:
#             result = parse_disk_input(input_str)
#             status = "✓" if result == expected else "✗"
#             print(f"{status} '{input_str}' -> {result} (期望: {expected})")
#         except Exception as e:
#             print(f"✗ '{input_str}' -> 错误: {e}")


# if __name__ == "__main__":
#     # 如果直接运行此文件，进行模块测试
#     test_parse_disk_input()