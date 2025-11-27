#!/usr/bin/env python3
"""
测试 initialize_disk_to_partitioning_E 函数的脚本

使用方法:
    python test_initialize_e_partition.py --disk_number 3 --e_letter E
    
参数说明:
    --disk_number: 磁盘编号 (必需)
    --e_letter: E分区盘符 (必需)
"""

import argparse
import sys
import traceback
import os

# 将当前目录添加到Python路径，确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from partition_disk import initialize_disk_to_partitioning_E
except ImportError as e:
    print(f"错误: 无法导入 partition_disk 模块: {e}")
    print("请确保 partition_disk.py 文件存在于当前目录下")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='测试 initialize_disk_to_partitioning_E 函数',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python test_initialize_e_partition.py --disk_number 3 --e_letter E
    python test_initialize_e_partition.py --disk_number 3 --e_letter F
    python test_initialize_e_partition.py --disk_number 2 --e_letter G
        """
    )
    
    parser.add_argument('--disk_number', type=int, required=True,
                       help='磁盘编号 (必需参数)')
    parser.add_argument('--e_letter', type=str, required=True,
                       help='E分区盘符 (必需参数, 例如: E, F, G)')
    
    args = parser.parse_args()
    
    # 参数验证
    if len(args.e_letter) != 1:
        print("错误: E分区盘符必须是单个字母")
        sys.exit(1)
        
    if not args.e_letter.isalpha():
        print("错误: E分区盘符必须是字母")
        sys.exit(1)
    
    print(f"测试参数:")
    print(f"  磁盘编号: {args.disk_number}")
    print(f"  E分区盘符: {args.e_letter}")
    print("-" * 50)
    
    try:
        # 调用函数
        result = initialize_disk_to_partitioning_E(
            disk_number=args.disk_number,
            e_letter=args.e_letter
        )
        
        print("-" * 50)
        if result:
            print("✓ 测试成功: E分区初始化完成")
            sys.exit(0)
        else:
            print("✗ 测试失败: E分区初始化失败")
            sys.exit(1)
            
    except Exception as e:
        print("-" * 50)
        print(f"✗ 测试过程中发生异常:")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()