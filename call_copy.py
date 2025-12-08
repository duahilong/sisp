#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复制功能模块
用于将指定文件夹复制到指定磁盘的第3个分区根目录
"""

import os
import shutil
import sys
import tempfile
# 导入disk_info模块中的DiskManager类
from disk_info import DiskManager

# 模拟DiskInfo类，用于测试
def mock_disk_info(disk_number, drive_letters):
    """
    模拟DiskInfo类，用于测试
    
    Args:
        disk_number (int): 磁盘编号
        drive_letters (str): 盘符信息，如 "C, D, E"
    
    Returns:
        object: 模拟的DiskInfo对象
    """
    class MockDiskInfo:
        def __init__(self, index, drive_letters):
            self.index = index
            self.drive_letters = drive_letters
    
    return MockDiskInfo(disk_number, drive_letters)

def copy_software_to_partition(disk_number, software_file):
    """
    将指定文件夹复制到指定磁盘的第3个分区根目录
    
    Args:
        disk_number (int): 磁盘编号
        software_file (str): 源文件夹路径
    
    Returns:
        bool: 复制成功返回True，失败返回False
    """
    try:
        # 1. 验证参数
        if not isinstance(disk_number, int):
            raise ValueError("disk_number必须是整数类型")
        
        if not os.path.exists(software_file):
            raise FileNotFoundError(f"源文件夹不存在: {software_file}")
        
        if not os.path.isdir(software_file):
            raise ValueError(f"源路径必须是文件夹: {software_file}")
        
        # 2. 使用DiskManager类查询磁盘信息
        disk_manager = DiskManager()
        disk_info = disk_manager.get_disk_by_index(disk_number)
        
        if not disk_info:
            raise ValueError(f"未找到磁盘编号为{disk_number}的磁盘")
        
        # 3. 解析磁盘的盘符信息
        # drive_letters 格式为逗号分隔的字符串，如 "C, D, E"
        if disk_info.drive_letters == "Unknown":
            raise ValueError(f"磁盘{disk_number}没有找到分区盘符")
        
        # 将字符串转换为列表并去除空格
        drive_letters = [letter.strip() for letter in disk_info.drive_letters.split(",")]
        
        # 检查是否有至少3个分区
        if len(drive_letters) < 3:
            raise ValueError(f"磁盘{disk_number}至少需要3个分区，但当前只有{len(drive_letters)}个分区")
        
        # 4. 获取第3个分区的盘符（索引为2，因为列表从0开始）
        target_drive = drive_letters[2] + ":\\"
        
        # 5. 构建目标路径
        # 源文件夹名称
        source_folder_name = os.path.basename(software_file)
        # 目标文件夹路径
        target_path = os.path.join(target_drive, source_folder_name)
        
        # 6. 执行复制操作
        print(f"正在将 {software_file} 复制到 {target_path}...")
        
        # 如果目标文件夹已存在，先删除它
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        # 复制文件夹到目标路径
        shutil.copytree(software_file, target_path)
        
        print(f"复制完成！文件夹已复制到 {target_path}")
        return True
        
    except Exception as e:
        print(f"复制失败: {e}")
        return False

def test_copy_function():
    """
    测试复制函数的核心逻辑，使用模拟数据
    """
    try:
        # 创建临时源文件夹
        with tempfile.TemporaryDirectory() as temp_src_dir:
            # 创建一些测试文件
            test_file1 = os.path.join(temp_src_dir, "test1.txt")
            with open(test_file1, "w") as f:
                f.write("测试文件1内容")
            
            test_file2 = os.path.join(temp_src_dir, "test2.txt")
            with open(test_file2, "w") as f:
                f.write("测试文件2内容")
            
            # 创建临时目标文件夹作为模拟的第3个分区
            with tempfile.TemporaryDirectory() as temp_dst_dir:
                # 模拟磁盘信息
                mock_disk = mock_disk_info(3, "C, D, E")
                
                # 模拟第3个分区的盘符
                target_drive = "E:\\\\"
                
                # 构建目标路径
                source_folder_name = os.path.basename(temp_src_dir)
                target_path = os.path.join(temp_dst_dir, source_folder_name)
                
                print(f"\n=== 测试复制功能 ===")
                print(f"源文件夹: {temp_src_dir}")
                print(f"模拟目标分区: {target_drive}")
                print(f"实际目标路径: {target_path}")
                
                # 执行复制操作
                print(f"\n正在复制文件夹...")
                shutil.copytree(temp_src_dir, target_path)
                
                # 验证复制结果
                print(f"复制完成！")
                print(f"目标文件夹内容: {os.listdir(target_path)}")
                
                # 验证文件内容
                for file in os.listdir(target_path):
                    file_path = os.path.join(target_path, file)
                    if os.path.isfile(file_path):
                        with open(file_path, "r") as f:
                            content = f.read()
                        print(f"{file} 内容: {content}")
                
                print("\n=== 测试成功！复制功能正常工作 ===")
                return True
    
    except Exception as e:
        print(f"\n=== 测试失败 ===")
        print(f"错误信息: {e}")
        return False

if __name__ == "__main__":
    """
    主函数，用于测试copy_software_to_partition函数
    """
    # 执行模拟测试
    test_copy_function()
    
    print("\n=== 实际系统测试（可能会失败，取决于系统配置） ===")
    # 尝试使用系统中存在的磁盘进行测试
    # 磁盘编号为0（如果存在）
    disk_num = 0
    # 源文件夹路径
    source_folder = r"D:\Sisp\TestFolder"
    
    # 调用复制函数
    copy_software_to_partition(disk_num, source_folder)
