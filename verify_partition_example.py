#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁盘分区创建与验证工具

支持命令行参数输入的磁盘分区创建和验证工具。
使用方法: python verify_partition_example.py --disk_number 3 --c_size 2000 --c_letter K

参数说明:
  --disk_number: 硬盘编号 (必填)
  --c_size: 分区大小(MB)，可选
  --c_letter: 分区盘符，可选

注意：验证功能使用 disk_info.py 模块，采用2秒等待时间。
"""

import argparse
import sys

# 导入主函数
from partition_disk import initialize_disk_to_partitioning_C


def main():
    """主函数：解析命令行参数并执行分区创建"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="磁盘分区创建与验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --disk_number 3 --c_size 2000 --c_letter K
  %(prog)s --disk_number 3 --c_size 2000
  %(prog)s --disk_number 3 --c_letter K
  %(prog)s --disk_number 3

注意：需要管理员权限运行
        """
    )
    
    # 添加命令行参数
    parser.add_argument("--disk_number", type=int, required=True,
                      help="硬盘编号 (必填)")
    parser.add_argument("--c_size", type=int, default=None,
                      help="分区大小(MB)，可选")
    parser.add_argument("--c_letter", type=str, default=None,
                      help="分区盘符，可选")
    
    # 解析参数
    args = parser.parse_args()
    
    print(f"开始为磁盘 {args.disk_number} 创建分区...")
    
    try:
        # 调用主函数创建并验证分区
        result = initialize_disk_to_partitioning_C(
            args.disk_number, 
            args.c_size, 
            args.c_letter
        )
        
        if result:
            print(f"✅ 磁盘{args.disk_number}分区创建成功")
            if args.c_letter and args.c_size:
                print(f"   分区盘符: {args.c_letter}")
                print(f"   分区大小: {args.c_size}MB")
            elif args.c_letter:
                print(f"   分区盘符: {args.c_letter}")
            elif args.c_size:
                print(f"   分区大小: {args.c_size}MB")
            sys.exit(0)  # 成功退出
        else:
            print(f"❌ 磁盘{args.disk_number}分区创建失败")
            sys.exit(1)  # 失败退出
            
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
        sys.exit(1)  # 异常退出


if __name__ == "__main__":
    main()