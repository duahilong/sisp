#!/usr/bin/env python3
"""
main.py - 磁盘信息主程序

直接运行disk_info来获取和显示硬盘信息，保持原有的输出格式和结构。
"""

from disk_info import get_disk_info, print_disk_info


def main():
    """主函数：获取并显示磁盘信息"""
    try:
        # 获取磁盘信息
        disk_data = get_disk_info()
        
        if disk_data:
            # 使用原有的print_disk_info函数显示表格格式
            print_disk_info(disk_data)
        else:
            print("未找到任何磁盘信息。")
            
    except Exception as e:
        print(f"获取磁盘信息时发生错误: {e}")
        print("请确保您有管理员权限运行此程序。")


if __name__ == "__main__":
    main()